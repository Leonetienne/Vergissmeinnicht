# Vergissmeinnicht: Agent Reference

Vergissmeinnicht is a small, self-hosted to-do app. Users keep tasks on boards,
optionally split into Kanban-like lists, and share boards with other users as
observer (read-only) or editor (read and write). The UI is English.

**Simplicity first.** This is a deliberately small project. Keep the codebase as
small, flat and readable as possible: few apps, few files, few dependencies, no
abstraction without a second caller. When a convention borrowed from Comaney adds
weight without need here, this rule wins.

## Rules
- Never use em-dash or en-dash; use ':', ';', ',' or rewrite
- Requirements are mandatory: see "Requirements (spec/)" below
- New functional features or fixes: must add tests
- Code so a human can maintain it; best practices, DRY, clear architecture
- Never load anything from the internet after deployment, except SMTP for reminder emails
- All assets (fonts, images, scripts, libraries, emoji data) are served locally: a package installed with yarn and bundled via esbuild, or a plain file under `static/`; never a CDN reference
- Code comments follow `../AGENTS.md` (Code-Kommentare)

## Requirements (spec/)
`spec/` is the requirements database (Lastenheft) for the whole system. Format: `spec/README.md` (ISO/IEC/IEEE 29148 structure, EARS sentences, OpenFastTrack item IDs).
- Every change that adds, changes, or removes observable behaviour updates the affected requirements in `spec/requirements/` in the same change.
- New feature area: add a `feat~...~1` item to `spec/features.md` (with `Needs: req`) plus its requirements file.
- Changed meaning of a requirement: bump its revision (`~1` -> `~2`). Removed behaviour: delete the item. Never reuse an ID.
- Every `req` item covers exactly one `feat` item via `Covers:`.

## Stack
- Python 3.12, Django, Gunicorn, WhiteNoise, mysqlclient, MariaDB
- SCSS: `build/scss/` -> `static/dist/main.css`
- JS: `build/js/` -> `static/dist/` via esbuild; Alpine.js v3 for components, SortableJS for drag and drop
- Build assets: `build/build-assets.sh` (Docker container, never run npm/yarn directly on host)
- CSS theming: CSS custom properties (`--var`) only, never SCSS `$vars` for themeable values (breaks dark mode)
- Accent: `#B7C4DE` in dark mode, a darker shade of it in light mode (`--accent`)
- Dev stack: `docker-compose up -d` (web at http://localhost:8080, MariaDB, Mailpit at http://localhost:8030)

## App layout (target)
```
vergissmeinnicht/  settings, root urls, wsgi
accounts/          User model (email login), login, registration, TOTP, settings page, API/MCP keys
boards/            Board, Share, List, Task models
  services.py      every business rule (permissions, state transitions, sorting, moves)
  serializers.py   the one JSON shape per entity (API, MCP, JSON export, undo)
api/               registry.py (operations), operations/ (handlers per concern), rest.py, mcp.py
templates/partials/ _confirm_dialog.html, _emoji_picker.html, _inline_edit.html, _search.html
build/             scss/, js/, build-assets.sh
tests/             unit/, api/, e2e/
```

## Key conventions
- **One operation layer**: every action is an `Operation` in `api/registry.py` with a handler in `api/operations/`. REST (`/api/v1/`), MCP (`/mcp`) and the frontend's JavaScript all go through it. Handlers validate and call `boards/services.py`; they hold no rules themselves. Pages are server-rendered from the same serializers.
- **Ownership**: a board and every list and task in it belong to the board's owner, whoever created them. Roles: owner, editor, observer. Check access only through the service helpers, never inline in a view.
- **Task states**: `open <-> done <-> archived`, one step at a time, only through the single transition function in `boards/services.py`.
- **Default list**: every board has exactly one, created with the board, untitled, undeletable, leftmost.
- **Undo/redo**: a per-page in-browser stack (`build/js/undo.js`). Each undoable action registers its inverse as ordinary operation calls; no server-side history.
- **Inline edit**: one shared partial and JS helper: text until clicked, then an input; Enter or blur saves, Esc reverts.
- **OK/Cancel**: one shared confirm dialog (`window.confirmDialog`), never the browser's native `confirm()`.

## Tests
- Always run with `-v` and pipe through `tee logfile.log`; never `-x`
- Unit (no Docker): `venv/bin/pytest tests/unit/ -v | tee logfile.log`
- API and MCP: `pytest tests/api/ -v | tee logfile.log`
- E2E (Selenium + live stack at :8080, Mailpit at :8030): `pytest tests/e2e/ -v | tee logfile.log`
- E2E: `time.sleep()` then assert, never `WebDriverWait`; verify through the UI when the test is about what the user sees

## Management commands
- `create_user <email> [-p pw] [--name X]`
- `set_user_password <email> [-p pw]`
- `delete_user <email> [--yes]`
- `remove_user_2fa <email>`
- `send_due_reminders` (daily via cron; no-op without email configuration)

## Key env vars
| Var | Purpose |
|-----|---------|
| `DJANGO_SECRET_KEY` | required in prod |
| `DEBUG` | `TRUE` for dev |
| `ALLOWED_HOSTS` | comma-separated |
| `DB_HOST/PORT/NAME/USER/PASSWORD` | MariaDB |
| `ENABLE_REGISTRATION` | `TRUE` to allow signups (default `FALSE`) |
| `EMAIL_HOST/PORT/USE_TLS/HOST_USER/HOST_PASSWORD` | SMTP; reminders are off without `EMAIL_HOST` |
| `DEFAULT_FROM_EMAIL` | sender address |
| `SITE_URL` | used in email links |
| `APP_VERSION` | shown in footer |
| `GUNICORN_WORKERS` | default 1 |

## Transport / TLS
Always deployed behind a TLS-terminating reverse proxy. The app speaks plain HTTP, never redirects to HTTPS, never emits HSTS. Do not add `SECURE_SSL_REDIRECT`, `SECURE_HSTS_*` or `SECURE_PROXY_SSL_HEADER`. With `DEBUG` off, session and CSRF cookies are `Secure`.

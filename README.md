# Vergissmeinnicht

A small, self-hosted to-do app. Tasks live on boards, optionally split into Kanban-like
lists, and boards can be shared with other users as observer or editor. Everything the UI
does is also available through a REST API (`/api/v1/`) and an MCP server (`/mcp`).

Requirements: [`spec/`](spec/). Design system: [`docs/design-system/`](docs/design-system/).

## Development

```bash
build/build-assets.sh          # SCSS and JS into static/dist, inside a Node container
docker-compose up -d           # web on :8080, MariaDB, Mailpit on :8030
docker-compose exec web python manage.py create_user you@example.org --name You
```

The dev stack mounts the source and runs Django's dev server; registration is enabled and
email goes to Mailpit.

## Tests

```bash
venv/bin/pytest tests/unit/ -v | tee logfile.log                          # no Docker
docker-compose exec web pytest tests/api/ -v | tee logfile.log            # REST, MCP, pages on MariaDB
venv/bin/pytest tests/e2e/ -v | tee logfile.log                           # Selenium against the dev stack
```

`tests/api/` also runs locally on SQLite when `DB_HOST` is unset. E2E tests need Chrome and
a running dev stack.

## Deployment

Build the image (assets are compiled inside it) and run it behind a TLS-terminating reverse
proxy. The container applies migrations on start, then starts Gunicorn on port 8000.

```bash
docker build --build-arg APP_VERSION=1.0.0 -t vergissmeinnicht .
```

Mount a volume at `/app/data` for uploaded backdrops.

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | required unless `DEBUG` |
| `DEBUG` | `TRUE` for development |
| `ALLOWED_HOSTS` | comma-separated, required unless `DEBUG` |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MariaDB |
| `ENABLE_REGISTRATION` | `TRUE` allows self-registration (default off) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP; reminders are off without `EMAIL_HOST` |
| `DEFAULT_FROM_EMAIL` | sender address |
| `SITE_URL` | public URL, used in email links and as trusted CSRF origin |
| `APP_VERSION` | shown in the footer |
| `GUNICORN_WORKERS` | default 1 |

### Cron

`send_due_reminders` is the only command to run by cron, once a day:

```cron
0 7 * * * docker exec vergissmeinnicht python manage.py send_due_reminders
```

### Management commands

| Command | Effect |
|---|---|
| `create_user <email> [-p pw] [--name X]` | create an account, regardless of `ENABLE_REGISTRATION` |
| `set_user_password <email> [-p pw]` | set a new password |
| `delete_user <email> [--yes]` | delete the account and every board it owns |
| `remove_user_2fa <email>` | remove the second factor |
| `send_due_reminders` | send due date reminder emails |

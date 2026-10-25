# Vergissmeinnicht

A small, self-hosted to-do app. Tasks live on boards, optionally split into Kanban-like
lists, and boards can be shared with other users as observer (read-only) or editor.

![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/theme-turquoise-dark.png)

*Colour themes and light or dark mode, switchable in the header.*

| Turquoise, light | OLED, dark |
|---|---|
| ![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/theme-turquoise-light.png) | ![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/theme-oled-dark.png) |
| **Bubblegum, light** | **Bubblegum, dark** |
| ![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/theme-bubblegum-light.png) | ![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/theme-bubblegum-dark.png) |

*Board overview.*

![image](https://raw.githubusercontent.com/Leonetienne/vergissmeinnicht/refs/heads/master/github-assets/home-bubblegum-light.png)

## Features

- Boards with emoji icons, Kanban-like lists and drag and drop for boards, lists and tasks
- Tasks with notes and due dates; `open`, `done` and `archived` states with an archive page
- Sharing boards with other users as observer or editor
- Page-wide search, keyboard undo and redo
- Optional email reminders before and on a task's due date
- JSON export of a board, a list or a task
- Login with email, optional TOTP second factor with recovery codes
- Light and dark mode, custom backdrop image and backdrop CSS
- REST API (`/api/v1/`) and MCP server (`/mcp`) with per-user keys from the settings page
- Fully offline after deployment: every asset is served locally, the only outbound
  connection is SMTP for reminders

## Running it

Vergissmeinnicht ships as one Docker image and needs a MariaDB database. It speaks plain
HTTP on port 8000 and belongs behind a TLS-terminating reverse proxy. On start the container
applies database migrations, then starts Gunicorn.

```yaml
services:
  web:
    image: leonetienne/vergissmeinnicht:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      DJANGO_SECRET_KEY: change-me
      ALLOWED_HOSTS: todo.example.org
      SITE_URL: https://todo.example.org
      DB_HOST: db
      DB_NAME: vergissmeinnicht
      DB_USER: vergissmeinnicht
      DB_PASSWORD: change-me
      EMAIL_HOST: smtp.example.org
      EMAIL_PORT: "587"
      EMAIL_USE_TLS: "TRUE"
      EMAIL_HOST_USER: todo@example.org
      EMAIL_HOST_PASSWORD: change-me
      DEFAULT_FROM_EMAIL: todo@example.org
    volumes:
      - data:/app/data
    depends_on:
      - db

  db:
    image: mariadb:11.4
    restart: unless-stopped
    environment:
      MARIADB_DATABASE: vergissmeinnicht
      MARIADB_USER: vergissmeinnicht
      MARIADB_PASSWORD: change-me
      MARIADB_RANDOM_ROOT_PASSWORD: "1"
    volumes:
      - db:/var/lib/mysql

volumes:
  data:
  db:
```

`/app/data` holds uploaded backdrops; keep it on a volume.

Registration is off by default, so create the first account by hand:

```bash
docker compose exec web python manage.py create_user you@example.org --name You
```

### Configuration

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | required unless `DEBUG` |
| `ALLOWED_HOSTS` | comma-separated, required unless `DEBUG` |
| `SITE_URL` | public URL, used in email links and as trusted CSRF origin |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MariaDB |
| `ENABLE_REGISTRATION` | `TRUE` allows self-registration (default off) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP; reminders are off without `EMAIL_HOST` |
| `DEFAULT_FROM_EMAIL` | sender address |
| `GUNICORN_WORKERS` | default 1 |
| `DEBUG` | `TRUE` for development only |

### Reminders

`send_due_reminders` sends due date reminder emails. Run it once a day by cron:

```cron
0 7 * * * docker exec vergissmeinnicht python manage.py send_due_reminders
```

### Management commands

Run inside the container with `python manage.py <command>`.

| Command | Effect |
|---|---|
| `create_user <email> [-p pw] [--name X]` | create an account, regardless of `ENABLE_REGISTRATION` |
| `set_user_password <email> [-p pw]` | set a new password |
| `delete_user <email> [--yes]` | delete the account and every board it owns |
| `remove_user_2fa <email>` | remove the second factor |
| `send_due_reminders` | send due date reminder emails |

## Building the image

Assets are compiled inside the image. `APP_VERSION` is shown in the footer.

```bash
docker buildx build \
    --platform linux/amd64 \
    -f Dockerfile \
    -t leonetienne/vergissmeinnicht:1.0.0 \
    -t leonetienne/vergissmeinnicht:latest \
    --build-arg APP_VERSION=1.0.0 \
    --push .
```

## Development

```bash
build/build-assets.sh          # SCSS and JS into static/dist, inside a Node container
docker-compose up -d           # web on :8080, MariaDB, Mailpit on :8030
docker-compose exec web python manage.py create_user you@example.org --name You
```

The dev stack mounts the source and runs Django's dev server; registration is enabled and
email goes to Mailpit.

```bash
venv/bin/pytest tests/unit/ -v | tee logfile.log                          # no Docker
docker-compose exec web pytest tests/api/ -v | tee logfile.log            # REST, MCP, pages on MariaDB
venv/bin/pytest tests/e2e/ -v | tee logfile.log                           # Selenium against the dev stack
```

`tests/api/` also runs locally on SQLite when `DB_HOST` is unset. E2E tests need Chrome and
a running dev stack.

Requirements: [`spec/`](spec/). Design system: [`docs/design-system/`](docs/design-system/).

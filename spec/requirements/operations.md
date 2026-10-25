# Operations and Deployment

### Self-hosted
`req~operations.selfhosted~1`

The system shall run entirely on infrastructure of the operator, with no external service except an optional SMTP server.

Covers:
- `feat~operations~1`

Tags: Operations, Privacy

### Docker image
`req~operations.image~1`

The system shall be built into one Docker image that is published to a container image registry and contains the application with all compiled assets.

Covers:
- `feat~operations~1`

Tags: Operations

### Startup
`req~operations.startup~1`

When the container starts, it shall apply pending database migrations and then start Gunicorn.

Covers:
- `feat~operations~1`

Tags: Operations

### Local development
`req~operations.dev-stack~1`

`docker-compose up -d` shall start a local development stack with the web app on `http://localhost:8080`, MariaDB and Mailpit (UI on `http://localhost:8030`), with email configured to Mailpit.

Covers:
- `feat~operations~1`

Tags: Operations

### Configuration by environment
`req~operations.env~1`

The system shall read all instance configuration from environment variables: `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `ENABLE_REGISTRATION`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SITE_URL`, `APP_VERSION`, `GUNICORN_WORKERS`.

Covers:
- `feat~operations~1`

Tags: Operations

### Misconfiguration
`req~operations.misconfig~1`

If `DEBUG` is off and `DJANGO_SECRET_KEY` or `ALLOWED_HOSTS` is missing, then the system shall refuse to start with a message naming the variable.

Covers:
- `feat~operations~1`

Tags: Operations, Security

### Media volume
`req~operations.media~1`

The system shall store uploaded backdrops under `/app/data/media` and serve them only through an authenticated view.

Covers:
- `feat~operations~1`

Tags: Operations, Privacy

### Cron
`req~operations.cron~1`

The documentation shall name `send_due_reminders` as the only command to run by cron, once a day.

Covers:
- `feat~operations~1`

Tags: Operations

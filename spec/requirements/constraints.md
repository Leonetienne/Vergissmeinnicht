# Design Constraints

Sources: AGENTS.md.

### Technology stack
`req~constraints.stack~1`

The system shall be built with Python 3.12, Django, Gunicorn, WhiteNoise and MariaDB, with SCSS and JavaScript (Alpine.js, SortableJS) bundled by esbuild through `build/build-assets.sh` in a container, never with npm or yarn on the host.

Covers:
- `feat~constraints~1`

### SCSS with custom properties
`req~constraints.css-vars~1`

Styles shall be written in SCSS; themeable values shall use CSS custom properties only, never SCSS variables.

Rationale:
SCSS variables are fixed at build time and break dark mode.

Covers:
- `feat~constraints~1`

### User model
`req~constraints.user-model~1`

Accounts shall use one custom Django user model with the email address as login field, defined in the first migration.

Covers:
- `feat~constraints~1`

### Modular apps
`req~constraints.apps~1`

The code shall be split into the Django apps `accounts`, `boards` and `api`, with dependencies pointing from `api` to `boards` and `accounts`, never back.

Covers:
- `feat~constraints~1`

### Rules in services
`req~constraints.services~1`

Business rules (permissions, state transitions, sort positions, moves) shall live in service functions of the `boards` app; views and operation handlers shall only validate input and call them.

Covers:
- `feat~constraints~1`

### Single state transition path
`req~constraints.transitions~1`

Code shall change a task's state only through the one transition function that enforces the allowed transitions.

Covers:
- `feat~constraints~1`

### One serializer per entity
`req~constraints.serializers~1`

Each of board, list and task shall have exactly one serializer, used by the REST API, the MCP server, the JSON export and the undo stack.

Covers:
- `feat~constraints~1`

### Frontend through operations
`req~constraints.frontend-api~1`

The frontend's JavaScript shall change data only by calling REST API operations with the session.

Covers:
- `feat~constraints~1`

### Reusable partials
`req~constraints.partials~1`

The confirm dialog, inline edit, emoji control and search popup shall each exist once as a template partial with its script, reused wherever needed.

Covers:
- `feat~constraints~1`

### Test conventions
`req~constraints.test-conventions~1`

Tests shall run with `-v` only (never `-x`); end-to-end tests shall wait with `time.sleep()` rather than `WebDriverWait`.

Covers:
- `feat~constraints~1`

### Comment style
`req~constraints.comments~1`

Code comments shall be the exception, describe the current state and the reason, avoid history, filler words and dashes as sentence separators, and stay within one or two lines.

Covers:
- `feat~constraints~1`

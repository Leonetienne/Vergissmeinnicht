# Quality Requirements

## Security

### Server-side authorisation
`req~quality.security.authz~1`

The system shall check board membership and role on the server for every read and write, independent of what the UI shows.

Covers:
- `feat~quality~1`

Tags: Security

### CSRF
`req~quality.security.csrf~1`

The system shall require a valid CSRF token for every state-changing browser request.

Covers:
- `feat~quality~1`

Tags: Security

### Secret storage
`req~quality.security.secrets~1`

The system shall store passwords as salted hashes, API keys, MCP keys and recovery codes as hashes, and generate all keys and codes with a cryptographically secure generator.

Covers:
- `feat~quality~1`

Tags: Security

### Uploaded images
`req~quality.security.images~1`

The system shall verify and re-encode every uploaded image before storing it.

Covers:
- `feat~quality~1`

Tags: Security

### Escaped embedded data
`req~quality.security.json-embed~1`

The system shall escape `<`, `>` and `&` in all JSON embedded in HTML script blocks.

Rationale:
Names and titles written by other members must not break out of a script element.

Covers:
- `feat~quality~1`

Tags: Security

### Robust parameters
`req~quality.security.params~1`

If a request carries a malformed or out-of-range parameter, then the system shall answer with a client error, never a server error.

Covers:
- `feat~quality~1`

Tags: Security

## Transport

### No in-app HTTPS enforcement
`req~quality.transport.no-redirect~1`

The system shall speak plain HTTP behind a TLS-terminating proxy and shall not redirect to HTTPS, emit HSTS or inspect `X-Forwarded-Proto`.

Rationale:
App-side redirects behind a TLS-terminating proxy cause redirect loops.

Covers:
- `feat~quality~1`

Tags: Security, Operations

### Secure cookies
`req~quality.transport.cookies~1`

While `DEBUG` is off, the system shall mark session and CSRF cookies `Secure`.

Covers:
- `feat~quality~1`

Tags: Security

## Self-containment

### No runtime downloads
`req~quality.selfcontained.assets~1`

The system shall serve all fonts, images, scripts, libraries and emoji data locally and load nothing from the internet at runtime.

Covers:
- `feat~quality~1`

Tags: Privacy

### Static asset caching
`req~quality.selfcontained.static~1`

The system shall serve static files with content-hashed names, compressed, for long-term browser caching.

Covers:
- `feat~quality~1`

Tags: Performance

## Reliability and performance

### Atomic changes
`req~quality.reliability.atomic~1`

Multi-step changes (bulk transitions, bulk moves, list deletion, board deletion, account deletion, reordering) shall be atomic: either all of their effects persist or none.

Covers:
- `feat~quality~1`

### Consistent order
`req~quality.reliability.order~1`

After any create, move, reorder or delete, the sort positions of the affected lists, tasks and boards shall be unique and gapless within their container.

Covers:
- `feat~quality~1`

### Small instances
`req~quality.performance.scale~1`

The system shall be dimensioned for small self-hosted instances; a single Gunicorn worker shall be sufficient for a household.

Covers:
- `feat~quality~1`

Tags: Performance

### Board page queries
`req~quality.performance.queries~1`

The board page shall load with a constant number of database queries, independent of the number of lists and tasks.

Covers:
- `feat~quality~1`

Tags: Performance

## Tests

### End-to-end coverage
`req~quality.tests.e2e~1`

Every feature in this database shall be covered by Selenium end-to-end tests run with pytest against the local development stack, verifying user-visible behaviour through the UI, including reminder emails through Mailpit.

Covers:
- `feat~quality~1`

### API and MCP coverage
`req~quality.tests.api~1`

Every operation shall be tested through both the REST API and the MCP server, including success, validation errors, missing authentication and each role that must be refused.

Covers:
- `feat~quality~1`

### Unit coverage
`req~quality.tests.unit~1`

Pure logic (state transitions, due date warnings and reminder stages, sort position handling, slugs, CSS sanitising, serializers) shall be covered by unit tests that run without the Docker stack.

Covers:
- `feat~quality~1`

### Tests for changes
`req~quality.tests.changes~1`

Every new feature and every fix shall come with automated tests.

Covers:
- `feat~quality~1`

### Full run
`req~quality.tests.no-skips~1`

A full test run in the development environment shall skip no test.

Covers:
- `feat~quality~1`

## Maintainability

### Small codebase
`req~quality.maint.small~1`

The codebase shall stay as small and plain as the requirements allow: few apps, few dependencies, no abstraction without at least two users.

Covers:
- `feat~quality~1`

### Specification in sync
`req~quality.maint.spec~1`

A behaviour change shall update `AGENTS.md` and this requirements database in the same change.

Covers:
- `feat~quality~1`

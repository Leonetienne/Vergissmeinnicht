# REST API

## Operation layer

### Central operation layer
`req~api.registry~1`

The system shall define every action on boards, shares, lists, tasks, search and the user profile once as an operation with name, parameters, access level (read or write) and handler; the frontend, the REST API and the MCP server shall all use these operations.

Covers:
- `feat~api~1`

### Same rules everywhere
`req~api.same-rules~1`

An operation shall apply the same validation, permissions and state rules no matter whether it is called from the frontend, the REST API or the MCP server.

Covers:
- `feat~api~1`

Tags: Security

## REST interface

### Base path
`req~api.base~1`

The system shall serve the REST API as JSON under `/api/v1/`, with one route per operation.

Covers:
- `feat~api~1`

### Authentication
`req~api.auth~1`

The REST API shall accept either a Bearer API key or the browser session with a valid CSRF token for writes; if neither is present or valid, then it shall answer 401.

Covers:
- `feat~api~1`

Tags: Security

### Coverage
`req~api.coverage~1`

The REST API shall offer every board, share, list, task, archive, search and export action of the UI, plus reading and changing display name, email address and reminder setting.

Covers:
- `feat~api~1`

### Excluded actions
`req~api.excluded~1`

The REST API shall offer no operation to create or delete accounts, change passwords, manage the second factor or API and MCP keys, or upload a backdrop.

Rationale:
A leaked key must not be able to take over or delete the account.

Covers:
- `feat~api~1`

Tags: Security

### Bulk operations
`req~api.bulk~1`

The REST API shall offer bulk operations to transition a list of tasks between neighbouring states and to move a list of tasks to a list and positions, each applied atomically.

Rationale:
Needed for "Unarchive selected", undoing "Archive what's done" and undoing a list deletion.

Covers:
- `feat~api~1`

### Representations
`req~api.serializer~1`

The REST API shall return boards, lists and tasks in the single serialized representation of each entity.

Covers:
- `feat~api~1`

### Errors
`req~api.errors~1`

If an operation fails, then the REST API shall answer with status 400, 401, 403, 404 or 409 and a JSON body `{"error": "<message>"}`, never a server error for invalid input.

Covers:
- `feat~api~1`

### Self-description
`req~api.index~1`

`GET /api/v1/` shall list all operations with method, path, description and parameters.

Covers:
- `feat~api~1`

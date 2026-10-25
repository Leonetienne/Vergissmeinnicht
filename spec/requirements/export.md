# JSON Export

### Board export
`req~export.board~2`

At the bottom left of every board page, the system shall show a "Json export" link that downloads the board with all lists and tasks of every state as a JSON file.

Covers:
- `feat~export~1`

### List export
`req~export.list~1`

The "Json export" link of a list shall download the list with all its tasks of every state as a JSON file.

Covers:
- `feat~export~1`

### Task export
`req~export.task~1`

The "Json export" link in the task singleview shall download the task as a JSON file.

Covers:
- `feat~export~1`

### Same serializer
`req~export.serializer~1`

Every JSON export shall be produced by the same serializer as the REST API and MCP representation of that entity.

Covers:
- `feat~export~1`

### Export for all members
`req~export.members~1`

The system shall offer every export to all members, observers included.

Covers:
- `feat~export~1`

### Export link style
`req~export.style~1`

"Json export" links shall be small, text only, underlined and without frame.

Covers:
- `feat~export~1`

Tags: UI

### File name
`req~export.filename~2`

The downloaded file shall be named after the slug of the exported board or task, and for a list after the board slug and the list slug joined by a hyphen, with the extension `.json`.

Covers:
- `feat~export~1`

# Search

### Open search
`req~search.open~1`

When a logged-in user presses Ctrl+F or Cmd+F on any page, the system shall open the search popup with the focus in its input, in place of the browser's own page search.

Covers:
- `feat~search~1`

Tags: UI

### Scope
`req~search.scope~1`

The search shall cover all boards the user is a member of: boards by name, tasks by title or note, tasks of every state.

Covers:
- `feat~search~1`

Tags: Security

### Matching
`req~search.match~1`

While the input holds at least 2 characters, the system shall show as-you-type results matching the text as case-insensitive substring, boards first, at most 50 results.

Covers:
- `feat~search~1`

### Result display
`req~search.result~1`

A board result shall show emoji and name; a task result shall show title, board emoji and name, and a marker for done or archived tasks.

Covers:
- `feat~search~1`

Tags: UI

### Result navigation
`req~search.navigate~1`

When the user picks a result by click or by arrow keys and Enter, the system shall open the board page for a board, the board page with anchor `#task-<id>` for an open or done task, and the archive page with that anchor for an archived task.

Covers:
- `feat~search~1`

### Close search
`req~search.close~1`

When the user presses Esc or clicks outside the popup, the system shall close it.

Covers:
- `feat~search~1`

Tags: UI

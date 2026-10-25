# System Features

Each feature groups the requirements in one file under [requirements/](requirements/).

### Accounts and authentication
`feat~accounts~1`

Registration, login, logout, login redirect, password and email change, account
deletion and the account management commands.

Needs: req

### Second-factor authentication
`feat~twofa~1`

TOTP setup, login challenge, recovery codes and removal.

Needs: req

### User settings
`feat~settings~1`

The settings page: profile, password, notifications, second factor, API and MCP
keys, appearance (backdrop, backdrop CSS, opacities) and account deletion.

Needs: req

### Boards
`feat~boards~1`

The board list on the start page, creating, renaming, reordering and deleting
boards, emoji icons and the board page.

Needs: req

### Board sharing
`feat~sharing~1`

Sharing a board with other users as observer or editor, roles and permissions.

Needs: req

### Lists
`feat~lists~1`

The default list, creating, renaming, reordering and deleting lists.

Needs: req

### Tasks
`feat~tasks~1`

Creating, editing, checking, moving and deleting tasks, the task card and the
task singleview.

Needs: req

### Archive
`feat~archive~1`

Archiving done tasks and restoring them from the archive page.

Needs: req

### Search
`feat~search~1`

The page-wide search popup for boards and tasks.

Needs: req

### Undo and redo
`feat~undo~1`

Keyboard undo and redo of the user's own actions on the current page.

Needs: req

### JSON export
`feat~export~1`

Exporting a board, a list or a task as JSON.

Needs: req

### Due date reminders
`feat~reminders~1`

Optional reminder emails before and on a task's due date.

Needs: req

### REST API
`feat~api~1`

The central operation layer and its REST interface.

Needs: req

### MCP server
`feat~mcp~1`

The MCP interface on top of the central operation layer.

Needs: req

### User interface framework
`feat~ui~1`

Layout, theming, footer, confirm dialog, inline edit, emoji picker, toasts and
responsive behaviour shared by all pages.

Needs: req

### Operations and deployment
`feat~operations~1`

Docker image, local development stack, configuration through environment
variables, cron and management commands.

Needs: req

### Quality
`feat~quality~1`

Security, privacy, reliability, performance and test coverage.

Needs: req

### Design constraints
`feat~constraints~1`

Rules for maintainers about stack, architecture and conventions.

Needs: req

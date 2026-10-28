# Boards

## Board list

### Start page
`req~boards.list.start~1`

The system shall show the board list on the start page `/`.

Covers:
- `feat~boards~1`

### Own and shared sections
`req~boards.list.sections~1`

The board list shall show the user's own boards first, then a section "Shared with me" with the boards shared with them, each labelled with the owner's display name and the user's role, sorted alphabetically; the section shall be hidden while empty.

Covers:
- `feat~boards~1`

Tags: UI

### Board list entry
`req~boards.list.entry~3`

Each board list entry shall be one card that opens the board page when clicked anywhere, except on the emoji field, which opens the emoji picker for the owner, and the board title, which starts inline editing for the owner.

Covers:
- `feat~boards~1`

Tags: UI

### Reorder own boards
`req~boards.list.reorder~1`

When a user drags one of their own boards to another position in the board list, the system shall store the new order.

Covers:
- `feat~boards~1`

## Creating, renaming, deleting

### Inline creation
`req~boards.create~2`

When a user types a title into the input at the end of their own boards and presses Enter, including the Enter key of an on-screen keyboard, the system shall create the board with an empty default list, show it in the list with an empty emoji placeholder, and clear the input for the next title.

Covers:
- `feat~boards~1`

### Starter boards
`req~boards.starter~1`

When an account is created, the system shall create the boards "My Todos" with emoji 🧹 and "Shopping List" with emoji 🛒 for it.

Rationale:
Shows new users what boards are for.

Covers:
- `feat~boards~1`

### Board title
`req~boards.name~1`

The system shall require a board title of 1 to 100 characters.

Covers:
- `feat~boards~1`

### Unique board title
`req~boards.name-unique~1`

If a request creates or renames a board with a title that another board of the same owner already has, ignoring case, then the system shall reject it and the page shall show a toast naming the taken title; boards of other owners, including boards shared with the user, shall not count.

Covers:
- `feat~boards~1`

### Inline rename
`req~boards.rename~1`

When the owner edits a board title inline, in the board list or in the board page title, the system shall store the new title.

Covers:
- `feat~boards~1`

### Delete board
`req~boards.delete~1`

When the owner confirms deletion of a board in the confirm dialog, the system shall delete the board with all lists, tasks and shares.

Covers:
- `feat~boards~1`

### Owner-only board actions
`req~boards.owner-only~2`

The system shall allow renaming, changing the emoji or description, sharing and deleting a board only to its owner and shall not show these controls to anyone else.

Covers:
- `feat~boards~1`

Tags: Security

## Description

### Board description
`req~boards.description~1`

The system shall store an optional board description of up to 1000 characters and show it as a paragraph between the board page title and the list tools; while the description is empty, the system shall hide it from everyone but the owner.

Covers:
- `feat~boards~1`

### Edit description
`req~boards.description.edit~1`

When the owner clicks the description, the system shall replace it with a textarea one row tall that grows with its content and shows the placeholder "Describe this board..."; Enter shall insert a line break, blur shall store the trimmed text, an empty text shall remove the description, and Esc shall discard the change.

Covers:
- `feat~boards~1`

Tags: UI

### Description in board list
`req~boards.description.list~1`

While a board has a description, the board list shall show its first line next to the board title on a single line, cut with an ellipsis where it exceeds the available width.

Covers:
- `feat~boards~1`

Tags: UI

## Emoji icon

### Emoji placeholder
`req~boards.emoji.placeholder~1`

While a board has no emoji, the system shall show an empty placeholder field left of its title.

Covers:
- `feat~boards~1`

Tags: UI

### Emoji picker
`req~boards.emoji.picker~1`

When the owner clicks the placeholder or the current emoji, the system shall open an emoji picker; when they choose an emoji, the system shall store it and show it in place of the placeholder; the picker shall also offer "Remove".

Covers:
- `feat~boards~1`

### Same emoji control everywhere
`req~boards.emoji.reuse~1`

The board list and the board page title shall use the same emoji control with identical behaviour.

Covers:
- `feat~boards~1`

Tags: UI

### Emoji read-only
`req~boards.emoji.readonly~1`

While the viewer is not the owner, the system shall show the emoji without placeholder or picker.

Covers:
- `feat~boards~1`

## Board page

### Board URL
`req~boards.page.url~2`

The system shall serve each board at `/<username>/<slug>/` with the owner's username and a slug derived from the board title, unique among the owner's boards by appending -1, -2 and so on; when the board is renamed, the slug shall follow the new title.

Covers:
- `feat~boards~1`

### Board access
`req~boards.page.access~1`

If a user who is not a member of a board requests its page, archive or any of its data, then the system shall answer 404.

Rationale:
404 does not reveal whether the board exists.

Covers:
- `feat~boards~1`

Tags: Security

### Board page header
`req~boards.page.header~1`

The board page shall show emoji and title as heading, followed by the buttons "Archive what's done" and "Open archive", and for the owner a "Share" control.

Covers:
- `feat~boards~1`

Tags: UI

### Ownership of content
`req~boards.ownership~1`

The system shall treat every list and task on a board as owned by the board owner, regardless of which member created it.

Covers:
- `feat~boards~1`

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

Each board list entry shall be one card that opens the board page when clicked anywhere, except on the emoji field, which opens the emoji picker for the owner, and the board name, which starts inline editing for the owner.

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
`req~boards.create~1`

When a user types a name into the input at the end of their own boards and presses Enter, the system shall create the board with an empty default list, show it in the list with an empty emoji placeholder, and clear the input for the next name.

Covers:
- `feat~boards~1`

### Starter boards
`req~boards.starter~1`

When an account is created, the system shall create the boards "My Todos" with emoji 🧹 and "Shopping List" with emoji 🛒 for it.

Rationale:
Shows new users what boards are for.

Covers:
- `feat~boards~1`

### Board name
`req~boards.name~1`

The system shall require a board name of 1 to 100 characters.

Covers:
- `feat~boards~1`

### Inline rename
`req~boards.rename~1`

When the owner edits a board name inline, in the board list or in the board page title, the system shall store the new name.

Covers:
- `feat~boards~1`

### Delete board
`req~boards.delete~1`

When the owner confirms deletion of a board in the confirm dialog, the system shall delete the board with all lists, tasks and shares.

Covers:
- `feat~boards~1`

### Owner-only board actions
`req~boards.owner-only~1`

The system shall allow renaming, changing the emoji, sharing and deleting a board only to its owner and shall not show these controls to anyone else.

Covers:
- `feat~boards~1`

Tags: Security

## Emoji icon

### Emoji placeholder
`req~boards.emoji.placeholder~1`

While a board has no emoji, the system shall show an empty placeholder field left of its name.

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

The system shall serve each board at `/<username>/<slug>/` with the owner's username and a slug derived from the board name, unique among the owner's boards by appending -1, -2 and so on; when the board is renamed, the slug shall follow the new name.

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

The board page shall show emoji and name as title, followed by the buttons "Archive what's done" and "Open archive", and for the owner a "Share" control.

Covers:
- `feat~boards~1`

Tags: UI

### Ownership of content
`req~boards.ownership~1`

The system shall treat every list and task on a board as owned by the board owner, regardless of which member created it.

Covers:
- `feat~boards~1`

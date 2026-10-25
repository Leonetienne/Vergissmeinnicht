# Tasks

## Data

### Task fields
`req~tasks.fields~1`

A task shall have a title (1 to 200 characters), a list, a state (`open`, `done` or `archived`), a sort position within its list, an optional due date (date without time), a colour and an optional plain-text note of up to 5000 characters.

Covers:
- `feat~tasks~1`

### Colours
`req~tasks.colours~1`

The system shall offer the task colours none (default), red, orange, yellow, green, blue, purple, grey and turquoise (`#B7C4DE`).

Covers:
- `feat~tasks~1`

### Task anchor
`req~tasks.anchor~1`

Every task card shall carry the HTML id `task-<id>`; when a board or archive page is opened with that anchor, the system shall scroll to the task and highlight it briefly.

Covers:
- `feat~tasks~1`

Tags: UI

## Creating

### Quick entry
`req~tasks.create~2`

Every list shall contain an input for a new task at its top, above the cards; when an editor or the owner types a title and presses Enter, the system shall create an open task at the end of the list's open tasks, clear the input and keep the focus in it.

Covers:
- `feat~tasks~1`

## Card

### Card content
`req~tasks.card.content~1`

A task card shall show the checkbox, the title, the due date if set and the note if set; cards shall be as high as their content needs.

Covers:
- `feat~tasks~1`

Tags: UI

### Note truncation
`req~tasks.card.note~1`

If a note needs more than 3 lines on the card, then the card shall cut it after 3 lines with "...".

Covers:
- `feat~tasks~1`

Tags: UI

### Card colour
`req~tasks.card.colour~1`

The card background shall show the task colour as a subtle tint: very light in light mode, very dark in dark mode, keeping text contrast.

Covers:
- `feat~tasks~1`

Tags: UI

### Due soon warning
`req~tasks.card.due-soon~1`

While an open task's due date is 1 to 3 days ahead, the card shall show the due date with a yellow warning.

Covers:
- `feat~tasks~1`

Tags: UI

### Due warning
`req~tasks.card.due-now~1`

While an open task's due date is today or in the past, the card shall show the due date with a red warning.

Covers:
- `feat~tasks~1`

Tags: UI

### Task order
`req~tasks.order~1`

The system shall order the tasks of a list first by state (open, then done, then archived) and then by sort position, everywhere tasks are listed: board page, archive page, REST API, MCP server and JSON export.

Covers:
- `feat~tasks~1`

### Done tasks
`req~tasks.card.done~2`

The system shall show done tasks muted and without due date warnings.

Covers:
- `feat~tasks~1`

Tags: UI

### Archived tasks hidden
`req~tasks.card.archived~1`

The board page shall not show archived tasks.

Covers:
- `feat~tasks~1`

## States

### Check
`req~tasks.check~1`

When an editor or the owner ticks the checkbox of an open task, the system shall set it to `done` and move it among the done tasks.

Covers:
- `feat~tasks~1`

### Uncheck
`req~tasks.uncheck~1`

When an editor or the owner unticks the checkbox of a done task, the system shall set it to `open` and show it at its stored position among the open tasks.

Covers:
- `feat~tasks~1`

### Allowed transitions
`req~tasks.transitions~1`

The system shall change a task's state only from `open` to `done`, `done` to `open`, `done` to `archived` or `archived` to `done`; if any other change is requested, then the system shall reject it with 409.

Covers:
- `feat~tasks~1`

## Editing and moving

### Title edit on the card
`req~tasks.title-edit~1`

When an editor or the owner clicks or taps a task title on its card, the system shall edit the title inline; a click that ends a drag shall change nothing.

Covers:
- `feat~tasks~1`

### Reorder and move
`req~tasks.drag~3`

When an editor or the owner drags an open or done task, starting anywhere on its card, to another position in its list or into another list, the system shall store its new list and position, keeping its state and placing it among the tasks of that state.

Covers:
- `feat~tasks~1`

### Drop outside lists
`req~tasks.drop-outside~1`

When an editor or the owner drops a task outside every list, the system shall move it to the end of its state's tasks in the default list and show the default list again.

Covers:
- `feat~tasks~1`

### Touch drag
`req~tasks.drag-touch~2`

Dragging tasks, lists and boards shall work with touch input, starting after a short press so that scrolling stays possible.

Covers:
- `feat~tasks~1`

Tags: UI

### Singleview
`req~tasks.singleview~3`

When a member clicks or taps a task card outside its title, checkbox and delete button, the system shall open a small popup with the title, due date (with clear), colour circles, the note as textarea and a "Json export" link; a drag shall move the card without opening it; for editors and the owner every change shall be saved immediately, for observers and on the archive page all fields shall be read-only.

Covers:
- `feat~tasks~1`

Tags: UI

### Close singleview
`req~tasks.singleview-close~1`

When the user presses Esc, clicks outside or clicks the close button, the system shall close the singleview and update the card.

Covers:
- `feat~tasks~1`

Tags: UI

### Delete task
`req~tasks.delete~1`

When an editor or the owner clicks the small "X" on a task card and confirms in the confirm dialog, the system shall delete the task.

Covers:
- `feat~tasks~1`

### Observer view
`req~tasks.observer~1`

While the viewer is an observer, the system shall show cards without new-task inputs, delete buttons, drag handles or active checkboxes.

Covers:
- `feat~tasks~1`

Tags: UI

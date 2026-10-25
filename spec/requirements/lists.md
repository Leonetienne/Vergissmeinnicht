# Lists

## Default list

### One default list
`req~lists.default.exists~1`

The system shall give every board exactly one default list from its creation.

Covers:
- `feat~lists~1`

### Default list appearance
`req~lists.default.appearance~2`

The system shall show the default list leftmost, without header, title or delete button, styled so its tasks look like loose tasks beside the other lists; while it holds no visible task and the board has other lists, the system shall hide it.

Rationale:
Lists only become a visible concept once a user creates one.

Covers:
- `feat~lists~1`

Tags: UI

### Default list protection
`req~lists.default.protected~1`

If a request tries to rename, move or delete the default list, then the system shall reject it.

Covers:
- `feat~lists~1`

## Layout

### Horizontal columns
`req~lists.layout~2`

On screens wider than 768 px, the board page shall show the lists side by side as columns, scrolling horizontally when they exceed the width; the columns shall reach at least down to the bottom of the viewport, keeping the page margins, the board export link and the footer visible.

Covers:
- `feat~lists~1`

Tags: UI

### Stacked on mobile
`req~lists.layout-mobile~1`

On screens up to 768 px wide, the board page shall show the lists stacked vertically.

Covers:
- `feat~lists~1`

Tags: UI

## Managing lists

### Create list
`req~lists.create~1`

Above the lists, the system shall show a small button "Create list", or "Create another list" while the board has a list besides the default list; when clicked, it shall show a title input, and Enter shall create the list at the end; Esc or an empty title shall cancel.

Covers:
- `feat~lists~1`

### List title
`req~lists.name~1`

The system shall require a list title of 1 to 100 characters.

Covers:
- `feat~lists~1`

### Unique list title
`req~lists.name-unique~1`

If a request creates or renames a list with a title that another list of the same board already has, ignoring case, then the system shall reject it and the board page shall show a toast naming the taken title.

Covers:
- `feat~lists~1`

### List header
`req~lists.header~1`

Every list except the default list shall have a header with its title, editable inline, and a small trash button.

Covers:
- `feat~lists~1`

Tags: UI

### Delete list
`req~lists.delete~1`

When an editor or the owner confirms deletion of a list in the confirm dialog, the system shall move all its tasks, of every state, to the end of the default list, keeping their relative order, and delete the list.

Covers:
- `feat~lists~1`

### Reorder lists
`req~lists.reorder~1`

When an editor or the owner drags a list by its header to another position, the system shall store the new order; the default list shall stay first.

Covers:
- `feat~lists~1`

### List export link
`req~lists.export-link~2`

While a list, including the default list, shows a task, it shall end with a "Json export" link at its bottom right.

Covers:
- `feat~lists~1`

Tags: UI

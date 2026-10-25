# Archive

### Archive what's done
`req~archive.archive-done~1`

When an editor or the owner clicks "Archive what's done" on the board page, the system shall set every done task of the board to `archived` and remove them from the board view.

Covers:
- `feat~archive~1`

### Open archive
`req~archive.open~1`

When a member clicks "Open archive", the system shall navigate to `/<id>-<slug>/archive/`.

Covers:
- `feat~archive~1`

### Archive page
`req~archive.page~1`

The archive page shall list all archived tasks of the board grouped by list in list order, each card with its title, due date, colour and note like on the board page.

Covers:
- `feat~archive~1`

Tags: UI

### Selection
`req~archive.select~1`

For editors and the owner, every archived task shall have a selection checkbox.

Covers:
- `feat~archive~1`

### Unarchive selected
`req~archive.unarchive~1`

When an editor or the owner clicks "Unarchive selected", the system shall set every selected task to `done` and remove it from the archive page.

Covers:
- `feat~archive~1`

### Leave archive
`req~archive.leave~1`

When a member clicks "Leave archive", the system shall navigate back to the board page without changing anything.

Covers:
- `feat~archive~1`

### Observer archive
`req~archive.observer~1`

While the viewer is an observer, the archive page shall show the archived tasks without selection checkboxes or "Unarchive selected".

Covers:
- `feat~archive~1`

Tags: UI

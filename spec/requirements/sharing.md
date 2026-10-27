# Board Sharing

### Share dialog
`req~sharing.dialog~2`

When the owner opens "Share" on the board page, the system shall show the current shares with role, a user combobox to add new ones and "Save"; additions, role changes and removals shall apply together on "Save" and be discarded on "Cancel" or close.

Covers:
- `feat~sharing~1`

Tags: UI

### User search
`req~sharing.search~1`

When the owner types at least 3 characters into the user search, the system shall list up to 10 users of the instance whose display name or email address contains the text (case-insensitive), excluding the owner and users already holding a share.

Covers:
- `feat~sharing~1`

### User search autofill
`req~sharing.search-autofill~1`

The user search field shall carry the opt-out markers of the browser and of common password managers, so they offer no autofill there.

Covers:
- `feat~sharing~1`

### Add share
`req~sharing.add~2`

When the owner picks a user from the combobox suggestions by click or arrow keys and Enter, the system shall add the user to the share list with role observer, changeable to editor, and grant the share on "Save", without invitation or acceptance.

Covers:
- `feat~sharing~1`

### Change role
`req~sharing.role~1`

When the owner changes the role of a share, the system shall apply it from the member's next request.

Covers:
- `feat~sharing~1`

### Remove share
`req~sharing.remove~1`

When the owner removes a share, the system shall revoke the member's access to the board.

Covers:
- `feat~sharing~1`

### Leave board
`req~sharing.leave~1`

When a member confirms "Leave board" in the confirm dialog, the system shall remove their share and return them to the board list.

Covers:
- `feat~sharing~1`

### Observer permissions
`req~sharing.observer~1`

While a user is observer of a board, the system shall let them view the board and its archive, search it and export it, and shall neither show nor accept any change to the board, its lists or tasks.

Covers:
- `feat~sharing~1`

Tags: Security

### Editor permissions
`req~sharing.editor~1`

While a user is editor of a board, the system shall let them do everything the owner can do with lists and tasks, including archiving and restoring, but not rename, change the emoji, share or delete the board.

Covers:
- `feat~sharing~1`

Tags: Security

### Server-side enforcement
`req~sharing.enforce~1`

If a request tries an action the member's role does not allow, then the system shall reject it with 403 regardless of the interface used.

Covers:
- `feat~sharing~1`

Tags: Security

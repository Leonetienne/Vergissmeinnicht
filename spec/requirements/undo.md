# Undo and Redo

### Undo key
`req~undo.undo~1`

When the user presses Ctrl+Z or Cmd+Z outside a text input, the system shall reverse their most recent undoable action on the current page.

Covers:
- `feat~undo~1`

### Redo keys
`req~undo.redo~1`

When the user presses Ctrl+Shift+Z, Cmd+Shift+Z, Ctrl+Y or Cmd+Y outside a text input, the system shall repeat the most recently undone action.

Covers:
- `feat~undo~1`

### Native text undo
`req~undo.text-input~1`

While the focus is in a text input or textarea, the system shall leave undo and redo keys to the browser.

Covers:
- `feat~undo~1`

Tags: UI

### Browser-side history
`req~undo.client-side~1`

The system shall keep the undo and redo history in the browser for the current page only, up to 100 entries, and perform every undo and redo through the regular operations; it shall keep no history on the server.

Rationale:
Keeps the server simple; reloading or leaving the page clears the history.

Covers:
- `feat~undo~1`

### New action clears redo
`req~undo.clear-redo~1`

When the user performs a new undoable action, the system shall discard the redo history.

Covers:
- `feat~undo~1`

### Undoable actions
`req~undo.scope~1`

The system shall make these actions undoable: create, rename, delete and reorder boards; change a board emoji; create, rename, delete and reorder lists; create, edit, check, uncheck, move and delete tasks; archive what's done; unarchive selected.

Covers:
- `feat~undo~1`

### Not undoable
`req~undo.excluded~1`

Deleting a board, deleting the account, sharing changes and settings shall not be undoable; deleting a board or the account stays guarded by the confirm dialog.

Covers:
- `feat~undo~1`

### Restoring deletions
`req~undo.restore~1`

When a deleted task or list is restored by undo, the system shall recreate it from its serialized state at its former position, including the former tasks of a deleted list, and later undo and redo entries shall refer to the recreated items.

Covers:
- `feat~undo~1`

### Undo feedback
`req~undo.feedback~1`

When an undo or redo runs, the system shall show a short toast naming the action; if it fails, then the system shall show the error, drop the entry and reload the affected data.

Covers:
- `feat~undo~1`

Tags: UI

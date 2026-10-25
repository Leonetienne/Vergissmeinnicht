# ConfirmDialog

The confirm dialog asks before a destructive action with a message, "Cancel" and "OK".

- One shared dialog, `window.confirmDialog(message)`, never the browser's native `confirm()`.
- Esc and "Cancel" abort; "OK" is `vm-btn--danger` for deletions.
- The message names what happens: "Delete board Household with all its lists and tasks?"
- Used for deleting a task, list, board or account, and for "Leave board".

Consumer provides: the message text; it resolves to true or false.

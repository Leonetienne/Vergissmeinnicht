# Glossary

| Term | Meaning |
|---|---|
| User | A registered account, identified by a unique email address and shown by its display name. |
| Board | A named container of lists and tasks with an optional emoji icon. Has exactly one owner. |
| Owner | The user who created a board. Owns the board and every list and task in it, regardless of who created them. |
| Share | A grant of access to a board for one other user, with a role. |
| Member | The owner or a user holding a share on a board. |
| Observer | Share role with read access: view, search and export. |
| Editor | Share role with read and write access to lists and tasks. |
| List | An ordered column of tasks on a board. |
| Default list | The untitled list every board has from creation. Cannot be renamed, moved or deleted. Shown without a header so its tasks look like loose tasks beside the other lists. |
| Task | A to-do item with title, state, optional due date, colour and note, belonging to one list. |
| State | The lifecycle position of a task: `open`, `done` or `archived`. |
| Transition | A change of state between neighbouring states: open and done, or done and archived. |
| Archive | The page of a board listing its archived tasks. |
| Card | The visual representation of a task inside a list. |
| Singleview | The small popup with all editable details of one task, opened through its "..." button. |
| Inline edit | Editing a text in place: plain text until clicked, then an input field. |
| Confirm dialog | The shared in-page OK/Cancel modal used before destructive actions. |
| Operation | One action of the central operation layer, used by the frontend, the REST API and the MCP server. |
| Serializer | The single JSON representation of a board, list or task, used by the API, the MCP server and the JSON export. |
| Undo stack | The in-browser history of undoable actions of the current page, with its redo counterpart. |
| API key | A user's secret for the REST API. |
| MCP key | A user's secret for the MCP server. |
| Backdrop | A user's custom background image behind the UI. |
| UI opacity | The opacity of the UI surfaces (lists, cards, panels) in front of the backdrop. |
| Recovery code | A single-use code that replaces a TOTP code and removes the second factor when used. |
| Reminder | An email about an open task whose due date is near or reached. |

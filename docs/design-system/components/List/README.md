# List

A list is a column of task cards on a board.

- The default list (`vm-list--default`) is leftmost, has no header, title, ground or trash button, so its tasks look like loose tasks.
- Other lists sit on `surface-sunken` with a header: small colour circles top right, then title (inline edit) and a trash button. Dragging by the header reorders lists; the default list stays first.
- A list colour tints the list ground with `task-<colour>-tint`, like a card.
- Order inside: open cards, the "New task" entry input, done cards, then "Json export" at the bottom right.
- Enter in the entry input creates the task at the end of the open tasks, clears the input and keeps focus.
- `vm-board` lays lists out as `list-width` columns that scroll horizontally, stacked full width up to 768px.
- Above the board: a small ghost button "Create list", or "Create another list" once a second list exists.

Consumer provides: the list (default or not, title), its cards, and the viewer's role. Observers get no entry input, colour circles or trash button.

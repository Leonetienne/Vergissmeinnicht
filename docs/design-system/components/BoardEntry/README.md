# BoardEntry

A board entry is one row of the board list on the start page, linking to the board.

- Left: the emoji control. Then the board name, inline editable for the owner.
- Own boards come first, draggable to reorder, followed by the "New board" entry input.
- "Shared with me" follows as a `vm-section-title`, hidden while empty, sorted alphabetically; each entry shows the owner's display name and the viewer's role in `vm-board-entry__meta`.

Consumer provides: emoji, name, URL, and for shared boards owner name and role.

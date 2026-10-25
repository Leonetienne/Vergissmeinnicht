# SearchPopup

The search popup finds boards and tasks across every board the user is a member of.

- Opens with Ctrl+F or Cmd+F or the header's search button, focus in the input.
- From 2 characters it lists matches as you type, boards first, at most 50.
- A board result shows emoji and name; a task result shows its title, the board's emoji and name, and a `vm-tag` "done" or "archived" where it applies.
- Arrow keys move the `aria-selected` row, Enter or click opens it; Esc or a click outside closes.

Consumer provides: results from the search operation.

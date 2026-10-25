# InlineEdit

Inline edit shows a text as plain text until clicked, then as an input in the same place and type style.

- Applies to board names, list titles and task titles, and nothing else.
- Enter or blur saves; Esc restores the previous value; an empty value restores it too.
- Hover shows `accent-soft` behind the text; the input shows a `focus-ring` border.
- Wrap the text in `vm-inline`; swap it for `vm-inline-input` while editing. The input inherits font and colour from its container.

Consumer provides: the current value, the save operation, and whether the viewer may edit (observers get plain text without `vm-inline`).

Lives once as `templates/partials/_inline_edit.html` with its script.

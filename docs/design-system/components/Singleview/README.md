# Singleview

The singleview is the small popup with every editable detail of one task, opened by its "..." button.

- Fields: title, due date with "Clear", colour circles, note (up to 5000 characters), then "Json export".
- Every change saves immediately; there is no Save button.
- Esc, a click outside or "×" closes it and updates the card.
- Observers see the same fields read-only.
- Width `singleview-width`, `shadow-pop`, over the `scrim`.

Consumer provides: the serialized task and the viewer's role.

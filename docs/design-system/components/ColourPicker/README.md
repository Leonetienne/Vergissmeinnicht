# ColourPicker

Colour circles pick a task's colour in the singleview.

- Nine circles in fixed order: none, red, orange, yellow, green, blue, purple, grey, turquoise.
- Each circle shows `task-<colour>` with a `border-strong` edge; "none" is a dashed empty circle.
- The selected one has `aria-checked="true"` and a `focus-ring` halo.
- Choosing saves immediately and tints the card.

Consumer provides: the current colour and the save operation. Observers see the circles without interaction.

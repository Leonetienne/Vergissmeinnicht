# TaskCard

A task card shows one task: checkbox, title, due date if set, note if set.

- Cards grow with their content; the title wraps and the note cuts after 3 lines.
- Colour: set `data-colour` to red, orange, yellow, green, blue, purple, grey or turquoise; the card ground takes `task-<colour>-tint`. No attribute means none.
- Due date: `vm-due--soon` (1 to 3 days ahead) or `vm-due--now` (today or past). Done tasks show the plain date.
- Done: `vm-card--done` mutes and strikes the title; done cards sit below all open cards and are not draggable.
- "..." opens the singleview, "×" asks through the confirm dialog, then deletes.
- Anchor: the card carries `id="task-<id>"`; when opened by that anchor add `vm-card--highlight` briefly.
- Observer: disabled checkbox, no "×", no drag handle.

Consumer provides: the serialized task (title, state, due date, colour, note) and the viewer's role.

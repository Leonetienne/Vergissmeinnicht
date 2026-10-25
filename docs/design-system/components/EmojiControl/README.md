# EmojiControl

The emoji control shows a board's emoji and lets the owner change it.

- No emoji: an empty dashed placeholder (`vm-emoji--empty`), owner only.
- Click opens `vm-emoji-picker`: search input, emoji grid, "Remove".
- Non-owners see the emoji as `vm-emoji--readonly`, without placeholder or picker.
- Same control, same behaviour in the board list and the board page title.
- Emoji data is served locally.

Consumer provides: the current emoji (or none), whether the viewer owns the board, and the save operation.

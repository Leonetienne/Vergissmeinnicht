# Vergissmeinnicht design system

Exported from the design system artifact https://claude.ai/artifact/3UenZLrpfc6xKMCKoRrLNA, which stays the source; re-export after changing it there.

- `tokens.json`: every colour, type style, spacing, radius, shadow, size and opacity token, light and dark values. In SCSS each token becomes a CSS custom property of the same name (`--accent`, `--space-2`, `--radius-md`); light values on `:root`, dark values in `@media (prefers-color-scheme: dark)`.
- `components/<Name>/README.md`: usage rules per component. `components/<Name>/preview.html`: HTML reference for markup and states.
- `components/bundle.css`: reference styles with `vm-` classes, written against the tokens.

Vergissmeinnicht is a small, self-hosted to-do app: tasks on boards, optionally split into Kanban-like lists, shared with other users as observer or editor. The interface stays quiet so the user's own tasks, colours and backdrop carry the page. One cool accent, plain system type, soft cards, nothing loaded from the internet.

## Content fundamentals

- Write the UI in English, sentence case.
- Keep labels as short as possible. Buttons are verbs or verb phrases: "Share", "Open archive", "Archive what's done", "Leave archive", "Unarchive selected", "Create list", "Create another list", "Leave board", "Delete account", "Remove".
- Keep the spec's exact strings: "Json export", "Shared with me", "Open Source on Github", "OK", "Cancel".
- Status and error messages state what happened in a few words. No apology, no "Please", no "try again", no exclamation marks. Examples: "Task deleted", "Board name is required", "Undo: move task".
- Confirm dialogs name the consequence: "Delete this list? Its tasks move to the default list." / "Delete your account? All boards and tasks you own are deleted."
- Help text only where a field is not self-explanatory, one short line.
- No emoji in UI copy. Emoji appear only as the board icon a user picks.
- Address the user implicitly; avoid "we" and "you" where a verb alone works.

## Visual foundations

### Colour

- Themes follow the browser's `prefers-color-scheme`. In the app, declare light values on `:root` and dark values in `@media (prefers-color-scheme: dark)`; this system shows them as the `light` and `dark` themes.
- Theme only through CSS custom properties (`var(--accent)`), never SCSS variables.
- Page ground is `bg`. Cards, header, inputs and popups are `surface`. List columns sit on `surface-sunken`; the default list has no ground so its cards read as loose tasks.
- `accent` is the one brand colour: `#B7C4DE` in dark, its darker shade `#4A5E86` in light. Use it for primary buttons, links, checked checkboxes and focus. Text on it is `on-accent`.
- Hover for quiet controls is `accent-soft`.
- Text is `ink`; secondary text (notes, meta, done tasks, labels) is `ink-muted`. Both read on `bg`, `surface`, `surface-sunken` and every `task-*-tint`.
- Lines: `border` for decorative hairlines, `border-strong` for anything a user operates (inputs, checkboxes, secondary buttons, colour circles).
- Task colours: none, red, orange, yellow, green, blue, purple, grey, turquoise. Show the full `task-<colour>` only in the colour circles; the card ground uses `task-<colour>-tint`, which stays very light in light mode and very dark in dark mode so `ink` keeps its contrast. Turquoise is fixed at `#B7C4DE`.
- Due dates: 1 to 3 days ahead `warning` on `warning-soft`; today or past `danger` on `danger-soft` with a "!" marker, so the two differ in more than hue. Done tasks show no warning.
- Errors and destructive OK buttons use `danger` with `on-danger`. Status toasts use `inverse` with `on-inverse`.

### Backdrop and UI opacity

- A user may set a backdrop image behind every page. It replaces `bg`.
- UI opacity (`ui-opacity-min` 0.3 to `ui-opacity-max` 1) applies to `surface`, `surface-sunken`, task tints and the header, so paint those grounds with alpha, never the whole element: text stays fully opaque.

### Type

- One family: the system UI stack (`--font-sans`), so nothing is downloaded. Monospace (`--font-mono`) only for keys, secrets and recovery codes in `code`.
- `board-title` for the board page title. `section-title` for list headers, board list sections, settings sections and dialog titles. `task-title` on cards, `body` elsewhere, `note` for task notes, `label` for buttons and fields, `meta` for due dates, role labels and the footer.
- Task titles wrap; notes cut after 3 lines with an ellipsis.

### Spacing and layout

- 4px steps: `space-1` to `space-8`. Cards in a list sit `space-2` apart; columns `space-4` apart.
- From 769px lists are `list-width` columns side by side, scrolling horizontally. Up to `breakpoint-stack` (768px) they stack full width.
- Every page works from `viewport-min` (360px).
- Page gutter: `space-4` on mobile, `space-6` from 768px.

### Shape and depth

- `radius-md` for cards, buttons, inputs, toasts; `radius-lg` for list columns and popups; `radius-sm` for checkboxes, badges, icon buttons; `radius-full` only for colour circles.
- Two shadows: `shadow-card` on cards and board entries, `shadow-pop` on anything floating (singleview, dialogs, menus, emoji picker, toasts). Floating layers over the page get the `scrim`.
- No gradients, no coloured side borders.

### States and motion

- Focus: 2px solid `focus-ring` outline, 2px offset, on every focusable element. It is at least 3:1 on `surface`, `surface-sunken` and `bg` in both themes.
- Changes show at once (optimistic); a rejected change restores the previous display and raises an error toast.
- Toasts sit bottom right and close after 5 seconds or by their "×".
- A task opened by its `#task-<id>` anchor scrolls into view and shows the `focus-ring` outline briefly.
- Keep motion short and functional: drag, toast in and out, highlight fade. No decorative animation.

### Roles in the UI

- Observers see the same cards with nothing to operate: no checkbox action, no new-task input, no "×", no drag handle, read-only singleview fields.
- Only the owner sees the emoji placeholder, rename, "Share" and delete for a board.

## Iconography

- No icon library. Icons are inline SVG at 16px, 1.5px stroke, round caps, `currentColor`, inside `vm-icon-btn`.
- Text glyphs where the spec names them: "..." opens the singleview, "×" deletes a task or closes a toast.
- Emoji appear only as board icons, chosen in the emoji picker from locally served emoji data.
- There is no logo. The app name is set in `section-title` in the header.

## Components

All components are plain HTML styled by `components/bundle.css` with `vm-` classes; behaviour lives in the app's Alpine.js partials. Each exists once and is reused: confirm dialog, inline edit, emoji control and search popup are shared partials.

## Self-containment

Fonts, scripts, emoji data and images ship with the app. Never reference a CDN or web font.

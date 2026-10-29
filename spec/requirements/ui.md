# User Interface Framework

### Language
`req~ui.language~1`

The UI shall be in English.

Covers:
- `feat~ui~1`

### Colour mode
`req~ui.theme~2`

The UI shall show light or dark colours as the user's colour mode says: "Light", "Dark", or "System" (default), which follows the browser's preference.

Covers:
- `feat~ui~1`

### Colour themes
`req~ui.colour-themes~2`

The system shall offer the colour themes "Turquoise" (default), "OLED" (pure black in dark mode, pure white in light mode) and "Bubblegum" (pink), each with light and dark colours.

Covers:
- `feat~ui~1`

### Bubblegum decoration
`req~ui.bubblegum~1`

While the Bubblegum theme is active, the UI shall show a playful look: rounded type and shapes, sticker shadows, a dotted pastel page ground, a striped header edge and drifting forget-me-not flowers behind the content; with reduced motion preferred, nothing moves.

Covers:
- `feat~ui~1`

### Theme menu
`req~ui.theme-menu~1`

When a user picks a colour mode or colour theme in the header's theme menu, the system shall apply it at once without a page reload and store it with the account, so it applies on every page and device.

Covers:
- `feat~ui~1`

### Accent colour
`req~ui.accent~2`

In the Turquoise theme the UI shall use `#B7C4DE` as accent colour in dark mode and a darker shade of it with sufficient contrast on light backgrounds in light mode; every other theme shall use one accent per mode with the same contrast.

Covers:
- `feat~ui~1`

### Header
`req~ui.header~3`

Every logged-in page shall have a header with the app icon followed by "<display name>'s Home" linking to the board list, a search button, a theme menu and a menu with Settings and Logout.

Covers:
- `feat~ui~1`

### Footer
`req~ui.footer~1`

Every page shall have a footer showing the value of `APP_VERSION` and a link "Open Source on Github" to the project's repository.

Covers:
- `feat~ui~1`

### Confirm dialog
`req~ui.confirm~1`

The system shall ask for destructive actions through one reusable in-page OK/Cancel dialog with a message, never the browser's native dialog; Esc and Cancel shall abort.

Covers:
- `feat~ui~1`

### Inline edit
`req~ui.inline-edit~3`

Inline-editable texts (board titles, list titles and task titles) shall show as plain text until clicked, then turn into an input; Enter or leaving the input shall save, Esc shall restore the previous value; an empty value shall restore the previous value.

Covers:
- `feat~ui~1`

### Emoji picker
`req~ui.emoji-picker~1`

The emoji picker shall be one reusable component with search, served from local assets.

Covers:
- `feat~ui~1`

### Toasts
`req~ui.toasts~1`

The system shall show transient messages and errors as toasts in the bottom-right corner, closing after 5 seconds or by their close button.

Covers:
- `feat~ui~1`

### Immediate feedback
`req~ui.optimistic~1`

When a member changes something on a board page, the system shall update the page without a full reload; if the server rejects the change, then the system shall restore the previous display and show the error as toast.

Covers:
- `feat~ui~1`

### Background refresh
`req~ui.refresh~1`

While the board overview, a board page or an archive page is visible, the system shall fetch its data from the server and update the page without a full reload when the browser tab becomes visible again and at least once a minute; while a text field or dialog is open, a drag is in progress, a change is being sent or a delayed display change such as a lingering tick is pending, the system shall postpone the reload.

Covers:
- `feat~ui~1`

### Responsive layout
`req~ui.responsive~1`

Every page shall be usable on screens from 360 px wide.

Covers:
- `feat~ui~1`

### Backdrop and opacity
`req~ui.backdrop~1`

While a user has a backdrop or UI opacity below 100, every page shall render them according to the user's appearance settings.

Covers:
- `feat~ui~1`

### Labels and messages
`req~ui.wording~1`

UI labels shall be short, buttons verbs, and status and error messages shall state what happened in few words without apologies.

Covers:
- `feat~ui~1`

### Error pages
`req~ui.error-pages~1`

When a page request fails with status 400, 403, 404 or 500, the system shall show a page in the app's design with the status code, a short title, one line of explanation and a "Go home" link to the board list.

Covers:
- `feat~ui~1`

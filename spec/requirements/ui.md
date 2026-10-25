# User Interface Framework

### Language
`req~ui.language~1`

The UI shall be in English.

Covers:
- `feat~ui~1`

### Theme
`req~ui.theme~1`

The UI shall follow the browser's light or dark preference throughout.

Covers:
- `feat~ui~1`

### Accent colour
`req~ui.accent~1`

The UI shall use `#B7C4DE` as accent colour in dark mode and a darker shade of it with sufficient contrast on light backgrounds in light mode.

Covers:
- `feat~ui~1`

### Header
`req~ui.header~2`

Every logged-in page shall have a header with the app icon followed by "<display name>'s Home" linking to the board list, a search button and a menu with Settings and Logout.

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

# User Settings

### Settings page
`req~settings.page~1`

The system shall provide a settings page at `/settings/`, reachable from every page, with the sections Profile, Password, Notifications, Second factor, API key, MCP key, Appearance and Delete account.

Covers:
- `feat~settings~1`

Tags: UI

### Independent sections
`req~settings.sections~1`

Each settings section shall be saved by its own action without affecting the others.

Covers:
- `feat~settings~1`

Tags: UI

### Profile
`req~settings.profile~1`

The Profile section shall let the user change display name and email address.

Covers:
- `feat~settings~1`

### Notifications
`req~settings.notifications~1`

Where email is configured, the Notifications section shall let the user switch due date reminders on or off (default on); while email is not configured, the system shall hide the section.

Covers:
- `feat~settings~1`

## Keys

### Key generation
`req~settings.keys.generate~1`

When a user generates an API key or an MCP key, the system shall show the key once, store only its hash, and replace any previous key of the same kind.

Covers:
- `feat~settings~1`

Tags: Security

### Key revocation
`req~settings.keys.revoke~1`

When a user revokes an API key or MCP key, the system shall delete it so that requests with it fail with 401.

Covers:
- `feat~settings~1`

Tags: Security

### Key status
`req~settings.keys.status~1`

The settings page shall show for each key kind whether a key exists, its creation date and its last use date.

Covers:
- `feat~settings~1`

### Separate keys
`req~settings.keys.separate~1`

The system shall accept the API key only on the REST API and the MCP key only on the MCP server.

Covers:
- `feat~settings~1`

Tags: Security

## Appearance

### Backdrop upload
`req~settings.backdrop.upload~1`

When a user uploads a PNG, JPEG, WebP or GIF of at most 20 MB as backdrop, the system shall store it and display it fixed behind the content of every page for that user only.

Covers:
- `feat~settings~1`

### Backdrop removal
`req~settings.backdrop.remove~1`

When a user removes their backdrop, the system shall delete the file and show the plain theme background again.

Covers:
- `feat~settings~1`

### Backdrop privacy
`req~settings.backdrop.private~1`

The system shall serve a backdrop image only to its owner.

Covers:
- `feat~settings~1`

Tags: Privacy, Security

### Backdrop options
`req~settings.backdrop.options~1`

The system shall let a user set backdrop mode (cover or fit) and backdrop opacity (0 to 100).

Covers:
- `feat~settings~1`

### Backdrop CSS
`req~settings.backdrop.css~1`

The system shall let a user enter two free CSS declaration boxes of up to 2000 characters each for the backdrop, one for all screens and one for screens up to 768 px wide, previewed live while typing.

Covers:
- `feat~settings~1`

### Backdrop CSS sanitising
`req~settings.backdrop.css-sanitise~1`

The system shall strip the characters `< > { } & @`, backtick and backslash from backdrop CSS before storing it.

Rationale:
Prevents breaking out of the style context.

Covers:
- `feat~settings~1`

Tags: Security

### UI opacity
`req~settings.ui-opacity~1`

The system shall let a user set the opacity of UI surfaces (lists, cards, panels, header) from 30 to 100, previewed live, so the backdrop shows through.

Rationale:
The lower bound keeps text readable.

Covers:
- `feat~settings~1`

## Delete account

### Delete account section
`req~settings.delete~1`

The Delete account section shall offer a "Delete account" button that asks through the confirm dialog, naming that all owned boards and tasks are deleted, before deleting the account.

Covers:
- `feat~settings~1`

Tags: UI

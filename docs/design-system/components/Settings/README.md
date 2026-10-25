# Settings

The settings page at `/settings/` holds every account option in independent sections.

- Sections in order: Profile, Password, Notifications, Second factor, API key, MCP key, Appearance, Delete account. Each is a `vm-settings__section` with its own button; saving one leaves the others untouched.
- Notifications shows only while email is configured.
- Keys: status line with creation and last use date, "Generate" and "Revoke". A new key appears once in `code` with "Copy"; generating replaces the old key.
- Appearance: backdrop upload with "Remove", mode Cover or Fit, backdrop opacity 0 to 100, two CSS boxes (all screens, up to 768px, 2000 characters each), UI opacity 30 to 100. CSS boxes and UI opacity preview live.
- Delete account: `vm-settings__section--danger`, button asks through the confirm dialog naming that owned boards and tasks are deleted.
- Column up to 640px wide; field pairs sit side by side in `vm-grid-2` and stack on narrow screens.

Consumer provides: the user's current values, key status, factor status, email configuration.

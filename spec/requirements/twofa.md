# Second-Factor Authentication

### TOTP setup
`req~twofa.setup~1`

When a user starts second-factor setup, the system shall show a locally generated QR code and the secret as text, and activate the factor only after the user enters a valid code from it.

Covers:
- `feat~twofa~1`

### One factor per user
`req~twofa.single~1`

The system shall allow at most one TOTP factor per user.

Covers:
- `feat~twofa~1`

### Recovery codes
`req~twofa.recovery-codes~1`

When a TOTP factor is activated, the system shall generate 10 single-use recovery codes, show them once with a copy button, and store only their hashes.

Covers:
- `feat~twofa~1`

Tags: Security

### Login challenge
`req~twofa.challenge~1`

While a user has a TOTP factor, after a correct password the system shall require either a valid TOTP code or a recovery code before completing the login.

Covers:
- `feat~twofa~1`

Tags: Security

### Code validity
`req~twofa.window~1`

The system shall accept a TOTP code of the current 30-second step and one step before or after, and reject a code that was already used for this account.

Covers:
- `feat~twofa~1`

Tags: Security

### Recovery code at login
`req~twofa.recovery-login~1`

When a user enters a valid recovery code in the login challenge, the system shall log them in, remove their TOTP factor with all recovery codes, and tell them that the second factor was removed.

Covers:
- `feat~twofa~1`

Tags: Security

### Removal in session
`req~twofa.remove~1`

When a logged-in user removes their second factor on the settings page and confirms with a valid TOTP code or recovery code, the system shall remove the factor and all recovery codes.

Covers:
- `feat~twofa~1`

Tags: Security

### Removal by admin
`req~twofa.cli.remove~1`

The command `remove_user_2fa <email>` shall remove the account's TOTP factor and recovery codes without further checks.

Covers:
- `feat~twofa~1`

Tags: Operations

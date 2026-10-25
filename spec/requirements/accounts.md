# Accounts and Authentication

## Registration

### Self-registration
`req~accounts.register~1`

Where `ENABLE_REGISTRATION` is `TRUE`, when a visitor submits display name, email address and password on the registration page, the system shall create the account and log the visitor in.

Covers:
- `feat~accounts~1`

### Registration disabled
`req~accounts.register-disabled~1`

While `ENABLE_REGISTRATION` is not `TRUE`, the system shall hide the registration link and answer requests to the registration page with 404.

Covers:
- `feat~accounts~1`

Tags: Security

### No email verification
`req~accounts.no-verification~1`

The system shall accept any syntactically valid email address at registration and email change without sending a confirmation email.

Covers:
- `feat~accounts~1`

### Unique email
`req~accounts.unique-email~1`

If an email address is already used by another account (case-insensitive), then the system shall reject registration or email change with an error message.

Covers:
- `feat~accounts~1`

### Password rules
`req~accounts.password-rules~1`

The system shall validate new passwords with Django's standard password validators at registration, password change and in the management commands.

Covers:
- `feat~accounts~1`

Tags: Security

### Display name
`req~accounts.display-name~1`

The system shall require a display name of 1 to 100 characters for every account.

Covers:
- `feat~accounts~1`

## Login and session

### Login
`req~accounts.login~1`

When a visitor submits a matching email address (case-insensitive) and password on `/login`, the system shall log them in, or show the second-factor challenge first if the account has one.

Covers:
- `feat~accounts~1`

### Login rate limit
`req~accounts.login-rate-limit~1`

If 5 failed login or second-factor attempts for one email address occur within 15 minutes, then the system shall refuse further attempts for that address for 15 minutes.

Covers:
- `feat~accounts~1`

Tags: Security

### Login redirect
`req~accounts.login-redirect~1`

While a visitor is not logged in, the system shall redirect every page request except login and registration to `/login`, keeping the requested path as `next` and returning there after login.

Covers:
- `feat~accounts~1`

Tags: Security

### Safe next parameter
`req~accounts.safe-next~1`

If the `next` parameter points to another host, then the system shall redirect to the start page instead.

Covers:
- `feat~accounts~1`

Tags: Security

### Logout
`req~accounts.logout~1`

When a user logs out, the system shall end the session and show the login page.

Covers:
- `feat~accounts~1`

## Account changes

### Password change
`req~accounts.password-change~1`

When a user submits their current password and a new password on the settings page, the system shall change the password and keep the current session logged in.

Covers:
- `feat~accounts~1`

### Email change
`req~accounts.email-change~1`

When a user submits a new email address on the settings page, the system shall store it immediately and use it for login and reminders.

Covers:
- `feat~accounts~1`

### Account deletion
`req~accounts.delete~1`

When a user confirms "Delete account" in the confirm dialog, the system shall delete the account, every board they own with all its lists, tasks and shares, all shares they hold on other boards, their keys, second factor and backdrop file, then log them out.

Covers:
- `feat~accounts~1`

Tags: Privacy

## Management commands

### Create user
`req~accounts.cli.create~1`

The command `create_user <email> [-p password] [--name name]` shall create an account, prompting for the password when `-p` is missing and using the email's local part as display name when `--name` is missing; it shall work regardless of `ENABLE_REGISTRATION`.

Covers:
- `feat~accounts~1`

Tags: Operations

### Set password
`req~accounts.cli.password~1`

The command `set_user_password <email> [-p password]` shall set a new password for the account, prompting for it when `-p` is missing.

Covers:
- `feat~accounts~1`

Tags: Operations

### Delete user
`req~accounts.cli.delete~1`

The command `delete_user <email> [--yes]` shall delete the account with the same effects as account deletion in the UI, asking for confirmation unless `--yes` is given.

Covers:
- `feat~accounts~1`

Tags: Operations

### Unknown account
`req~accounts.cli.unknown~1`

If a management command names an email address without account, then it shall print an error and exit with a non-zero status.

Covers:
- `feat~accounts~1`

Tags: Operations

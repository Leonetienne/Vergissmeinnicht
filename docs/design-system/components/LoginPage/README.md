# LoginPage

The login page signs a visitor in with email and password; the registration page sits beside it in the same layout.

- One `vm-auth__panel` centred on `bg` (or the backdrop): app name in `board-title` size, fields, primary button, one link below.
- Login: "Email", "Password", "Log in". Errors as `vm-error` above the button, few words: "Email or password is wrong", "Too many attempts, wait 15 minutes".
- "Create account" shows only while `ENABLE_REGISTRATION` is `TRUE`; the registration page asks for "Display name", "Email", "Password".
- After a correct password, accounts with a second factor continue to the TOTP challenge (see TwoFactor).
- No header on these pages; the footer stays.

Consumer provides: form errors, the `next` parameter, whether registration is enabled.

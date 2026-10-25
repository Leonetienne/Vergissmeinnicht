# TwoFactor

TwoFactor covers the TOTP login challenge and the setup, recovery codes and removal in settings.

- Challenge: after a correct password, one "Code" field accepting a TOTP code or a recovery code, button "Verify". A used recovery code logs in and a toast says "Second factor removed".
- Setup: QR code generated locally (`vm-qr`, always dark modules on a light ground so scanners read it in both themes), the secret as `code` text, a "Code" field and "Activate". The factor counts only after a valid code.
- Recovery codes: 10 codes in `vm-codes`, shown once, with "Copy".
- Removal: needs a valid code or recovery code, then "Remove second factor" (`vm-btn--danger`).
- At most one factor per user; while one is active the section shows its status and the removal row.

Consumer provides: the QR SVG and secret from the server, the codes, the factor status.

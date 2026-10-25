import io
import secrets
import time
from datetime import timedelta
from pathlib import Path

import pyotp
import segno
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone
from PIL import Image

from boards.services import Conflict, Invalid, clean_text

from .models import FailedLogin, RecoveryCode, User, hash_secret

LOGIN_LIMIT = 5
LOGIN_WINDOW = timedelta(minutes=15)
CSS_MAX = 2000
CSS_FORBIDDEN = set("<>{}&@`\\")
BACKDROP_MAX_BYTES = 20 * 1024 * 1024
BACKDROP_FORMATS = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp", "GIF": "gif"}


# Profile

def clean_email(value):
    value = clean_text(value, "Email", 254).lower()
    try:
        validate_email(value)
    except ValidationError:
        raise Invalid("Email is not valid")
    return value


def check_email_free(email, user=None):
    taken = User.objects.filter(email__iexact=email)
    if user is not None:
        taken = taken.exclude(pk=user.pk)
    if taken.exists():
        raise Conflict("Email is already in use")


def check_password(password, user=None):
    try:
        validate_password(password, user)
    except ValidationError as e:
        raise Invalid(" ".join(e.messages))


def register(display_name, email, password):
    display_name = clean_text(display_name, "Display name", 100)
    email = clean_email(email)
    check_email_free(email)
    check_password(password, User(email=email, display_name=display_name))
    return User.objects.create_user(email, password, display_name=display_name)


def update_profile(user, display_name=None, email=None, reminders_enabled=None):
    if display_name is not None:
        user.display_name = clean_text(display_name, "Display name", 100)
    if email is not None:
        email = clean_email(email)
        check_email_free(email, user)
        user.email = email
    if reminders_enabled is not None:
        user.reminders_enabled = bool(reminders_enabled)
    user.save()
    return user


def profile_data(user):
    return {
        "id": user.id,
        "display_name": user.display_name,
        "email": user.email,
        "reminders_enabled": user.reminders_enabled,
    }


@transaction.atomic
def delete_account(user):
    remove_backdrop(user)
    user.delete()


# Login rate limit

def login_blocked(email):
    since = timezone.now() - LOGIN_WINDOW
    return FailedLogin.objects.filter(email=email.strip().lower(), at__gte=since).count() >= LOGIN_LIMIT


def record_failure(email):
    FailedLogin.objects.create(email=email.strip().lower())


def clear_failures(email):
    FailedLogin.objects.filter(email=email.strip().lower()).delete()


# Second factor

def new_totp_secret():
    return pyotp.random_base32()


def totp_uri(user, secret):
    return pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Vergissmeinnicht")


def qr_svg(data):
    """QR code as SVG of unit rects, styled by .vm-qr."""
    qr = segno.make(data, error="m")
    rows = list(qr.matrix)
    size = len(rows)
    rects = "".join(
        f'<rect x="{x}" y="{y}" width="1" height="1"/>'
        for y, row in enumerate(rows)
        for x, cell in enumerate(row)
        if cell
    )
    return f'<svg viewBox="0 0 {size} {size}" aria-label="QR code" shape-rendering="crispEdges">{rects}</svg>'


def totp_step(secret, code, last_step=None, now=None):
    """Return the matching time step for code within one step of now, or None. Rejects reused steps."""
    code = (code or "").replace(" ", "")
    if not code.isdigit() or len(code) != 6:
        return None
    totp = pyotp.TOTP(secret)
    current = int((now if now is not None else time.time()) // 30)
    for step in (current - 1, current, current + 1):
        if last_step is not None and step <= last_step:
            continue
        if secrets.compare_digest(totp.generate_otp(step), code):
            return step
    return None


def activate_totp(user, secret, code):
    """Activate the factor if code is valid. Returns the 10 recovery codes or None."""
    step = totp_step(secret, code)
    if step is None:
        return None
    codes = [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}" for _ in range(10)]
    with transaction.atomic():
        user.totp_secret = secret
        user.totp_last_step = step
        user.save(update_fields=["totp_secret", "totp_last_step"])
        RecoveryCode.objects.filter(user=user).delete()
        RecoveryCode.objects.bulk_create(RecoveryCode(user=user, code_hash=hash_secret(c)) for c in codes)
    return codes


def remove_totp(user):
    with transaction.atomic():
        user.totp_secret = ""
        user.totp_last_step = None
        user.save(update_fields=["totp_secret", "totp_last_step"])
        RecoveryCode.objects.filter(user=user).delete()


def verify_second_factor(user, code):
    """Return "totp", "recovery" or None. A recovery code removes the factor."""
    if not user.has_totp:
        return None
    step = totp_step(user.totp_secret, code, user.totp_last_step)
    if step is not None:
        user.totp_last_step = step
        user.save(update_fields=["totp_last_step"])
        return "totp"
    normalized = (code or "").strip().lower()
    if normalized and RecoveryCode.objects.filter(user=user, code_hash=hash_secret(normalized)).exists():
        remove_totp(user)
        return "recovery"
    return None


# Appearance

def sanitise_css(value):
    value = "".join(ch for ch in (value or "") if ch not in CSS_FORBIDDEN)
    return value[:CSS_MAX].strip()


def clamp_int(value, low, high, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def update_appearance(user, mode, backdrop_opacity, css, css_mobile, ui_opacity):
    user.backdrop_mode = mode if mode in ("cover", "fit") else "cover"
    user.backdrop_opacity = clamp_int(backdrop_opacity, 0, 100, 100)
    user.backdrop_css = sanitise_css(css)
    user.backdrop_css_mobile = sanitise_css(css_mobile)
    user.ui_opacity = clamp_int(ui_opacity, 30, 100, 100)
    user.save()


def backdrop_dir():
    path = Path(settings.MEDIA_ROOT) / "backdrops"
    path.mkdir(parents=True, exist_ok=True)
    return path


def store_backdrop(user, upload):
    """Verify, re-encode and store an uploaded image as the user's backdrop."""
    if upload.size > BACKDROP_MAX_BYTES:
        raise Invalid("Backdrop is larger than 20 MB")
    data = upload.read()
    try:
        Image.open(io.BytesIO(data)).verify()
        image = Image.open(io.BytesIO(data))
        fmt = image.format
        if fmt not in BACKDROP_FORMATS:
            raise Invalid("Backdrop must be PNG, JPEG, WebP or GIF")
        out = io.BytesIO()
        if fmt == "GIF":
            image.save(out, "GIF", save_all=True)
        elif fmt == "JPEG":
            image.convert("RGB").save(out, "JPEG", quality=90)
        else:
            image.save(out, fmt)
    except Invalid:
        raise
    except Exception:
        raise Invalid("Backdrop is not a valid image")
    name = f"{user.pk}-{secrets.token_hex(8)}.{BACKDROP_FORMATS[fmt]}"
    (backdrop_dir() / name).write_bytes(out.getvalue())
    remove_backdrop(user, save=False)
    user.backdrop = name
    user.save(update_fields=["backdrop"])


def backdrop_path(user):
    return backdrop_dir() / user.backdrop if user.backdrop else None


def remove_backdrop(user, save=True):
    path = backdrop_path(user)
    if path is not None:
        path.unlink(missing_ok=True)
    user.backdrop = ""
    if save:
        user.save(update_fields=["backdrop"])

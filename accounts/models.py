import hashlib
import secrets

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# First URL segments the app uses itself, so no username may take them.
RESERVED_USERNAMES = {"login", "logout", "register", "settings", "api", "mcp", "export", "static", "admin"}


def unique_slug(base, taken, fallback):
    """base, or base-1, base-2, ... whichever is not in taken."""
    base = slugify(base)[:60].strip("-") or fallback
    slug, n = base, 0
    while slug in taken:
        n += 1
        slug = f"{base}-{n}"
    return slug


def hash_secret(value):
    return hashlib.sha256(value.encode()).hexdigest()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, display_name="", starter_boards=True, **extra):
        from boards.services import create_starter_boards

        email = self.normalize_email(email).lower()
        display_name = display_name or email.split("@")[0][:100]
        taken = set(self.filter(username__startswith=slugify(display_name)[:60]).values_list("username", flat=True))
        username = unique_slug(display_name, taken | RESERVED_USERNAMES, "user")
        user = self.model(email=email, display_name=display_name, username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        if starter_boards:
            create_starter_boards(user)
        return user

    def create_superuser(self, email, password=None, **extra):
        return self.create_user(email, password, is_staff=True, is_superuser=True, **extra)

    def get_by_email(self, email):
        return self.get(email__iexact=email.strip())


class User(AbstractBaseUser, PermissionsMixin):
    BACKDROP_MODES = [("cover", "Cover"), ("fit", "Fit")]

    email = models.EmailField(unique=True)
    username = models.SlugField(max_length=70, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    reminders_enabled = models.BooleanField(default=True)

    backdrop = models.CharField(max_length=200, blank=True)
    backdrop_mode = models.CharField(max_length=5, choices=BACKDROP_MODES, default="cover")
    backdrop_opacity = models.PositiveSmallIntegerField(default=100)
    backdrop_css = models.TextField(blank=True)
    backdrop_css_mobile = models.TextField(blank=True)
    ui_opacity = models.PositiveSmallIntegerField(default=100)

    totp_secret = models.CharField(max_length=64, blank=True)
    totp_last_step = models.BigIntegerField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def has_totp(self):
        return bool(self.totp_secret)


class RecoveryCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recovery_codes")
    code_hash = models.CharField(max_length=64)


class Key(models.Model):
    API = "api"
    MCP = "mcp"
    KINDS = [(API, "API key"), (MCP, "MCP key")]
    PREFIX = {API: "vmk_", MCP: "vmm_"}

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keys")
    kind = models.CharField(max_length=3, choices=KINDS)
    key_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "kind"], name="one_key_per_kind")]

    @classmethod
    def generate(cls, user, kind):
        raw = cls.PREFIX[kind] + secrets.token_urlsafe(32)
        cls.objects.filter(user=user, kind=kind).delete()
        cls.objects.create(user=user, kind=kind, key_hash=hash_secret(raw))
        return raw

    @classmethod
    def authenticate(cls, raw, kind):
        key = cls.objects.select_related("user").filter(key_hash=hash_secret(raw), kind=kind).first()
        if key is None or not key.user.is_active:
            return None
        cls.objects.filter(pk=key.pk).update(last_used_at=timezone.now())
        return key.user


class FailedLogin(models.Model):
    email = models.CharField(max_length=254, db_index=True)
    at = models.DateTimeField(default=timezone.now)

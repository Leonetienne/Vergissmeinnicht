import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=""):
    return os.environ.get(name, default)


def env_bool(name):
    return env(name).upper() == "TRUE"


DEBUG = env_bool("DEBUG")

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS").split(",") if h.strip()]
if not DEBUG:
    for name, value in (("DJANGO_SECRET_KEY", SECRET_KEY), ("ALLOWED_HOSTS", ALLOWED_HOSTS)):
        if not value:
            raise ImproperlyConfigured(f"{name} is required while DEBUG is off")
else:
    SECRET_KEY = SECRET_KEY or "dev-insecure-secret-key"
    ALLOWED_HOSTS = ALLOWED_HOSTS or ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "boards",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "vergissmeinnicht.urls"
WSGI_APPLICATION = "vergissmeinnicht.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "vergissmeinnicht.context_processors.app",
            ],
        },
    },
]

# Without DB_HOST a local SQLite file keeps tests and quick runs Docker-free.
if env("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", "3306"),
            "NAME": env("DB_NAME", "vergissmeinnicht"),
            "USER": env("DB_USER", "vergissmeinnicht"),
            "PASSWORD": env("DB_PASSWORD"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "data" / "db.sqlite3"}}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 3}},
]
LOGIN_URL = "/login"

LANGUAGE_CODE = "en"
TIME_ZONE = env("TIME_ZONE", "Europe/Berlin")
USE_I18N = False
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
WHITENOISE_USE_FINDERS = DEBUG
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DATA_DIR = Path(env("DATA_DIR", str(BASE_DIR / "data")))
MEDIA_ROOT = DATA_DIR / "media"
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

ENABLE_REGISTRATION = env_bool("ENABLE_REGISTRATION")
APP_VERSION = env("APP_VERSION", "dev")
SITE_URL = env("SITE_URL", "http://localhost:8080").rstrip("/")
REPOSITORY_URL = "https://github.com/Leonetienne/vergissmeinnicht"

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT", "25") or 25)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "vergissmeinnicht@localhost")
EMAIL_CONFIGURED = bool(EMAIL_HOST)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
CSRF_TRUSTED_ORIGINS = [SITE_URL]

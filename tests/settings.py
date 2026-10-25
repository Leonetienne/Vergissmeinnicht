import os
import tempfile

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret")
os.environ.setdefault("ALLOWED_HOSTS", "testserver,localhost")

from vergissmeinnicht.settings import *  # noqa: E402,F401,F403
from vergissmeinnicht.settings import STORAGES  # noqa: E402

STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
MEDIA_ROOT = tempfile.mkdtemp(prefix="vm-media-")
WHITENOISE_AUTOREFRESH = True
STATIC_ROOT = None

"""
Django settings for dc_master project.
"""

from pathlib import Path
import os
import shutil

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure--vw)rh*5gpn&su952&kcugzg1-rsi!@)e-vtp(fi@4os_f4qh9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "student",
    "trainer",
    "bd",
    "administration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dc_master.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dc_master.wsgi.application"


# ─── Database ──────────────────────────────────────────────────────────────────
# On Vercel: filesystem is read-only except /tmp.
# We copy the pre-seeded db.sqlite3 to /tmp on cold start (handled in wsgi.py).
# Locally: use the project db.sqlite3 directly.

IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    DB_PATH = '/tmp/db.sqlite3'
else:
    DB_PATH = str(BASE_DIR / 'db.sqlite3')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
    }
}

# ─── Sessions ──────────────────────────────────────────────────────────────────
# Use signed cookies so sessions don't need DB writes
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 hours

# ─── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 4},
    },
]

# ─── Internationalization ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# CompressedStaticFilesStorage: serves gzip/brotli compressed files
# but does NOT rename files with hashes, so {% static %} tags always
# produce /static/css/styles.css which WhiteNoise can serve directly.
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── Default primary key field type ───────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Custom Auth User Model ────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard_redirect"
LOGOUT_REDIRECT_URL = "login"

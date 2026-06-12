"""Minimal Django settings to use the app standalone — for mypy's
django-stubs plugin and for running the test suite (locally or in CI):

    python -m django test mkview --settings=test_settings

Never used to serve a real project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "not-a-secret"  # nosec: tooling only, never serves requests

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "mkview",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "test_urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

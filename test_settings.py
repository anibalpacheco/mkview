"""Minimal Django settings so tools (mypy's django-stubs plugin) can load
the app standalone — not used to run a real project."""

SECRET_KEY = "not-a-secret"  # nosec: tooling only, never serves requests

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "mkview",
]

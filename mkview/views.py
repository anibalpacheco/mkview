from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.module_loading import import_string
from django.views import View
from django.views.static import serve


def default_access(request):
    """Default MKVIEW_ACCESS_CALLBACK: superusers."""
    return request.user.is_superuser


def get_site_dir():
    """Resolve the mkdocs build output dir.

    MKVIEW_SITE_DIR takes precedence; otherwise site_dir is read from
    BASE_DIR/mkdocs.yml, falling back to mkdocs' own default ("site").
    The dir must stay out of STATIC_ROOT — anything there is served
    publicly, bypassing the access callback.
    """
    site_dir = getattr(settings, "MKVIEW_SITE_DIR", None)
    if site_dir:
        return Path(site_dir)
    import yaml

    base_dir = Path(settings.BASE_DIR)
    config = yaml.safe_load((base_dir / "mkdocs.yml").read_text(encoding="utf-8"))
    return base_dir / config.get("site_dir", "site")


class DocsView(UserPassesTestMixin, View):
    """Serve the mkdocs-built site behind a configurable access gate.

    MKVIEW_ACCESS_CALLBACK is a callable (or dotted path to one) taking the
    request and returning a bool — the SHOW_TOOLBAR_CALLBACK pattern from
    django-debug-toolbar. Defaults to superusers.
    Anonymous users are redirected to LOGIN_URL; authenticated users failing
    the gate get a 403 (UserPassesTestMixin behaviour).
    """

    def test_func(self):
        callback = getattr(settings, "MKVIEW_ACCESS_CALLBACK", default_access)
        if isinstance(callback, str):
            callback = import_string(callback)
        return callback(self.request)

    def get(self, request, path):
        # mkdocs builds directory URLs (use_directory_urls): each page is a
        # <page>/index.html, so bare/trailing-slash paths resolve to the index.
        if path == "" or path.endswith("/"):
            path += "index.html"
        return serve(request, path, document_root=get_site_dir())

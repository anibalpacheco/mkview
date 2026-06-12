"""
DocsView: access-gated serving of the mkdocs-built site.

Access is controlled by MKVIEW_ACCESS_CALLBACK (callable or dotted path
taking the request, returning a bool); the default is superusers.
The site dir comes from MKVIEW_SITE_DIR or, failing that,
from BASE_DIR/mkdocs.yml — tests run against temp dirs via those settings.
"""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase, override_settings
from django.urls import reverse


def _make_site(root: Path):
    (root / "index.html").write_text("<h1>Docs home</h1>")
    (root / "dev-setup").mkdir()
    (root / "dev-setup" / "index.html").write_text("<h1>Dev setup</h1>")


class DocsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site_dir = Path(tempfile.mkdtemp())
        cls.addClassCleanup(shutil.rmtree, cls.site_dir)
        _make_site(cls.site_dir)
        cls.settings_override = override_settings(MKVIEW_SITE_DIR=cls.site_dir)
        cls.settings_override.enable()
        cls.addClassCleanup(cls.settings_override.disable)

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.staff = user_model.objects.create_user("staff", password="x", is_staff=True)
        cls.plain = user_model.objects.create_user("plain", password="x")
        cls.superuser = user_model.objects.create_superuser("super", password="x")

    def _docs_url(self, path=""):
        return reverse("mkview:docs", kwargs={"path": path})

    def test_anonymous_redirects_to_login(self):
        resp = self.client.get(self._docs_url())
        self.assertEqual(resp.status_code, 302)
        self.assertIn(resolve_url(settings.LOGIN_URL), resp["Location"])

    def test_non_superuser_gets_403(self):
        for username in ("plain", "staff"):
            self.client.login(username=username, password="x")
            resp = self.client.get(self._docs_url())
            self.assertEqual(resp.status_code, 403)

    def test_superuser_gets_site_index(self):
        self.client.login(username="super", password="x")
        resp = self.client.get(self._docs_url())
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Docs home", b"".join(resp.streaming_content))

    @override_settings(MKVIEW_ACCESS_CALLBACK=lambda request: request.user.is_staff)
    def test_access_callback_setting_overrides_default(self):
        self.client.login(username="plain", password="x")
        self.assertEqual(self.client.get(self._docs_url()).status_code, 403)
        # staff fails the default gate, so a 200 proves the override applies
        self.client.login(username="staff", password="x")
        self.assertEqual(self.client.get(self._docs_url()).status_code, 200)

    @override_settings(MKVIEW_ACCESS_CALLBACK="mkview.views.default_access")
    def test_access_callback_accepts_dotted_path(self):
        self.client.login(username="super", password="x")
        self.assertEqual(self.client.get(self._docs_url()).status_code, 200)
        self.client.login(username="staff", password="x")
        self.assertEqual(self.client.get(self._docs_url()).status_code, 403)

    def test_directory_url_serves_nested_index(self):
        self.client.login(username="super", password="x")
        resp = self.client.get(self._docs_url("dev-setup/"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Dev setup", b"".join(resp.streaming_content))

    def test_missing_page_returns_404(self):
        self.client.login(username="super", password="x")
        resp = self.client.get(self._docs_url("nope/"))
        self.assertEqual(resp.status_code, 404)

    def test_site_dir_falls_back_to_mkdocs_yml(self):
        base_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base_dir)
        (base_dir / "built").mkdir()
        _make_site(base_dir / "built")
        (base_dir / "mkdocs.yml").write_text("site_name: x\nsite_dir: built\n")
        self.client.login(username="super", password="x")
        with override_settings(MKVIEW_SITE_DIR=None, BASE_DIR=base_dir):
            resp = self.client.get(self._docs_url())
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Docs home", b"".join(resp.streaming_content))

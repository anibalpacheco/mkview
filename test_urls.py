"""URLconf for test_settings: just the app under /docs/."""

from django.urls import include, path

urlpatterns = [
    path("docs/", include("mkview.urls")),
]

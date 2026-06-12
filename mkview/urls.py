from django.urls import re_path

from .views import DocsView

app_name = "mkview"

urlpatterns = [
    re_path(r"^(?P<path>.*)$", DocsView.as_view(), name="docs"),
]

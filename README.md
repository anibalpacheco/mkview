# mkview

Reusable Django app that serves an mkdocs-built site from the same Django
project the app is installed in, behind a configurable access gate.

## Usage

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "mkview",
]

# urls.py
urlpatterns = [
    ...,
    path("docs/", include("mkview.urls")),
]
```

Build the docs with `mkdocs build` and the site is served at `/docs/`.

## Settings

All optional:

- `MKVIEW_ACCESS_CALLBACK` — callable (or dotted path to one) taking the
  request and returning a bool, same pattern as django-debug-toolbar's
  `SHOW_TOOLBAR_CALLBACK`. Default: superusers
  (`request.user.is_superuser`). Anonymous users are redirected to
  `LOGIN_URL`; authenticated users failing the gate get a 403. Any extra
  conditions (e.g. `is_active`) are the callback's responsibility.

  ```python
  # e.g. open the docs up to staff users
  MKVIEW_ACCESS_CALLBACK = lambda request: request.user.is_staff
  ```

- `MKVIEW_SITE_DIR` — path to the mkdocs build output. Default: the
  `site_dir` read from `BASE_DIR/mkdocs.yml` (mkdocs' own default: `site`).
  Reading mkdocs.yml requires PyYAML.

The site dir must stay out of `STATIC_ROOT` — anything there is served
publicly, bypassing the access callback.

## Tests

From a project with the app installed:

```bash
python manage.py test mkview
```

"""Pytest configuration shared by the whole suite.

Settings are adjusted for the test run only. ``project/settings.py`` derives
several values from ``DEBUG``, which comes from an untracked ``.env``, and the
view tests cannot pass under either value as shipped:

- ``DEBUG=True`` installs the ``debug_toolbar`` middleware, but Django's test
  runner forces ``settings.DEBUG = False``, so ``project/urls.py`` never
  registers the ``djdt`` namespace the middleware tries to reverse. Every view
  test fails with ``NoReverseMatch``.
- ``DEBUG=False`` turns on ``SECURE_SSL_REDIRECT`` and manifest static storage,
  so the test client gets 301 responses instead of rendered pages.

Neutralizing both here keeps the suite's result independent of a developer's
local ``.env``.
"""


def pytest_configure() -> None:
    """Strip deployment-only behavior that breaks the Django test client."""
    from django.conf import settings

    settings.MIDDLEWARE = [
        middleware
        for middleware in settings.MIDDLEWARE
        if "debug_toolbar" not in middleware
    ]
    settings.SECURE_SSL_REDIRECT = False
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }

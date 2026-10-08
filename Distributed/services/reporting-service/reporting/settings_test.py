"""Default pytest database. SQLite so the suite does not need Docker or reporting Postgres."""

from __future__ import annotations

from reporting.settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": ":memory:"},
    }
}

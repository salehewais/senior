"""Process settings for reporting_db and the broker.

This module refuses a DSN whose database name is order_db or odoo_db.
The reporting login in compose.yaml exists only on the reporting server,
which does not host those databases.
"""

from __future__ import annotations

import os
from urllib.parse import unquote, urlparse

DEFAULT_DATABASE_URL = "postgresql://reporting_service:reporting_service@127.0.0.1:5433/reporting_db"
DEFAULT_RABBITMQ_URL = "amqp://order_service:order_service@127.0.0.1:5672/%2F"

REFUSED_DATABASES = frozenset({"order_db", "odoo_db"})


def database_url() -> str:
    return os.environ.get("REPORTING_DATABASE_URL", DEFAULT_DATABASE_URL)


def rabbitmq_url() -> str:
    return os.environ.get("RABBITMQ_URL", DEFAULT_RABBITMQ_URL)


def rabbitmq_timeout_seconds() -> float:
    return _positive_float("RABBITMQ_TIMEOUT_SECONDS", 5.0)


def db_connect_timeout_seconds() -> int:
    return _positive_int("DB_CONNECT_TIMEOUT_SECONDS", 5)


def db_statement_timeout_ms() -> int:
    return _positive_int("DB_STATEMENT_TIMEOUT_MS", 10000)


def django_database() -> dict[str, object]:
    """Django DATABASES['default'] for reporting_db. One alias, one database."""

    url = database_url()
    parsed = urlparse(url)
    scheme = parsed.scheme.split("+", 1)[0]
    if scheme not in {"postgresql", "postgres"}:
        raise RuntimeError("reporting-service only opens a PostgreSQL DSN for reporting_db.")
    name = parsed.path.lstrip("/")
    if name in REFUSED_DATABASES:
        raise RuntimeError(
            f"reporting-service refuses to open {name}. Reports read reporting_db, which is filled from events."
        )
    if not name or name != "reporting_db":
        raise RuntimeError("reporting-service only opens the database named reporting_db.")
    port = parsed.port or 5432
    timeout = db_connect_timeout_seconds()
    statement_ms = db_statement_timeout_ms()
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "127.0.0.1",
        "PORT": str(port),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "connect_timeout": timeout,
            "options": f"-c statement_timeout={statement_ms}",
        },
    }


def _positive_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    value = int(raw)
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero.")
    return value


def _positive_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    value = float(raw)
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero.")
    return value

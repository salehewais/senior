"""Process settings for notification_db and the broker.

This module refuses a DSN whose database name is order_db, reporting_db, or
odoo_db. The check runs before SQLAlchemy creates an engine.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://notification_service:notification_service@127.0.0.1:5435/notification_db"
)
DEFAULT_RABBITMQ_URL = "amqp://order_service:order_service@127.0.0.1:5672/%2F"

REFUSED_DATABASES = frozenset({"order_db", "reporting_db", "odoo_db"})
REQUIRED_DATABASE = "notification_db"


def notification_database_url() -> str:
    return require_notification_database(os.environ.get("NOTIFICATION_DATABASE_URL", DEFAULT_DATABASE_URL))


def require_notification_database(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.split("+", 1)[0]
    if scheme not in {"postgresql", "postgres"}:
        raise RuntimeError("notification-service only opens a PostgreSQL DSN for notification_db.")
    name = parsed.path.lstrip("/").split("/", 1)[0]
    if name in REFUSED_DATABASES:
        raise RuntimeError(
            f"notification-service refuses to open {name}. "
            "Notifications use notification_db and do not open order_db, reporting_db, or odoo_db."
        )
    if name != REQUIRED_DATABASE:
        raise RuntimeError("notification-service only opens the database named notification_db.")
    return url


def rabbitmq_url() -> str:
    return os.environ.get("RABBITMQ_URL", DEFAULT_RABBITMQ_URL)


def rabbitmq_timeout_seconds() -> float:
    return _positive_float("RABBITMQ_TIMEOUT_SECONDS", 5.0)


def db_connect_timeout_seconds() -> int:
    return _positive_int("DB_CONNECT_TIMEOUT_SECONDS", 5)


def http_port() -> int:
    return _positive_int("NOTIFICATION_HTTP_PORT", 8002)


def metrics_port() -> int:
    return _positive_int("METRICS_PORT", 9100)


def jwt_public_key() -> str:
    inline = os.environ.get("JWT_PUBLIC_KEY", "")
    if inline.strip():
        return inline
    path = os.environ.get("JWT_PUBLIC_KEY_PATH", "")
    if not path:
        return ""
    file = Path(path)
    if not file.is_file():
        return ""
    return file.read_text(encoding="utf-8")


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

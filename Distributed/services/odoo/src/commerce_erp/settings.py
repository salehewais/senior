"""Process settings. Passwords and tokens come from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

FORBIDDEN_DATABASES = frozenset({"order_db", "reporting_db"})
ODOO_DATABASE = "odoo_db"


@dataclass(frozen=True, slots=True)
class Settings:
    rabbitmq_url: str
    rabbitmq_timeout_seconds: float
    odoo_url: str
    odoo_db: str
    odoo_user: str
    odoo_password: str
    odoo_timeout_seconds: float
    order_service_url: str
    internal_service_token: str
    order_service_timeout_seconds: float
    odoo_database_url: str
    db_connect_timeout_seconds: float
    db_statement_timeout_ms: int
    outbox_poll_interval_seconds: float
    outbox_batch_size: int
    outbox_max_attempts: int

    def require_odoo_database_url(self) -> str:
        """The inventory publisher opens odoo_db. It does not open order_db or reporting_db."""

        name = urlparse(self.odoo_database_url).path.lstrip("/")
        if name in FORBIDDEN_DATABASES:
            raise RuntimeError(f"Refusing to open {name}. The inventory publisher uses {ODOO_DATABASE} only.")
        if name != ODOO_DATABASE:
            raise RuntimeError(f"Refusing database {name or '(none)'}. Expected {ODOO_DATABASE}.")
        return self.odoo_database_url

    @classmethod
    def from_environ(cls) -> Settings:
        return cls(
            rabbitmq_url=os.environ.get(
                "RABBITMQ_URL",
                "amqp://order_service:order_service@127.0.0.1:5672/%2F",
            ),
            rabbitmq_timeout_seconds=_positive_float("RABBITMQ_TIMEOUT_SECONDS", 5),
            odoo_url=os.environ.get("ODOO_URL", "http://127.0.0.1:8069"),
            odoo_db=os.environ.get("ODOO_DB", ODOO_DATABASE),
            odoo_user=os.environ.get("ODOO_USER", "admin"),
            odoo_password=os.environ.get("ODOO_PASSWORD", "admin"),
            odoo_timeout_seconds=_positive_float("ODOO_TIMEOUT_SECONDS", 5),
            order_service_url=os.environ.get("ORDER_SERVICE_URL", "http://127.0.0.1:8000"),
            internal_service_token=os.environ.get("INTERNAL_SERVICE_TOKEN", ""),
            order_service_timeout_seconds=_positive_float("ORDER_SERVICE_TIMEOUT_SECONDS", 5),
            odoo_database_url=os.environ.get(
                "ODOO_DATABASE_URL",
                "postgresql://odoo:odoo@127.0.0.1:5434/odoo_db",
            ),
            db_connect_timeout_seconds=_positive_float("DB_CONNECT_TIMEOUT_SECONDS", 5),
            db_statement_timeout_ms=int(_positive_float("DB_STATEMENT_TIMEOUT_MS", 10000)),
            outbox_poll_interval_seconds=_positive_float("OUTBOX_POLL_INTERVAL_SECONDS", 1),
            outbox_batch_size=int(_positive_float("OUTBOX_BATCH_SIZE", 100)),
            outbox_max_attempts=int(_positive_float("OUTBOX_MAX_ATTEMPTS", 5)),
        )


def _positive_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "")
    if raw == "":
        return default
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value

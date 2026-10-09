"""The service refuses every database that is not notification_db."""

from __future__ import annotations

from pathlib import Path

import pytest

from notification_service.settings import require_notification_database
from notification_service.store import SqlStore
from notification_service.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_EVENTS,
    QUEUE_NOTIFICATION,
    RETRY_DELAYS_MS,
    declare_notification_topology,
)

SERVICE_ROOT = Path(__file__).resolve().parents[1]


def test_order_reporting_and_odoo_databases_are_refused_before_an_engine_exists(monkeypatch) -> None:
    created: list[object] = []

    def _engine(*args, **kwargs):
        created.append((args, kwargs))
        raise AssertionError("create_engine must not run for a refused database")

    monkeypatch.setattr("notification_service.store.create_engine", _engine)
    for name in ("order_db", "reporting_db", "odoo_db"):
        url = f"postgresql+psycopg://notification_service:secret@127.0.0.1:5432/{name}"
        monkeypatch.setenv("NOTIFICATION_DATABASE_URL", url)
        with pytest.raises(RuntimeError, match=name):
            SqlStore.from_settings()
    assert created == []
    accepted = require_notification_database(
        "postgresql+psycopg://notification_service:secret@127.0.0.1:5435/notification_db"
    )
    assert accepted.endswith("/notification_db")


def test_service_files_do_not_embed_another_database_url() -> None:
    for path in SERVICE_ROOT.rglob("*"):
        allowed = {".py", ".yml", ".yaml", ".ini", ".md", ".toml"}
        if ".venv" in path.parts or "__pycache__" in path.parts or path.suffix not in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "://" not in line:
                continue
            for name in ("order_db", "reporting_db", "odoo_db"):
                assert name not in line, f"{path} contains a URL for {name}"


class _Channel:
    def __init__(self) -> None:
        self.queues: list[dict[str, object]] = []
        self.binds: list[dict[str, object]] = []

    def exchange_declare(self, **kwargs) -> None:
        del kwargs

    def queue_declare(self, **kwargs) -> None:
        self.queues.append(kwargs)

    def queue_bind(self, **kwargs) -> None:
        self.binds.append(kwargs)


def test_topology_matches_the_commerce_retry_ladder() -> None:
    channel = _Channel()
    declare_notification_topology(channel)
    primary = next(item for item in channel.queues if item["queue"] == QUEUE_NOTIFICATION)
    assert "arguments" not in primary
    retry_queues = [item for item in channel.queues if ".retry." in str(item["queue"])]
    assert [item["arguments"]["x-message-ttl"] for item in retry_queues] == list(RETRY_DELAYS_MS)
    assert {item["arguments"]["x-dead-letter-exchange"] for item in retry_queues} == {EXCHANGE_COMMERCE_EVENTS}
    dlq = next(item for item in channel.queues if str(item["queue"]).endswith(".dlq"))
    assert "arguments" not in dlq
    assert any(
        item["queue"] == f"{QUEUE_NOTIFICATION}.dlq"
        and item["exchange"] == EXCHANGE_COMMERCE_DLX
        and item["routing_key"] == DLQ_ROUTING_KEY
        for item in channel.binds
    )
    business = {
        item["routing_key"]
        for item in channel.binds
        if item["queue"] == QUEUE_NOTIFICATION and item["exchange"] == EXCHANGE_COMMERCE_EVENTS
    }
    assert "order.confirmed" in business
    assert "payment.failed" in business
    assert "order.*" not in business

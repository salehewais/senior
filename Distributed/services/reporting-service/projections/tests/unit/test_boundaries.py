"""Boundaries that keep this service off order_db and off the signing key."""

from __future__ import annotations

import threading
from pathlib import Path

import pytest
from reporting.config import DEFAULT_DATABASE_URL, django_database

from projections.messaging.consumer import consume_until_stopped
from projections.messaging.topology import PREFETCH_COUNT
from projections.models import CustomerProjection


def test_default_database_is_reporting_db_on_5433() -> None:
    assert DEFAULT_DATABASE_URL.endswith("@127.0.0.1:5433/reporting_db")
    assert "order_db" not in DEFAULT_DATABASE_URL
    assert "odoo_db" not in DEFAULT_DATABASE_URL


def test_order_db_dsn_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "REPORTING_DATABASE_URL",
        "postgresql://reporting_service:reporting_service@127.0.0.1:5432/order_db",
    )
    with pytest.raises(RuntimeError, match="order_db"):
        django_database()


def test_settings_do_not_read_a_private_key() -> None:
    text = Path("reporting/settings.py").read_text(encoding="utf-8")
    assert "JWT_PRIVATE" not in text
    assert "private_key" not in text.lower()


def test_customer_projection_has_no_password_material() -> None:
    names = {field.name for field in CustomerProjection._meta.get_fields()}
    assert "password" not in names
    assert "password_hash" not in names
    assert "refresh_token" not in names


def test_prefetch_is_small_and_fixed() -> None:
    assert PREFETCH_COUNT == 10


def test_shutdown_finishes_current_work_then_cancels_and_the_caller_closes() -> None:
    events: list[str] = []
    stop = threading.Event()

    class Loop:
        def call_later(self, delay: float, callback) -> int:
            del delay, callback
            return 1

        def remove_timeout(self, handle: int) -> None:
            del handle

    class Impl:
        ioloop = Loop()

    class Connection:
        _impl = Impl()

        def process_data_events(self, time_limit: float = 0) -> None:
            del time_limit
            events.append("callback")
            stop.set()

    class Channel:
        is_open = True

        def basic_cancel(self, consumer_tag: str) -> None:
            del consumer_tag
            events.append("cancel")

    consume_until_stopped(Connection(), Channel(), "tag", stop, 1)
    events.append("close")
    assert events == ["callback", "cancel", "close"]

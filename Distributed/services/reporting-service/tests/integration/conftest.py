"""Skip the pipeline when local Postgres or RabbitMQ is not accepting connections."""

from __future__ import annotations

import socket

import pytest


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def _postgres_up() -> bool:
    if not _port_open("127.0.0.1", 5433):
        return False
    try:
        import psycopg
    except ImportError:
        return False
    try:
        with psycopg.connect(
            "postgresql://reporting_service:reporting_service@127.0.0.1:5433/reporting_db",
            connect_timeout=2,
        ) as connection:
            connection.execute("SELECT 1")
    except Exception:
        return False
    return True


def _rabbit_up() -> bool:
    if not _port_open("127.0.0.1", 5672):
        return False
    try:
        from projections.messaging.broker import close_connection, open_connection
    except Exception:
        return False
    try:
        connection = open_connection("amqp://order_service:order_service@127.0.0.1:5672/%2F", 2)
    except Exception:
        return False
    close_connection(connection, timeout_seconds=2)
    return True


def pytest_collection_modifyitems(config, items) -> None:
    del config
    if _postgres_up() and _rabbit_up():
        return
    skip = pytest.mark.skip(reason="reporting Postgres on 127.0.0.1:5433 or RabbitMQ on 127.0.0.1:5672 is not running.")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)

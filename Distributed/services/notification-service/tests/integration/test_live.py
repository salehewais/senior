"""Live Postgres and RabbitMQ checks. Skipped when those processes are down."""

from __future__ import annotations

import socket
import uuid

import pytest

from notification_service.config import rabbitmq_timeout_seconds, rabbitmq_url
from notification_service.messaging.topology import QUEUE_NOTIFICATION, declare_notification_topology
from notification_service.persistence.models import Base
from notification_service.persistence.store import SqlStore


def _open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.integration


def test_notification_db_stores_a_device_token() -> None:
    if not _open("127.0.0.1", 5435):
        pytest.skip("notification postgres is not listening on 127.0.0.1:5435")
    store = SqlStore.from_settings()
    if not store.ping():
        pytest.skip("notification_db did not accept a connection on 127.0.0.1:5435")
    Base.metadata.create_all(store._engine)
    account_id = uuid.uuid4()
    with store.transaction():
        row, created = store.register_token(account_id, f"live-{uuid.uuid4()}", "android")
        assert created
        listed = store.list_tokens(account_id)
    assert [item.id for item in listed] == [row.id]
    with store.transaction():
        assert store.delete_token(account_id, row.id)


def test_broker_declares_the_notification_queue() -> None:
    if not _open("127.0.0.1", 5672):
        pytest.skip("RabbitMQ is not listening on 127.0.0.1:5672")
    from notification_service.messaging.broker import close_connection, open_connection

    timeout = min(rabbitmq_timeout_seconds(), 2.0)
    try:
        connection = open_connection(rabbitmq_url(), timeout)
    except Exception as exc:
        pytest.skip(f"RabbitMQ did not accept a connection: {type(exc).__name__}")
    try:
        channel = connection.channel()
        declare_notification_topology(channel)
        channel.queue_declare(queue=QUEUE_NOTIFICATION, durable=True, passive=True)
    finally:
        close_connection(connection, timeout_seconds=timeout)

"""One real publish and one real ack. Skipped when RabbitMQ is not reachable."""

from __future__ import annotations

import json
import threading
import time
import uuid
from base64 import b64encode
from datetime import UTC, datetime
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pytest

from order_service.application.publishing import to_outbound
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.ids import CustomerId, ProductId
from order_service.domain.value_objects import Money, Quantity
from order_service.infrastructure.messaging.connection import close_connection, open_connection
from order_service.infrastructure.messaging.consumer import run_consumer
from order_service.infrastructure.messaging.publisher import PikaEventPublisher
from order_service.infrastructure.messaging.topology import (
    QUEUE_ODOO_CONFIRMED,
    QUEUE_REPORTING,
    declare_topology,
)
from order_service.infrastructure.settings import Settings


def _settings() -> Settings:
    return Settings()


def _broker_up(settings: Settings) -> bool:
    try:
        connection = open_connection(settings, timeout_seconds=2)
    except Exception:
        return False
    close_connection(connection)
    return True


def _prepare(settings: Settings) -> None:
    connection = open_connection(settings, timeout_seconds=2)
    try:
        channel = connection.channel()
        declare_topology(channel)
        channel.queue_purge(QUEUE_REPORTING)
        channel.queue_purge(QUEUE_ODOO_CONFIRMED)
    finally:
        close_connection(connection)


def _queue_stats(settings: Settings, queue_name: str) -> dict:
    parsed = urlparse(settings.rabbitmq_url)
    user = parsed.username or "order_service"
    password = parsed.password or "order_service"
    host = parsed.hostname or "127.0.0.1"
    token = b64encode(f"{user}:{password}".encode()).decode("ascii")
    # Management listens on 15672 in compose.yaml. The default vhost is "/".
    url = f"http://{host}:15672/api/queues/%2F/{queue_name}"
    request = Request(url, headers={"Authorization": f"Basic {token}"})
    with urlopen(request, timeout=2) as response:
        return json.load(response)


def _ack_total(stats: dict) -> int:
    return int(stats.get("message_stats", {}).get("ack", 0))


def test_publish_is_acked_by_the_consumer() -> None:
    settings = _settings()
    if not _broker_up(settings):
        pytest.skip("RabbitMQ is not running. Start services/order-service/compose.yaml.")
    _prepare(settings)
    before = None
    last_error: Exception | None = None
    for _ in range(10):
        try:
            before = _ack_total(_queue_stats(settings, QUEUE_REPORTING))
            break
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(0.5)
    if before is None:
        pytest.skip(f"RabbitMQ management API is not reachable, so ack stats cannot be read: {last_error}")

    order = Order.create(
        customer_id=CustomerId(uuid.uuid4()),
        items=(
            OrderItem(
                product_id=ProductId(uuid.uuid4()),
                sku="MUG-01",
                quantity=Quantity.of_line(2),
                unit_price=Money(1500, "USD"),
            ),
        ),
        now=datetime(2026, 10, 8, 12, 0, tzinfo=UTC),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    message = to_outbound(order.pending_events()[0])
    seen: list[dict] = []
    errors: list[BaseException] = []
    stop = threading.Event()
    ready = threading.Event()

    def _handle(envelope: dict) -> None:
        seen.append(envelope)

    def _run() -> None:
        try:
            run_consumer(settings, _handle, stop, ready=ready)
        except Exception as exc:
            errors.append(exc)
            ready.set()

    worker = threading.Thread(target=_run, name="rabbitmq-ack-test")
    worker.start()
    try:
        assert ready.wait(10), errors or "consumer did not start"
        # publish() returns only after the broker confirms it accepted the message.
        PikaEventPublisher(settings).publish(message)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not any(item.get("event_id") == str(message.event_id) for item in seen):
            time.sleep(0.05)
    finally:
        stop.set()
        worker.join(10)
    assert not worker.is_alive()
    assert errors == []
    assert [item.get("event_id") for item in seen] == [str(message.event_id)]
    assert seen[0]["event_type"] == "OrderCreated"
    # Management ack totals trail the broker. The queue can already be empty.
    reporting = None
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        reporting = _queue_stats(settings, QUEUE_REPORTING)
        if reporting["messages"] == 0 and _ack_total(reporting) >= before + 1:
            break
        time.sleep(0.1)
    assert reporting is not None
    odoo = _queue_stats(settings, QUEUE_ODOO_CONFIRMED)
    assert reporting["messages"] == 0
    assert reporting.get("messages_unacknowledged", 0) == 0
    assert _ack_total(reporting) >= before + 1
    # order.created is not bound to the Odoo queue. The exchange did the routing.
    assert odoo["messages"] == 0

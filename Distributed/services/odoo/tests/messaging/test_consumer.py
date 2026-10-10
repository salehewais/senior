"""OrderCreated is dead-lettered. The Odoo client is not asked to create a sales order."""

from __future__ import annotations

import json

from commerce_erp.messaging.consuming import DeliveryOutcome, DeliveryResult, settle_delivery

ORDER_ID = "018f1c2a-1111-7c11-8a22-222222222222"
EVENT_ID = "018f1c2a-7b3d-7c11-8a22-111111111111"


class Channel:
    def __init__(self) -> None:
        self.acked: list[int] = []
        self.nacked: list[tuple[int, bool]] = []

    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None:
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None:
        self.nacked.append((delivery_tag, requeue))


class Router:
    def __init__(self) -> None:
        self.retries: list[int] = []
        self.dead: list[str] = []

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        self.retries.append(attempt)

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None:
        self.dead.append(reason)


def _body(event_type: str, status: str) -> bytes:
    return json.dumps(
        {
            "event_id": EVENT_ID,
            "event_type": event_type,
            "occurred_at": "2026-10-08T12:00:00Z",
            "producer": "order-service",
            "aggregate_id": ORDER_ID,
            "correlation_id": ORDER_ID,
            "causation_id": EVENT_ID,
            "version": 1,
            "payload": {"order_id": ORDER_ID, "status": status, "aggregate_version": 1},
        }
    ).encode()


def test_order_created_is_dead_lettered_without_a_handler_call() -> None:
    channel = Channel()
    router = Router()

    def handler(_envelope: dict[str, object]) -> DeliveryResult:
        raise AssertionError("OrderCreated must not be applied")

    settle_delivery(channel, 7, _body("OrderCreated", "PENDING"), handler, router=router, routing_key="order.created")

    assert channel.acked == [7]
    assert channel.nacked == []
    assert router.dead == ["unknown-event-type"]
    assert router.retries == []


def test_odoo_outage_schedules_retry_then_acks() -> None:
    channel = Channel()
    router = Router()

    def handler(_envelope: dict[str, object]) -> DeliveryResult:
        return DeliveryResult(DeliveryOutcome.TRANSIENT, "odoo-unavailable")

    settle_delivery(
        channel,
        7,
        _body("OrderConfirmed", "CONFIRMED"),
        handler,
        router=router,
        routing_key="order.confirmed",
    )

    assert router.retries == [1]
    assert router.dead == []
    assert channel.acked == [7]
    assert channel.nacked == []

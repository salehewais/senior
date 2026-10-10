"""Projection rules against SQLite. No Docker and no broker."""

from __future__ import annotations

import json
import uuid

from django.test import TestCase

from projections.domain.apply import apply_envelope
from projections.domain.envelope import ParsedEnvelope, inspect_envelope
from projections.domain.outcomes import REASON_DUPLICATE, REASON_STALE_SNAPSHOT, REASON_VERSION_GAP, Outcome
from projections.httpapi.queries import orders_summary, revenue_report
from projections.messaging.delivery import settle_delivery
from projections.models import OrderProjection, PaymentProjection, ProcessedEvent, ProductProjection


def apply_body(body: dict[str, object]):
    inspected = inspect_envelope(json.dumps(body).encode("utf-8"))
    assert isinstance(inspected, ParsedEnvelope)
    return apply_envelope(inspected)


def envelope(event_type: str, aggregate_id: uuid.UUID, payload: dict[str, object], **overrides: object) -> dict:
    body: dict[str, object] = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": "2026-10-08T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": str(aggregate_id),
        "correlation_id": str(uuid.uuid4()),
        "causation_id": str(uuid.uuid4()),
        "version": 1,
        "payload": payload,
    }
    body.update(overrides)
    return body


def order_payload(order_id: uuid.UUID, *, status: str, version: int, total: int = 3000) -> dict[str, object]:
    customer_id = uuid.uuid4()
    product_id = uuid.uuid4()
    payload: dict[str, object] = {
        "order_id": str(order_id),
        "status": status,
        "aggregate_version": version,
    }
    if status in {"PENDING", "CONFIRMED"}:
        payload["customer_id"] = str(customer_id)
        payload["items"] = [
            {
                "product_id": str(product_id),
                "sku": "MUG-01",
                "quantity": 2,
                "unit_price": {"amount_minor": total // 2, "currency": "USD"},
            }
        ]
        payload["total"] = {"amount_minor": total, "currency": "USD"}
    return payload


class FakeChannel:
    def __init__(self) -> None:
        self.acked: list[int] = []
        self.nacked: list[tuple[int, bool]] = []

    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None:
        del multiple
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None:
        del multiple
        self.nacked.append((delivery_tag, requeue))


class FakeRouter:
    def __init__(self) -> None:
        self.retries: list[int] = []
        self.dead: list[str] = []

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        del body, original_routing_key
        self.retries.append(attempt)
        self.reasons = reason

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None:
        del body, original_routing_key, retry_count
        self.dead.append(reason)


class ProjectionTests(TestCase):
    def test_order_confirmed_updates_the_projection_and_the_summary(self) -> None:
        order_id = uuid.uuid4()
        created = envelope("OrderCreated", order_id, order_payload(order_id, status="PENDING", version=1, total=5000))
        confirmed_payload = order_payload(order_id, status="CONFIRMED", version=2, total=5000)
        confirmed_payload["customer_id"] = created["payload"]["customer_id"]
        confirmed = envelope(
            "OrderConfirmed",
            order_id,
            confirmed_payload,
            occurred_at="2026-10-08T12:05:00Z",
        )
        self.assertEqual(apply_body(created).outcome, Outcome.SUCCESS)
        result = apply_body(confirmed)
        self.assertEqual(result.outcome, Outcome.SUCCESS)
        row = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(row.status, "CONFIRMED")
        self.assertEqual(row.aggregate_version, 2)
        self.assertEqual(row.total_amount_minor, 5000)
        summary = orders_summary()
        self.assertEqual(summary["as_of"], "2026-10-08T12:05:00Z")
        self.assertEqual(
            summary["by_status"],
            [{"status": "CONFIRMED", "count": 1, "total": {"amount_minor": 5000, "currency": "USD"}}],
        )

    def test_duplicate_event_id_does_not_double_the_count(self) -> None:
        """Two workers, or one redelivery, apply a given event_id once."""
        order_id = uuid.uuid4()
        created = envelope("OrderCreated", order_id, order_payload(order_id, status="PENDING", version=1))
        first = apply_body(created)
        second = apply_body(created)
        self.assertEqual(first.outcome, Outcome.SUCCESS)
        self.assertEqual(second.reason, REASON_DUPLICATE)
        self.assertEqual(OrderProjection.objects.count(), 1)
        self.assertEqual(ProcessedEvent.objects.count(), 1)
        summary = orders_summary()
        self.assertEqual(summary["by_status"][0]["count"], 1)

    def test_older_product_snapshot_is_ignored(self) -> None:
        product_id = uuid.uuid4()
        newer = envelope(
            "ProductUpdated",
            product_id,
            {
                "product_id": str(product_id),
                "sku": "MUG-01",
                "name": "New mug",
                "unit_price": {"amount_minor": 1800, "currency": "USD"},
                "active": True,
                "aggregate_version": 3,
            },
            occurred_at="2026-10-08T13:00:00Z",
        )
        older = envelope(
            "ProductUpdated",
            product_id,
            {
                "product_id": str(product_id),
                "sku": "MUG-01",
                "name": "Old mug",
                "unit_price": {"amount_minor": 1500, "currency": "USD"},
                "active": True,
                "aggregate_version": 1,
            },
            occurred_at="2026-10-08T11:00:00Z",
        )
        self.assertEqual(apply_body(newer).outcome, Outcome.SUCCESS)
        stale = apply_body(older)
        self.assertEqual(stale.outcome, Outcome.SUCCESS)
        self.assertEqual(stale.reason, REASON_STALE_SNAPSHOT)
        row = ProductProjection.objects.get(product_id=product_id)
        self.assertEqual(row.name, "New mug")
        self.assertEqual(row.unit_price_amount_minor, 1800)
        self.assertEqual(row.aggregate_version, 3)

    def test_skipped_order_version_is_not_applied_and_is_a_retry(self) -> None:
        order_id = uuid.uuid4()
        created = envelope("OrderCreated", order_id, order_payload(order_id, status="PENDING", version=1))
        self.assertEqual(apply_body(created).outcome, Outcome.SUCCESS)
        skipped_payload = order_payload(order_id, status="CONFIRMED", version=3)
        skipped_payload["customer_id"] = created["payload"]["customer_id"]
        skipped = envelope("OrderConfirmed", order_id, skipped_payload, occurred_at="2026-10-08T12:05:00Z")
        channel = FakeChannel()
        router = FakeRouter()
        settle_delivery(
            channel,
            9,
            json.dumps(skipped).encode(),
            apply_envelope,
            router=router,
            property_message_id="amqp-says-something-else",
        )
        self.assertEqual(channel.acked, [9])
        self.assertEqual(channel.nacked, [])
        self.assertEqual(router.retries, [1])
        self.assertEqual(router.dead, [])
        self.assertEqual(router.reasons, REASON_VERSION_GAP)
        row = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(row.status, "PENDING")
        self.assertEqual(row.aggregate_version, 1)
        self.assertEqual(ProcessedEvent.objects.count(), 1)

    def test_payment_confirmed_feeds_revenue_without_changing_order_status(self) -> None:
        order_id = uuid.uuid4()
        created = envelope("OrderCreated", order_id, order_payload(order_id, status="PENDING", version=1, total=5000))
        confirmed_payload = order_payload(order_id, status="CONFIRMED", version=2, total=5000)
        confirmed_payload["customer_id"] = created["payload"]["customer_id"]
        confirmed = envelope("OrderConfirmed", order_id, confirmed_payload)
        payment = envelope(
            "PaymentConfirmed",
            order_id,
            {
                "order_id": str(order_id),
                "payment_reference": "pay_123",
                "amount": {"amount_minor": 3000, "currency": "USD"},
                "aggregate_version": 3,
            },
            occurred_at="2026-10-08T12:09:00Z",
        )
        self.assertEqual(apply_body(created).outcome, Outcome.SUCCESS)
        self.assertEqual(apply_body(confirmed).outcome, Outcome.SUCCESS)
        self.assertEqual(apply_body(payment).outcome, Outcome.SUCCESS)
        self.assertEqual(OrderProjection.objects.get(order_id=order_id).status, "CONFIRMED")
        stored = PaymentProjection.objects.get(order_id=order_id)
        self.assertEqual(stored.outcome, "confirmed")
        self.assertEqual(stored.payment_reference, "pay_123")
        report = revenue_report()
        self.assertEqual(report["as_of"], "2026-10-08T12:09:00Z")
        self.assertEqual(report["confirmed_totals"], [{"amount_minor": 3000, "currency": "USD"}])
        self.assertEqual(report["confirmed_count"], 1)
        self.assertEqual(report["failed_count"], 0)

    def test_unknown_event_type_is_dead_lettered_and_not_applied(self) -> None:
        body = envelope("OrderCreated", uuid.uuid4(), {"aggregate_version": 1})
        body["event_type"] = "OrderCorrected"
        channel = FakeChannel()
        router = FakeRouter()
        settle_delivery(channel, 3, json.dumps(body).encode(), apply_envelope, router=router)
        self.assertEqual(router.dead, ["unknown-event-type"])
        self.assertEqual(router.retries, [])
        self.assertEqual(channel.nacked, [])
        self.assertEqual(OrderProjection.objects.count(), 0)

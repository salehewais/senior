"""The confirm commit is readable before any reporting consumer runs."""

from __future__ import annotations

import json

from tests.support.consistency_export import export_completed_saga_order, export_confirmed_order


def test_confirmed_order_row_and_outbox_share_one_snapshot() -> None:
    exported = export_confirmed_order()
    encoded = json.dumps(exported)
    loaded = json.loads(encoded)
    order = loaded["order"]
    saga = loaded["saga"]
    events = loaded["events"]

    assert order["status"] == "CONFIRMED"
    assert order["version"] == 2
    assert order["saga_status"] == "STARTED"
    assert order["total_amount_minor"] == 3000
    assert order["currency"] == "USD"
    assert saga["status"] == "STARTED"
    assert saga["order_id"] == order["order_id"]
    assert [event["event_type"] for event in events] == ["OrderCreated", "OrderConfirmed"]
    assert events[0]["payload"]["status"] == "PENDING"
    assert events[0]["payload"]["aggregate_version"] == 1
    assert events[1]["payload"]["status"] == "CONFIRMED"
    assert events[1]["payload"]["aggregate_version"] == 2
    assert events[1]["payload"]["order_id"] == order["order_id"]
    assert events[1]["aggregate_id"] == order["order_id"]


def test_completed_saga_stays_confirmed_and_records_payment_before_any_projection() -> None:
    exported = export_completed_saga_order()
    order = exported["order"]
    saga = exported["saga"]
    events = exported["events"]
    assert isinstance(order, dict)
    assert isinstance(saga, dict)
    assert isinstance(events, list)
    types = [event["event_type"] for event in events]

    assert order["status"] == "CONFIRMED"
    assert order["version"] == 3
    assert order["saga_status"] == "COMPLETED"
    assert saga["status"] == "COMPLETED"
    assert saga["order_id"] == order["order_id"]
    assert types == ["OrderCreated", "OrderConfirmed", "PaymentConfirmed"]
    assert "OrderDelivered" not in types
    payment = events[2]["payload"]
    assert payment["order_id"] == order["order_id"]
    assert payment["aggregate_version"] == 3
    assert payment["amount"]["amount_minor"] == order["total_amount_minor"]
    assert payment["amount"]["currency"] == order["currency"]

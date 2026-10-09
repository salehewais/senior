"""Saga commands are idempotent. OrderConfirmed does not create the sales order."""

from __future__ import annotations

from commerce_erp.commands import (
    CANCEL_ERP_ORDER,
    CREATE_ERP_ORDER,
    RELEASE_INVENTORY,
    RESERVE_INVENTORY,
    apply_command,
    lookup_reservation,
    lookup_sales_order,
)
from commerce_erp.confirmed import ConfirmedOrder

ORDER_ID = "018f1c2a-1111-7c11-8a22-222222222222"
CUSTOMER_ID = "018f1c2a-3333-7c11-8a22-444444444444"
PRODUCT_ID = "018f1c2a-5555-7c11-8a22-666666666666"
EVENT_ID = "018f1c2a-7b3d-7c11-8a22-111111111111"
SECOND_EVENT_ID = "018f1c2a-7b3d-7c11-8a22-999999999999"


class MemoryCommands:
    def __init__(self) -> None:
        self.events: set[str] = set()
        self.keys: dict[str, object] = {}
        self.reservations: dict[str, tuple[str, bool]] = {}
        self.orders: dict[str, ConfirmedOrder] = {}
        self.cancelled: set[str] = set()

    def has_event(self, event_id: str) -> bool:
        return event_id in self.events

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None:
        del event_type, aggregate_id
        self.events.add(event_id)

    def result_for_key(self, idempotency_key: str):
        return self.keys.get(idempotency_key)

    def remember_key(self, idempotency_key: str, result) -> None:
        self.keys[idempotency_key] = result

    def find_reservation(self, order_id: str):
        return self.reservations.get(order_id)

    def save_reservation(self, order_id: str, reservation_id: str, *, released: bool) -> None:
        self.reservations[order_id] = (reservation_id, released)

    def has_order(self, order_id: str) -> bool:
        return order_id in self.orders and order_id not in self.cancelled

    def create_sales_order(self, order: ConfirmedOrder) -> None:
        if order.order_id in self.orders:
            raise AssertionError("second sales order")
        self.orders[order.order_id] = order

    def cancel_sales_order(self, order_id: str) -> bool:
        if order_id not in self.orders or order_id in self.cancelled:
            return False
        self.cancelled.add(order_id)
        return True


def _command(event_type: str, payload: dict, *, event_id: str = EVENT_ID) -> dict:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": "2026-10-08T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": ORDER_ID,
        "correlation_id": CUSTOMER_ID,
        "causation_id": EVENT_ID,
        "version": 1,
        "payload": payload,
    }


def _reserve_payload() -> dict:
    return {
        "order_id": ORDER_ID,
        "idempotency_key": f"{ORDER_ID}:reserve",
        "lines": [{"product_id": PRODUCT_ID, "sku": "MUG-01", "quantity": 2}],
    }


def _create_payload() -> dict:
    return {
        "order_id": ORDER_ID,
        "customer_id": CUSTOMER_ID,
        "idempotency_key": f"{ORDER_ID}:create_erp",
        "items": [
            {
                "product_id": PRODUCT_ID,
                "sku": "MUG-01",
                "quantity": 2,
                "unit_price": {"amount_minor": 1500, "currency": "USD"},
            }
        ],
        "total": {"amount_minor": 3000, "currency": "USD"},
    }


def test_an_event_arrives_twice() -> None:
    store = MemoryCommands()
    first = apply_command(store, _command(RESERVE_INVENTORY, _reserve_payload()))
    second = apply_command(store, _command(RESERVE_INVENTORY, _reserve_payload(), event_id=SECOND_EVENT_ID))
    created = apply_command(
        store,
        _command(CREATE_ERP_ORDER, _create_payload(), event_id="018f1c2a-7b3d-7c11-8a22-aaaaaaaaaaaa"),
    )
    again = apply_command(
        store,
        _command(CREATE_ERP_ORDER, _create_payload(), event_id="018f1c2a-7b3d-7c11-8a22-bbbbbbbbbbbb"),
    )

    assert first.outcome == "succeeded"
    assert second.outcome == "duplicate"
    assert second.reference == first.reference
    assert list(store.reservations) == [ORDER_ID]
    assert created.outcome == "succeeded"
    assert again.outcome == "duplicate"
    assert list(store.orders) == [ORDER_ID]
    assert store.orders[ORDER_ID].lines[0].sku == "MUG-01"
    assert store.orders[ORDER_ID].lines[0].quantity == 2


def test_release_and_cancel_are_idempotent() -> None:
    store = MemoryCommands()
    apply_command(store, _command(RESERVE_INVENTORY, _reserve_payload()))
    apply_command(store, _command(CREATE_ERP_ORDER, _create_payload(), event_id=SECOND_EVENT_ID))
    release = {
        "order_id": ORDER_ID,
        "reservation_id": f"rsv-{ORDER_ID}",
        "idempotency_key": f"{ORDER_ID}:release",
    }
    cancel = {"order_id": ORDER_ID, "idempotency_key": f"{ORDER_ID}:cancel_erp"}
    first_release = apply_command(
        store,
        _command(RELEASE_INVENTORY, release, event_id="018f1c2a-7b3d-7c11-8a22-cccccccccccc"),
    )
    second_release = apply_command(
        store,
        _command(RELEASE_INVENTORY, release, event_id="018f1c2a-7b3d-7c11-8a22-dddddddddddd"),
    )
    first_cancel = apply_command(
        store,
        _command(CANCEL_ERP_ORDER, cancel, event_id="018f1c2a-7b3d-7c11-8a22-eeeeeeeeeeee"),
    )
    second_cancel = apply_command(
        store,
        _command(CANCEL_ERP_ORDER, cancel, event_id="018f1c2a-7b3d-7c11-8a22-ffffffffffff"),
    )

    assert first_release.outcome == "succeeded"
    assert second_release.outcome == "duplicate"
    assert store.reservations[ORDER_ID][1] is True
    assert first_cancel.outcome == "succeeded"
    assert second_cancel.outcome == "duplicate"
    assert lookup_reservation(store, ORDER_ID).outcome == "absent"
    assert lookup_sales_order(store, ORDER_ID).outcome == "absent"


def test_unknown_timeout_looks_up_before_a_second_reserve() -> None:
    """A timeout is unknown. Look the reservation up. A second command does not hold stock twice."""

    store = MemoryCommands()
    first = apply_command(store, _command(RESERVE_INVENTORY, _reserve_payload()))
    found = lookup_reservation(store, ORDER_ID)
    replay = apply_command(
        store,
        _command(RESERVE_INVENTORY, _reserve_payload(), event_id=SECOND_EVENT_ID),
    )
    retry_payload = _reserve_payload()
    retry_payload["idempotency_key"] = f"{ORDER_ID}:reserve-retry"
    retry_payload["lines"] = [{"product_id": PRODUCT_ID, "sku": "MUG-01", "quantity": 9}]
    retry = apply_command(
        store,
        _command(RESERVE_INVENTORY, retry_payload, event_id="018f1c2a-7b3d-7c11-8a22-aaaaaaaaaaaa"),
    )

    assert first.outcome == "succeeded"
    assert found.outcome == "succeeded"
    assert found.reference == first.reference == f"rsv-{ORDER_ID}"
    assert replay.outcome == "duplicate"
    assert retry.outcome == "succeeded"
    assert retry.reason == "already-reserved"
    assert retry.reference == first.reference
    assert list(store.reservations) == [ORDER_ID]
    assert store.reservations[ORDER_ID] == (f"rsv-{ORDER_ID}", False)


def test_lookup_finds_a_reservation_before_a_second_insert() -> None:
    store = MemoryCommands()
    apply_command(store, _command(RESERVE_INVENTORY, _reserve_payload()))
    found = lookup_reservation(store, ORDER_ID)
    assert found.outcome == "succeeded"
    assert found.reference == f"rsv-{ORDER_ID}"
    assert lookup_reservation(store, "018f1c2a-1111-7c11-8a22-000000000000").outcome == "absent"


def test_order_confirmed_is_not_a_command() -> None:
    store = MemoryCommands()
    result = apply_command(store, _command("OrderConfirmed", _create_payload()))
    assert result.outcome == "permanent"
    assert result.reason == "not-saga-command"
    assert store.orders == {}

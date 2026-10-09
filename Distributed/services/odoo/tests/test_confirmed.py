"""Duplicate OrderConfirmed does not create a second sales order. OrderCreated never does."""

from __future__ import annotations

from commerce_erp.confirmed import ApplyResult, ConfirmedOrder, apply_confirmed_order, partner_values, product_values

EVENT_ID = "018f1c2a-7b3d-7c11-8a22-111111111111"
OTHER_EVENT_ID = "018f1c2a-7b3d-7c11-8a22-999999999999"
ORDER_ID = "018f1c2a-1111-7c11-8a22-222222222222"
CUSTOMER_ID = "018f1c2a-3333-7c11-8a22-444444444444"
PRODUCT_ID = "018f1c2a-5555-7c11-8a22-666666666666"
CORRELATION_ID = "018f1c2a-3333-7c11-8a22-444444444444"
CAUSATION_ID = "018f1c2a-5555-7c11-8a22-666666666666"


class MemoryErp:
    def __init__(self) -> None:
        self.events: set[str] = set()
        self.orders: dict[str, ConfirmedOrder] = {}

    def has_event(self, event_id: str) -> bool:
        return event_id in self.events

    def has_order(self, order_id: str) -> bool:
        return order_id in self.orders

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None:
        self.events.add(event_id)

    def create_sales_order(self, order: ConfirmedOrder) -> None:
        if order.order_id in self.orders:
            raise AssertionError("second sales order")
        self.orders[order.order_id] = order


def _envelope(event_type: str = "OrderConfirmed", *, event_id: str = EVENT_ID, status: str = "CONFIRMED") -> dict:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": "2026-10-08T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": ORDER_ID,
        "correlation_id": CORRELATION_ID,
        "causation_id": CAUSATION_ID,
        "version": 1,
        "payload": {
            "order_id": ORDER_ID,
            "customer_id": CUSTOMER_ID,
            "status": status,
            "items": [
                {
                    "product_id": PRODUCT_ID,
                    "sku": "MUG-01",
                    "quantity": 2,
                    "unit_price": {"amount_minor": 1500, "currency": "USD"},
                }
            ],
            "total": {"amount_minor": 3000, "currency": "USD"},
            "aggregate_version": 2,
            "password_hash": "argon2$not-for-odoo",
        },
    }


def test_duplicate_order_confirmed_creates_one_sales_order() -> None:
    erp = MemoryErp()
    first = apply_confirmed_order(erp, _envelope())
    second = apply_confirmed_order(erp, _envelope())
    third = apply_confirmed_order(erp, _envelope(event_id=OTHER_EVENT_ID))

    assert first == ApplyResult("created", "")
    assert second == ApplyResult("duplicate", "event_id")
    assert third == ApplyResult("duplicate", "order_id")
    assert list(erp.orders) == [ORDER_ID]
    assert erp.orders[ORDER_ID].lines[0].sku == "MUG-01"
    assert erp.orders[ORDER_ID].lines[0].quantity == 2
    assert erp.orders[ORDER_ID].lines[0].amount_minor == 1500
    assert OTHER_EVENT_ID in erp.events


def test_order_created_is_not_a_sales_order() -> None:
    erp = MemoryErp()
    result = apply_confirmed_order(erp, _envelope("OrderCreated", status="PENDING"))

    assert result == ApplyResult("permanent", "not-order-confirmed")
    assert erp.orders == {}
    assert erp.events == set()


def test_partner_and_product_values_omit_password_hashes() -> None:
    envelope = _envelope()
    erp = MemoryErp()
    apply_confirmed_order(erp, envelope)
    order = erp.orders[ORDER_ID]
    partner = partner_values(order.customer_id)
    product = product_values(order.lines[0])

    assert "password" not in partner
    assert "password_hash" not in partner
    assert partner["commerce_customer_id"] == CUSTOMER_ID
    assert product["default_code"] == "MUG-01"
    assert product["commerce_product_id"] == PRODUCT_ID
    assert "argon2$not-for-odoo" not in repr(partner)
    assert "argon2$not-for-odoo" not in repr(product)

"""Turn one OrderConfirmed envelope into a recorded delivery, not a sales order.

ERP creation is the CreateErpOrder command. Reporting still consumes
OrderConfirmed. This function stays so a duplicate event_id is remembered
and a second delivery does not become a second code path.

OrderCreated is a permanent rejection. This function does not open
order_db, and it does not copy password hashes onto the partner.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Protocol

EVENT_ORDER_CONFIRMED = "OrderConfirmed"
REASON_MALFORMED = "malformed-envelope"
REASON_NOT_CONFIRMED = "not-order-confirmed"
REASON_INVALID = "invalid-order-payload"
SCHEMA_VERSION = 1

_SKU = re.compile(r"^.{1,64}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True, slots=True)
class OrderLine:
    product_id: str
    sku: str
    quantity: int
    amount_minor: int
    currency: str


@dataclass(frozen=True, slots=True)
class ConfirmedOrder:
    event_id: str
    event_type: str
    order_id: str
    customer_id: str
    correlation_id: str
    causation_id: str
    aggregate_version: int
    lines: tuple[OrderLine, ...]
    total_amount_minor: int
    total_currency: str


@dataclass(frozen=True, slots=True)
class PermanentRejection:
    reason: str


@dataclass(frozen=True, slots=True)
class ApplyResult:
    outcome: str
    reason: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"outcome": self.outcome, "reason": self.reason}


class ErpStore(Protocol):
    def has_event(self, event_id: str) -> bool:
        """True when this event_id was already committed."""

    def has_order(self, order_id: str) -> bool:
        """True when a sales order already stores this commerce order id."""

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None:
        """Insert the processed-event row in the caller's transaction."""

    def create_sales_order(self, order: ConfirmedOrder) -> None:
        """Create one sales order from the payload. No second lookup of order_db."""


def apply_confirmed_order(store: ErpStore, envelope: object) -> ApplyResult:
    """Remember OrderConfirmed without creating a sales order.

    CreateErpOrder is the only path that calls create_sales_order. A duplicate
    event_id is still a duplicate. The caller commits the processed-event row
    and acks only after that commit.
    """

    parsed = parse_order_confirmed(envelope)
    if isinstance(parsed, PermanentRejection):
        return ApplyResult("permanent", parsed.reason)
    if store.has_event(parsed.event_id):
        return ApplyResult("duplicate", "event_id")
    store.remember_event(parsed.event_id, parsed.event_type, parsed.order_id)
    return ApplyResult("ignored", "create-erp-order-command")


def parse_order_confirmed(envelope: object) -> ConfirmedOrder | PermanentRejection:
    """Read a sales order from the envelope alone.

    Any event type other than OrderConfirmed is rejected before lines are
    read, so OrderCreated cannot become an ERP document.
    """

    if not isinstance(envelope, dict):
        return PermanentRejection(REASON_MALFORMED)
    event_type = envelope.get("event_type")
    if event_type != EVENT_ORDER_CONFIRMED:
        return PermanentRejection(REASON_NOT_CONFIRMED)
    version = envelope.get("version")
    if isinstance(version, bool) or version != SCHEMA_VERSION:
        return PermanentRejection(REASON_MALFORMED)
    event_id = _uuid(envelope.get("event_id"))
    aggregate_id = _uuid(envelope.get("aggregate_id"))
    correlation_id = _uuid(envelope.get("correlation_id"))
    causation_id = _uuid(envelope.get("causation_id"))
    payload = envelope.get("payload")
    if (
        event_id is None
        or aggregate_id is None
        or correlation_id is None
        or causation_id is None
        or not isinstance(payload, dict)
    ):
        return PermanentRejection(REASON_MALFORMED)
    if payload.get("status") != "CONFIRMED":
        return PermanentRejection(REASON_INVALID)
    order_id = _uuid(payload.get("order_id"))
    customer_id = _uuid(payload.get("customer_id"))
    aggregate_version = payload.get("aggregate_version")
    total = _money(payload.get("total"))
    lines = _lines(payload.get("items"))
    if (
        order_id is None
        or customer_id is None
        or order_id != aggregate_id
        or total is None
        or lines is None
        or isinstance(aggregate_version, bool)
        or not isinstance(aggregate_version, int)
        or aggregate_version < 1
    ):
        return PermanentRejection(REASON_INVALID)
    return ConfirmedOrder(
        event_id=event_id,
        event_type=EVENT_ORDER_CONFIRMED,
        order_id=order_id,
        customer_id=customer_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
        aggregate_version=aggregate_version,
        lines=lines,
        total_amount_minor=total[0],
        total_currency=total[1],
    )


def partner_values(customer_id: str) -> dict[str, object]:
    """Partner fields taken from the commerce customer id. No password, no email."""

    return {
        "name": f"Commerce {customer_id}",
        "commerce_customer_id": customer_id,
        "ref": customer_id,
        "customer_rank": 1,
    }


def product_values(line: OrderLine) -> dict[str, object]:
    """Product fields taken from the order line. The stable external id is the sku."""

    return {
        "name": line.sku,
        "default_code": line.sku,
        "commerce_product_id": line.product_id,
        "type": "consu",
        "is_storable": True,
        "list_price": line.amount_minor / 100.0,
        "sale_ok": True,
    }


def xmlid_for_customer(customer_id: str) -> str:
    return "customer_" + customer_id.replace("-", "_")


def xmlid_for_sku(sku: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in sku).strip("_") or "item"
    return ("sku_" + cleaned)[:64]


def _lines(value: object) -> tuple[OrderLine, ...] | None:
    if not isinstance(value, list) or not value:
        return None
    lines: list[OrderLine] = []
    for item in value:
        if not isinstance(item, dict):
            return None
        product_id = _uuid(item.get("product_id"))
        sku = item.get("sku")
        quantity = item.get("quantity")
        money = _money(item.get("unit_price"))
        if (
            product_id is None
            or not isinstance(sku, str)
            or _SKU.fullmatch(sku) is None
            or isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 1
            or money is None
        ):
            return None
        lines.append(
            OrderLine(
                product_id=product_id,
                sku=sku,
                quantity=quantity,
                amount_minor=money[0],
                currency=money[1],
            )
        )
    return tuple(lines)


def _money(value: object) -> tuple[int, str] | None:
    if not isinstance(value, dict):
        return None
    amount = value.get("amount_minor")
    currency = value.get("currency")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        return None
    if not isinstance(currency, str) or _CURRENCY.fullmatch(currency) is None:
        return None
    return amount, currency


def _uuid(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None

"""Idempotent ReserveInventory, ReleaseInventory, CreateErpOrder, and CancelErpOrder.

A timeout at the sender is not a failure here. The sender looks the row up
before it publishes the command again. This module also looks the row up
before it inserts, so a late duplicate does not reserve twice or create a
second sales order.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from commerce_erp.confirmed import (
    REASON_INVALID,
    REASON_MALFORMED,
    ConfirmedOrder,
    PermanentRejection,
    parse_order_confirmed,
)

RESERVE_INVENTORY = "ReserveInventory"
RELEASE_INVENTORY = "ReleaseInventory"
CREATE_ERP_ORDER = "CreateErpOrder"
CANCEL_ERP_ORDER = "CancelErpOrder"
COMMAND_TYPES = frozenset(
    {RESERVE_INVENTORY, RELEASE_INVENTORY, CREATE_ERP_ORDER, CANCEL_ERP_ORDER}
)
REASON_NOT_COMMAND = "not-saga-command"


@dataclass(frozen=True, slots=True)
class CommandResult:
    outcome: str
    reason: str = ""
    reference: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"outcome": self.outcome, "reason": self.reason, "reference": self.reference}


class CommandStore(Protocol):
    def has_event(self, event_id: str) -> bool: ...

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None: ...

    def result_for_key(self, idempotency_key: str) -> CommandResult | None: ...

    def remember_key(self, idempotency_key: str, result: CommandResult) -> None: ...

    def find_reservation(self, order_id: str) -> tuple[str, bool] | None:
        """Return (reservation_id, released) or None when this order was never reserved."""

    def save_reservation(self, order_id: str, reservation_id: str, *, released: bool) -> None: ...

    def has_order(self, order_id: str) -> bool: ...

    def create_sales_order(self, order: ConfirmedOrder) -> None: ...

    def cancel_sales_order(self, order_id: str) -> bool:
        """Cancel the sales order. Return False when there is nothing to cancel."""


def apply_command(store: CommandStore, envelope: object) -> CommandResult:
    parsed = _envelope(envelope)
    if isinstance(parsed, PermanentRejection):
        return CommandResult("permanent", parsed.reason)
    event_id, event_type, order_id, idempotency_key, body = parsed
    if store.has_event(event_id):
        return CommandResult("duplicate", "event_id")
    prior = store.result_for_key(idempotency_key)
    if prior is not None:
        store.remember_event(event_id, event_type, order_id)
        return CommandResult("duplicate", "idempotency_key", prior.reference)
    if event_type == RESERVE_INVENTORY:
        result = _reserve(store, order_id, body)
    elif event_type == RELEASE_INVENTORY:
        result = _release(store, order_id)
    elif event_type == CREATE_ERP_ORDER:
        result = _create(store, envelope, order_id)
    else:
        result = _cancel(store, order_id)
    if result.outcome == "permanent":
        return result
    store.remember_event(event_id, event_type, order_id)
    store.remember_key(idempotency_key, result)
    return result


def lookup_reservation(store: CommandStore, order_id: str) -> CommandResult:
    found = store.find_reservation(order_id)
    if found is None or found[1]:
        return CommandResult("absent", "not-reserved")
    return CommandResult("succeeded", "", found[0])


def lookup_sales_order(store: CommandStore, order_id: str) -> CommandResult:
    if store.has_order(order_id):
        return CommandResult("succeeded", "", order_id)
    return CommandResult("absent", "not-created")


def _reserve(store: CommandStore, order_id: str, body: dict[str, object]) -> CommandResult:
    lines = body.get("lines")
    if not isinstance(lines, list) or not lines:
        return CommandResult("permanent", REASON_INVALID)
    found = store.find_reservation(order_id)
    if found is not None and not found[1]:
        return CommandResult("succeeded", "already-reserved", found[0])
    reservation_id = f"rsv-{order_id}"
    store.save_reservation(order_id, reservation_id, released=False)
    return CommandResult("succeeded", "", reservation_id)


def _release(store: CommandStore, order_id: str) -> CommandResult:
    found = store.find_reservation(order_id)
    if found is None or found[1]:
        return CommandResult("succeeded", "absent", found[0] if found else "")
    store.save_reservation(order_id, found[0], released=True)
    return CommandResult("succeeded", "", found[0])


def _create(store: CommandStore, envelope: object, order_id: str) -> CommandResult:
    if store.has_order(order_id):
        return CommandResult("succeeded", "already-created", order_id)
    sales = _sales_order(envelope)
    if isinstance(sales, PermanentRejection):
        return CommandResult("permanent", sales.reason)
    store.create_sales_order(sales)
    return CommandResult("succeeded", "", order_id)


def _cancel(store: CommandStore, order_id: str) -> CommandResult:
    if not store.has_order(order_id):
        return CommandResult("succeeded", "absent", "")
    cancelled = store.cancel_sales_order(order_id)
    if not cancelled:
        return CommandResult("succeeded", "already-cancelled", order_id)
    return CommandResult("succeeded", "", order_id)


def _sales_order(envelope: object) -> ConfirmedOrder | PermanentRejection:
    if not isinstance(envelope, dict):
        return PermanentRejection(REASON_MALFORMED)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        return PermanentRejection(REASON_MALFORMED)
    synthetic = dict(envelope)
    synthetic["event_type"] = "OrderConfirmed"
    synthetic_payload = dict(payload)
    synthetic_payload["status"] = "CONFIRMED"
    if "aggregate_version" not in synthetic_payload:
        synthetic_payload["aggregate_version"] = 1
    synthetic["payload"] = synthetic_payload
    return parse_order_confirmed(synthetic)


def _envelope(
    envelope: object,
) -> tuple[str, str, str, str, dict[str, object]] | PermanentRejection:
    if not isinstance(envelope, dict):
        return PermanentRejection(REASON_MALFORMED)
    event_type = envelope.get("event_type")
    if event_type not in COMMAND_TYPES:
        return PermanentRejection(REASON_NOT_COMMAND)
    event_id = envelope.get("event_id")
    aggregate_id = envelope.get("aggregate_id")
    payload = envelope.get("payload")
    if not isinstance(event_id, str) or not isinstance(aggregate_id, str) or not isinstance(payload, dict):
        return PermanentRejection(REASON_MALFORMED)
    order_id = payload.get("order_id")
    idempotency_key = payload.get("idempotency_key")
    if (
        not isinstance(order_id, str)
        or order_id != aggregate_id
        or not isinstance(idempotency_key, str)
        or not idempotency_key
    ):
        return PermanentRejection(REASON_INVALID)
    if event_type == CREATE_ERP_ORDER:
        items = payload.get("items")
        if not isinstance(items, list):
            return PermanentRejection(REASON_INVALID)
    return event_id, event_type, order_id, idempotency_key, payload

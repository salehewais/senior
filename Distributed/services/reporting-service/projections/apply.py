"""Project one accepted envelope into reporting_db.

The processed_events insert and the projection write commit together.
A version gap rolls that transaction back and asks for a retry.
An older product, customer, or inventory snapshot is stored as seen and
does not overwrite the newer row.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from projections.envelope import (
    AGGREGATE_TYPE,
    CANCEL_REASONS,
    EXPECTED_STATUS,
    ORDER_STREAM,
    PAYMENT_FAILURE_REASONS,
    SNAPSHOT_EVENTS,
    ParsedEnvelope,
    aggregate_version,
    inspect_envelope,
)
from projections.models import (
    CustomerProjection,
    InventoryProjection,
    OrderItemProjection,
    OrderProjection,
    PaymentProjection,
    ProcessedEvent,
    ProductProjection,
    ProjectionVersion,
)
from projections.outcomes import (
    REASON_DUPLICATE,
    REASON_INVALID_PAYLOAD,
    REASON_STALE_ORDER_VERSION,
    REASON_STALE_SNAPSHOT,
    REASON_VERSION_GAP,
    ApplyResult,
    Outcome,
    PermanentFailure,
    VersionGap,
)


def apply_envelope(envelope: dict[str, object]) -> ApplyResult:
    """Apply one body. The caller acks only after this returns."""

    try:
        parsed = _require_parsed(envelope)
        with transaction.atomic():
            return _apply(parsed)
    except VersionGap:
        return ApplyResult(Outcome.RETRY, REASON_VERSION_GAP)
    except PermanentFailure as exc:
        return ApplyResult(Outcome.PERMANENT, exc.reason)


def _require_parsed(envelope: dict[str, object]) -> ParsedEnvelope:
    inspected = inspect_envelope(json.dumps(envelope).encode("utf-8"))
    if not isinstance(inspected, ParsedEnvelope):
        raise PermanentFailure(inspected.reason)
    return inspected


def _apply(parsed: ParsedEnvelope) -> ApplyResult:
    payload = parsed.body.get("payload")
    if not isinstance(payload, dict):
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    if ProcessedEvent.objects.filter(event_id=parsed.event_id).exists():
        return ApplyResult(Outcome.SUCCESS, REASON_DUPLICATE)

    incoming = aggregate_version(payload)
    aggregate_type = AGGREGATE_TYPE[parsed.event_type]
    current = _locked_version(aggregate_type, parsed.aggregate_id)
    stored = current.aggregate_version if current is not None else 0

    if parsed.event_type in ORDER_STREAM:
        if incoming > stored + 1:
            raise VersionGap()
        if stored > 0 and incoming <= stored:
            raise PermanentFailure(REASON_STALE_ORDER_VERSION)
    elif parsed.event_type in SNAPSHOT_EVENTS and stored > 0 and incoming <= stored:
        if _insert_processed(parsed):
            return ApplyResult(Outcome.SUCCESS, REASON_DUPLICATE)
        return ApplyResult(Outcome.SUCCESS, REASON_STALE_SNAPSHOT)

    if _insert_processed(parsed):
        return ApplyResult(Outcome.SUCCESS, REASON_DUPLICATE)

    _write(parsed, payload, incoming)
    _save_version(current, aggregate_type, parsed.aggregate_id, incoming)
    return ApplyResult(Outcome.SUCCESS)


def _insert_processed(parsed: ParsedEnvelope) -> bool:
    """Return True when event_id was already committed. Nested savepoint keeps the outer transaction usable."""

    try:
        with transaction.atomic():
            ProcessedEvent.objects.create(
                event_id=parsed.event_id,
                event_type=parsed.event_type,
                aggregate_id=parsed.aggregate_id,
                processed_at=timezone.now(),
            )
    except IntegrityError:
        return True
    return False


def _locked_version(aggregate_type: str, aggregate_id: uuid.UUID) -> ProjectionVersion | None:
    query = ProjectionVersion.objects.filter(aggregate_type=aggregate_type, aggregate_id=aggregate_id)
    if connection.features.has_select_for_update:
        query = query.select_for_update()
    return query.first()


def _save_version(
    current: ProjectionVersion | None,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    incoming: int,
) -> None:
    if current is None:
        try:
            with transaction.atomic():
                ProjectionVersion.objects.create(
                    aggregate_type=aggregate_type,
                    aggregate_id=aggregate_id,
                    aggregate_version=incoming,
                )
        except IntegrityError as exc:
            raise VersionGap() from exc
        return
    current.aggregate_version = incoming
    current.save(update_fields=["aggregate_version"])


def _write(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    event_type = parsed.event_type
    if event_type in EXPECTED_STATUS:
        _write_order(parsed, payload, incoming, EXPECTED_STATUS[event_type])
        return
    if event_type == "PaymentConfirmed":
        _write_payment_confirmed(parsed, payload, incoming)
        return
    if event_type == "PaymentFailed":
        _write_payment_failed(parsed, payload, incoming)
        return
    if event_type in {"ProductCreated", "ProductUpdated"}:
        _write_product(parsed, payload, incoming)
        return
    if event_type == "CustomerUpdated":
        _write_customer(parsed, payload, incoming)
        return
    if event_type == "InventoryUpdated":
        _write_inventory(parsed, payload, incoming)
        return
    raise PermanentFailure(REASON_INVALID_PAYLOAD)


def _write_order(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int, status: str) -> None:
    if payload.get("status") != status:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    order_id = _same_id(parsed, payload.get("order_id"))
    order = OrderProjection.objects.filter(order_id=order_id).first()
    if order is None:
        order = OrderProjection(
            order_id=order_id,
            customer_id=None,
            status=status,
            total_amount_minor=0,
            currency="",
            aggregate_version=incoming,
            occurred_at=parsed.occurred_at,
        )
    customer_raw = payload.get("customer_id")
    if customer_raw is not None:
        customer_id = _uuid(customer_raw)
        if customer_id is None:
            raise PermanentFailure(REASON_INVALID_PAYLOAD)
        order.customer_id = customer_id
    if "total" in payload:
        amount, currency = _money(payload.get("total"))
        order.total_amount_minor = amount
        order.currency = currency
    if status == "CANCELLED":
        reason = payload.get("reason")
        if reason not in CANCEL_REASONS:
            raise PermanentFailure(REASON_INVALID_PAYLOAD)
        order.cancel_reason = reason
    if status == "SHIPPED":
        tracking = payload.get("tracking_reference")
        if tracking is not None and not isinstance(tracking, str):
            raise PermanentFailure(REASON_INVALID_PAYLOAD)
        order.tracking_reference = tracking
    if status == "PENDING" or (status == "CONFIRMED" and "items" in payload):
        items = _items(payload.get("items"), required=status == "PENDING")
    else:
        items = None
    if status == "PENDING" and order.customer_id is None:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    order.status = status
    order.aggregate_version = incoming
    order.occurred_at = parsed.occurred_at
    order.save()
    if items is not None and (status == "PENDING" or items):
        order.items.all().delete()
        OrderItemProjection.objects.bulk_create(
            [
                OrderItemProjection(
                    order=order,
                    position=index,
                    product_id=item["product_id"],
                    sku=item["sku"],
                    quantity=item["quantity"],
                    unit_price_amount_minor=item["amount_minor"],
                    currency=item["currency"],
                )
                for index, item in enumerate(items)
            ]
        )


def _write_payment_confirmed(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    order_id = _same_id(parsed, payload.get("order_id"))
    reference = payload.get("payment_reference")
    if not isinstance(reference, str) or not reference:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    amount, currency = _money(payload.get("amount"))
    PaymentProjection.objects.update_or_create(
        order_id=order_id,
        defaults={
            "outcome": "confirmed",
            "payment_reference": reference,
            "amount_minor": amount,
            "currency": currency,
            "reason_code": "",
            "aggregate_version": incoming,
            "occurred_at": parsed.occurred_at,
        },
    )


def _write_payment_failed(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    order_id = _same_id(parsed, payload.get("order_id"))
    reason = payload.get("reason_code")
    if reason not in PAYMENT_FAILURE_REASONS:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    PaymentProjection.objects.update_or_create(
        order_id=order_id,
        defaults={
            "outcome": "failed",
            "payment_reference": "",
            "amount_minor": None,
            "currency": "",
            "reason_code": reason,
            "aggregate_version": incoming,
            "occurred_at": parsed.occurred_at,
        },
    )


def _write_product(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    product_id = _same_id(parsed, payload.get("product_id"))
    amount, currency = _money(payload.get("unit_price"))
    sku = _text(payload.get("sku"))
    name = _text(payload.get("name"))
    active = payload.get("active")
    if not isinstance(active, bool):
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    ProductProjection.objects.update_or_create(
        product_id=product_id,
        defaults={
            "sku": sku,
            "name": name,
            "unit_price_amount_minor": amount,
            "currency": currency,
            "active": active,
            "aggregate_version": incoming,
            "occurred_at": parsed.occurred_at,
        },
    )


def _write_customer(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    customer_id = _same_id(parsed, payload.get("customer_id"))
    email = _text(payload.get("email"))
    display_name = _text(payload.get("display_name"))
    CustomerProjection.objects.update_or_create(
        customer_id=customer_id,
        defaults={
            "email": email,
            "display_name": display_name,
            "aggregate_version": incoming,
            "occurred_at": parsed.occurred_at,
        },
    )


def _write_inventory(parsed: ParsedEnvelope, payload: dict[str, Any], incoming: int) -> None:
    product_id = _same_id(parsed, payload.get("product_id"))
    sku = _text(payload.get("sku"))
    warehouse = _text(payload.get("warehouse_code"))
    on_hand = _stock(payload.get("quantity_on_hand"))
    reserved = _stock(payload.get("quantity_reserved"))
    InventoryProjection.objects.update_or_create(
        product_id=product_id,
        defaults={
            "sku": sku,
            "quantity_on_hand": on_hand,
            "quantity_reserved": reserved,
            "warehouse_code": warehouse,
            "aggregate_version": incoming,
            "occurred_at": parsed.occurred_at,
        },
    )


def _items(value: object, *, required: bool) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    if required and not value:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    items: list[dict[str, object]] = []
    for raw in value:
        if not isinstance(raw, dict):
            raise PermanentFailure(REASON_INVALID_PAYLOAD)
        product_id = _uuid(raw.get("product_id"))
        quantity = raw.get("quantity")
        if product_id is None or isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise PermanentFailure(REASON_INVALID_PAYLOAD)
        amount, currency = _money(raw.get("unit_price"))
        items.append(
            {
                "product_id": product_id,
                "sku": _text(raw.get("sku")),
                "quantity": quantity,
                "amount_minor": amount,
                "currency": currency,
            }
        )
    return items


def _money(value: object) -> tuple[int, str]:
    if not isinstance(value, dict):
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    amount = value.get("amount_minor")
    currency = value.get("currency")
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return amount, currency.upper()


def _same_id(parsed: ParsedEnvelope, value: object) -> uuid.UUID:
    parsed_id = _uuid(value)
    if parsed_id is None or parsed_id != parsed.aggregate_id:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return parsed_id


def _uuid(value: object) -> uuid.UUID | None:
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def _text(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return value


def _stock(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return value

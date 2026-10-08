"""Error envelope shared with the order service, and report JSON helpers."""

from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime

from django.db.models import Max, Q
from django.http import HttpRequest, JsonResponse

from projections.models import InventoryProjection, OrderProjection, PaymentProjection


def correlation_id_of(request: HttpRequest) -> str:
    existing = getattr(request, "correlation_id", None)
    if isinstance(existing, str) and existing:
        return existing
    return str(uuid.uuid4())


def error_body(*, code: str, message: str, correlation_id: str, details: list[dict[str, str]] | None = None):
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id,
            "details": details or [],
        }
    }


def error_response(
    status: int,
    code: str,
    message: str,
    correlation_id: str,
    details: list[dict[str, str]] | None = None,
) -> JsonResponse:
    return JsonResponse(
        error_body(code=code, message=message, correlation_id=correlation_id, details=details),
        status=status,
    )


def iso_z(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    text = value.astimezone(UTC).isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text


def parse_limit(raw: str | None) -> int:
    if raw is None or raw == "":
        return 20
    if not raw.isdigit():
        raise ValueError("limit")
    value = int(raw)
    if value < 1 or value > 100:
        raise ValueError("limit")
    return value


def encode_cursor(occurred_at: datetime, entity_id: uuid.UUID) -> str:
    stamp = iso_z(occurred_at)
    raw = f"{stamp}|{entity_id}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def decode_cursor(raw: str) -> tuple[datetime, uuid.UUID]:
    try:
        text = base64.urlsafe_b64decode(raw.encode("ascii")).decode("utf-8")
        stamp, entity = text.split("|", 1)
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return parsed, uuid.UUID(entity)
    except (ValueError, UnicodeError):
        raise ValueError("cursor") from None


def orders_summary() -> dict[str, object]:
    as_of = OrderProjection.objects.aggregate(newest=Max("occurred_at"))["newest"]
    buckets: dict[tuple[str, str], list[int]] = {}
    for status, currency, amount in OrderProjection.objects.values_list("status", "currency", "total_amount_minor"):
        key = (status, currency)
        bucket = buckets.setdefault(key, [0, 0])
        bucket[0] += 1
        bucket[1] += int(amount)
    by_status = [
        {
            "status": status,
            "count": count,
            "total": {"amount_minor": total, "currency": currency},
        }
        for (status, currency), (count, total) in sorted(buckets.items())
    ]
    return {"as_of": iso_z(as_of), "by_status": by_status}


def orders_page(*, limit: int, cursor: str | None) -> dict[str, object]:
    as_of = OrderProjection.objects.aggregate(newest=Max("occurred_at"))["newest"]
    query = OrderProjection.objects.prefetch_related("items").order_by("-occurred_at", "-order_id")
    if cursor:
        stamp, entity_id = decode_cursor(cursor)
        query = query.filter(Q(occurred_at__lt=stamp) | Q(occurred_at=stamp, order_id__lt=entity_id))
    rows = list(query[: limit + 1])
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit and page:
        last = page[-1]
        next_cursor = encode_cursor(last.occurred_at, last.order_id)
    return {
        "as_of": iso_z(as_of),
        "items": [_order_json(row) for row in page],
        "next_cursor": next_cursor,
    }


def inventory_page(*, limit: int, cursor: str | None) -> dict[str, object]:
    as_of = InventoryProjection.objects.aggregate(newest=Max("occurred_at"))["newest"]
    query = InventoryProjection.objects.order_by("-occurred_at", "-product_id")
    if cursor:
        stamp, entity_id = decode_cursor(cursor)
        query = query.filter(Q(occurred_at__lt=stamp) | Q(occurred_at=stamp, product_id__lt=entity_id))
    rows = list(query[: limit + 1])
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit and page:
        last = page[-1]
        next_cursor = encode_cursor(last.occurred_at, last.product_id)
    return {
        "as_of": iso_z(as_of),
        "items": [
            {
                "product_id": str(row.product_id),
                "sku": row.sku,
                "quantity_on_hand": row.quantity_on_hand,
                "quantity_reserved": row.quantity_reserved,
                "warehouse_code": row.warehouse_code,
                "aggregate_version": row.aggregate_version,
            }
            for row in page
        ],
        "next_cursor": next_cursor,
    }


def revenue_report() -> dict[str, object]:
    as_of = PaymentProjection.objects.aggregate(newest=Max("occurred_at"))["newest"]
    totals: dict[str, int] = {}
    confirmed = 0
    failed = 0
    for outcome, currency, amount in PaymentProjection.objects.values_list("outcome", "currency", "amount_minor"):
        if outcome == "confirmed" and amount is not None and currency:
            confirmed += 1
            totals[currency] = totals.get(currency, 0) + int(amount)
        elif outcome == "failed":
            failed += 1
    return {
        "as_of": iso_z(as_of),
        "confirmed_totals": [
            {"amount_minor": amount, "currency": currency} for currency, amount in sorted(totals.items())
        ],
        "confirmed_count": confirmed,
        "failed_count": failed,
    }


def _order_json(row: OrderProjection) -> dict[str, object]:
    return {
        "order_id": str(row.order_id),
        "customer_id": str(row.customer_id) if row.customer_id else None,
        "status": row.status,
        "total": {"amount_minor": row.total_amount_minor, "currency": row.currency},
        "cancel_reason": row.cancel_reason,
        "tracking_reference": row.tracking_reference,
        "aggregate_version": row.aggregate_version,
        "items": [
            {
                "product_id": str(item.product_id),
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": {"amount_minor": item.unit_price_amount_minor, "currency": item.currency},
            }
            for item in row.items.all()
        ],
    }

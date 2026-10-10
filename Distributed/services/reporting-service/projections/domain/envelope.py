"""Read the outbox envelope. The JSON body wins over AMQP properties."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from projections.domain.outcomes import (
    REASON_INVALID_PAYLOAD,
    REASON_MALFORMED,
    REASON_UNKNOWN_TYPE,
    REASON_UNKNOWN_VERSION,
    PermanentFailure,
)

UNDERSTOOD_SCHEMA_VERSION = 1

ORDER_EVENTS = frozenset(
    {
        "OrderCreated",
        "OrderConfirmed",
        "OrderCancelled",
        "OrderProcessingStarted",
        "OrderShipped",
        "OrderDelivered",
    }
)
PAYMENT_EVENTS = frozenset({"PaymentConfirmed", "PaymentFailed"})
SNAPSHOT_EVENTS = frozenset(
    {
        "ProductCreated",
        "ProductUpdated",
        "CustomerUpdated",
        "InventoryUpdated",
    }
)
ACCEPTED_EVENT_TYPES = ORDER_EVENTS | PAYMENT_EVENTS | SNAPSHOT_EVENTS

ORDER_STREAM = ORDER_EVENTS | PAYMENT_EVENTS

AGGREGATE_TYPE = {
    "OrderCreated": "order",
    "OrderConfirmed": "order",
    "OrderCancelled": "order",
    "OrderProcessingStarted": "order",
    "OrderShipped": "order",
    "OrderDelivered": "order",
    "PaymentConfirmed": "order",
    "PaymentFailed": "order",
    "ProductCreated": "product",
    "ProductUpdated": "product",
    "CustomerUpdated": "customer",
    "InventoryUpdated": "inventory",
}

EXPECTED_STATUS = {
    "OrderCreated": "PENDING",
    "OrderConfirmed": "CONFIRMED",
    "OrderCancelled": "CANCELLED",
    "OrderProcessingStarted": "PROCESSING",
    "OrderShipped": "SHIPPED",
    "OrderDelivered": "DELIVERED",
}

CANCEL_REASONS = frozenset({"customer_request", "staff_request"})
PAYMENT_FAILURE_REASONS = frozenset({"declined", "timeout", "circuit_open", "provider_error"})


@dataclass(frozen=True, slots=True)
class EnvelopeRejection:
    reason: str


@dataclass(frozen=True, slots=True)
class ParsedEnvelope:
    event_id: uuid.UUID
    event_type: str
    aggregate_id: uuid.UUID
    occurred_at: datetime
    correlation_id: str
    body: dict[str, object]


def inspect_envelope(body: bytes) -> ParsedEnvelope | EnvelopeRejection:
    """Identity comes from the JSON body. AMQP message_id and type are ignored."""

    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return EnvelopeRejection(REASON_MALFORMED)
    if not isinstance(parsed, dict):
        return EnvelopeRejection(REASON_MALFORMED)
    event_id = _uuid_field(parsed.get("event_id"))
    aggregate_id = _uuid_field(parsed.get("aggregate_id"))
    event_type = parsed.get("event_type")
    version = parsed.get("version")
    if event_id is None or aggregate_id is None or not isinstance(event_type, str) or not event_type:
        return EnvelopeRejection(REASON_MALFORMED)
    if isinstance(version, bool) or not isinstance(version, int):
        return EnvelopeRejection(REASON_MALFORMED)
    if version != UNDERSTOOD_SCHEMA_VERSION:
        return EnvelopeRejection(REASON_UNKNOWN_VERSION)
    if event_type not in ACCEPTED_EVENT_TYPES:
        return EnvelopeRejection(REASON_UNKNOWN_TYPE)
    occurred_at = _timestamp(parsed.get("occurred_at"))
    if occurred_at is None:
        return EnvelopeRejection(REASON_MALFORMED)
    payload = parsed.get("payload")
    if not isinstance(payload, dict):
        return EnvelopeRejection(REASON_MALFORMED)
    correlation = parsed.get("correlation_id")
    correlation_id = str(correlation) if isinstance(correlation, str) else "missing"
    return ParsedEnvelope(
        event_id=event_id,
        event_type=event_type,
        aggregate_id=aggregate_id,
        occurred_at=occurred_at,
        correlation_id=correlation_id,
        body=parsed,
    )


def aggregate_version(payload: dict[str, object]) -> int:
    value = payload.get("aggregate_version")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return value


def _uuid_field(value: object) -> uuid.UUID | None:
    if isinstance(value, uuid.UUID):
        return value
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)

"""Decide how one delivery is settled. This module does not import a broker.

Delivery is at least once. The consumer records event_id, then acks. A second
delivery of the same event_id acks and does not run the effect again.

A transient failure is scheduled onto the next retry attempt. The sixth
failure, and any permanent failure, is a dead letter. Permanent means the
bytes cannot succeed no matter how often they are tried: malformed JSON, an
event type this consumer does not handle, or a schema version it does not
understand. A handler exception is transient. Older inventory snapshots are
neither: they are acked and ignored.

The attempt count lives in the x-retry-count header the worker sets when it
publishes to commerce.retry. The body remains the source of truth when an
AMQP property disagrees with it.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

# docs/rabbitmq.md: five delayed retries, then the dead-letter queue.
MAX_AUTOMATIC_RETRIES = 5

HEADER_RETRY_COUNT = "x-retry-count"
HEADER_ORIGINAL_ROUTING_KEY = "x-original-routing-key"
HEADER_FAILURE_REASON = "x-failure-reason"

# Schema version this process can apply. A higher version is a permanent failure.
UNDERSTOOD_SCHEMA_VERSION = 1

CONSUMER_ORDER_INVENTORY = "order-inventory"

# The order service applies InventoryUpdated only. Reporting owns the other types.
INVENTORY_EVENT_TYPES = frozenset({"InventoryUpdated"})

CATALOG_EVENT_TYPES = frozenset(
    {
        "OrderCreated",
        "OrderConfirmed",
        "OrderCancelled",
        "OrderProcessingStarted",
        "OrderShipped",
        "OrderDelivered",
        "ProductCreated",
        "ProductUpdated",
        "CustomerUpdated",
        "PaymentConfirmed",
        "PaymentFailed",
        "InventoryUpdated",
    }
)

REASON_MALFORMED = "malformed-envelope"
REASON_UNKNOWN_TYPE = "unknown-event-type"
REASON_UNKNOWN_VERSION = "unknown-schema-version"
REASON_RETRIES_EXHAUSTED = "retries-exhausted"
REASON_DUPLICATE = "duplicate"
REASON_HANDLER_FAILED = "handler-failed"


class DeliveryOutcome(Enum):
    SUCCESS = "success"
    TRANSIENT = "transient"
    PERMANENT = "permanent"


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    outcome: DeliveryOutcome
    reason: str = ""


class PermanentMessageError(Exception):
    """The payload can never be applied. Retrying it would waste the budget."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class ParsedEnvelope:
    event_id: uuid.UUID
    event_type: str
    version: int
    aggregate_id: uuid.UUID
    body: dict[str, object]


@dataclass(frozen=True, slots=True)
class EnvelopeRejection:
    reason: str


@dataclass(frozen=True, slots=True)
class ProcessedEvent:
    event_id: uuid.UUID
    event_type: str
    aggregate_id: uuid.UUID
    processed_at: datetime
    consumer_name: str


class Ledger(Protocol):
    def insert_if_new(self, record: ProcessedEvent) -> bool:
        """Insert event_id. Return False when this consumer already applied it."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class FailureRouter(Protocol):
    def schedule_retry(
        self,
        *,
        attempt: int,
        body: bytes,
        original_routing_key: str,
        reason: str,
    ) -> None:
        """Publish to the attempt's retry queue. The caller acks after this returns."""

    def dead_letter(
        self,
        *,
        body: bytes,
        original_routing_key: str,
        reason: str,
        retry_count: int,
    ) -> None:
        """Publish to this consumer's dead-letter queue. The caller acks after this returns."""


def inspect_envelope(
    body: bytes,
    *,
    accepted_event_types: frozenset[str],
) -> ParsedEnvelope | EnvelopeRejection:
    """Read identity from the JSON body. AMQP properties are not consulted."""

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
    if event_type not in accepted_event_types:
        return EnvelopeRejection(REASON_UNKNOWN_TYPE)
    return ParsedEnvelope(
        event_id=event_id,
        event_type=event_type,
        version=version,
        aggregate_id=aggregate_id,
        body=parsed,
    )


def retries_already_scheduled(headers: Mapping[str, object] | None) -> int | EnvelopeRejection:
    """How many delayed retries have already been published for this body.

    Absent means this is the first delivery. A garbage count is permanent:
    treating it as zero would start the ladder over forever.
    """

    if not headers or HEADER_RETRY_COUNT not in headers or headers[HEADER_RETRY_COUNT] is None:
        return 0
    raw = headers[HEADER_RETRY_COUNT]
    if isinstance(raw, str) and raw.isdigit():
        raw = int(raw)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        return EnvelopeRejection(REASON_MALFORMED)
    return raw


def next_retry_attempt(retries_already_scheduled: int) -> int | None:
    """Attempt number to schedule, or None when the failure belongs on the DLQ."""

    if retries_already_scheduled >= MAX_AUTOMATIC_RETRIES:
        return None
    return retries_already_scheduled + 1


def original_routing_key(headers: Mapping[str, object] | None, delivery_routing_key: str) -> str:
    """Keep the first routing key. A retry return is delivered under the retry key."""

    if headers:
        stored = headers.get(HEADER_ORIGINAL_ROUTING_KEY)
        if isinstance(stored, str) and stored:
            return stored
    return delivery_routing_key


def apply_once(ledger: Ledger, record: ProcessedEvent, effect: Callable[[], None]) -> DeliveryResult:
    """Run effect only when event_id was not already committed.

    The insert and the effect commit together. A duplicate acks without
    calling effect. A failure rolls back so a retry can try the insert again.
    """

    try:
        inserted = ledger.insert_if_new(record)
    except Exception:
        ledger.rollback()
        return DeliveryResult(DeliveryOutcome.TRANSIENT, REASON_HANDLER_FAILED)
    if not inserted:
        ledger.rollback()
        return DeliveryResult(DeliveryOutcome.SUCCESS, REASON_DUPLICATE)
    try:
        effect()
    except PermanentMessageError as exc:
        ledger.rollback()
        return DeliveryResult(DeliveryOutcome.PERMANENT, exc.reason)
    except Exception:
        ledger.rollback()
        return DeliveryResult(DeliveryOutcome.TRANSIENT, REASON_HANDLER_FAILED)
    try:
        ledger.commit()
    except Exception:
        ledger.rollback()
        return DeliveryResult(DeliveryOutcome.TRANSIENT, REASON_HANDLER_FAILED)
    return DeliveryResult(DeliveryOutcome.SUCCESS)


def coerce_handler_result(value: DeliveryResult | DeliveryOutcome | None) -> DeliveryResult:
    if value is None or value is DeliveryOutcome.SUCCESS:
        return DeliveryResult(DeliveryOutcome.SUCCESS)
    if isinstance(value, DeliveryOutcome):
        return DeliveryResult(value)
    if isinstance(value, DeliveryResult):
        return value
    raise TypeError("A handler must return a delivery outcome or None.")


def _uuid_field(value: object) -> uuid.UUID | None:
    if isinstance(value, uuid.UUID):
        return value
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None

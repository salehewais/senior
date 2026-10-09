"""Settle one delivery from q.odoo.order-confirmed.

Ack after the handler returns success. The handler's success means Odoo has
committed the sales order and the processed-event row. A transient failure
is published to commerce.retry and then acked. requeue=true is not used.
A message that is not OrderConfirmed is a permanent failure.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

logger = logging.getLogger("commerce_erp.consumer")

MAX_AUTOMATIC_RETRIES = 5
HEADER_RETRY_COUNT = "x-retry-count"
HEADER_ORIGINAL_ROUTING_KEY = "x-original-routing-key"
HEADER_FAILURE_REASON = "x-failure-reason"
UNDERSTOOD_SCHEMA_VERSION = 1
ACCEPTED_EVENT_TYPES = frozenset({"OrderConfirmed"})

REASON_MALFORMED = "malformed-envelope"
REASON_UNKNOWN_TYPE = "unknown-event-type"
REASON_UNKNOWN_VERSION = "unknown-schema-version"
REASON_RETRIES_EXHAUSTED = "retries-exhausted"
REASON_HANDLER_FAILED = "handler-failed"


class DeliveryOutcome(Enum):
    SUCCESS = "success"
    TRANSIENT = "transient"
    PERMANENT = "permanent"


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    outcome: DeliveryOutcome
    reason: str = ""


@dataclass(frozen=True, slots=True)
class ParsedEnvelope:
    event_id: uuid.UUID
    event_type: str
    body: dict[str, object]


@dataclass(frozen=True, slots=True)
class EnvelopeRejection:
    reason: str


class DeliveryChannel(Protocol):
    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None: ...

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None: ...


class FailureRouter(Protocol):
    def schedule_retry(
        self,
        *,
        attempt: int,
        body: bytes,
        original_routing_key: str,
        reason: str,
    ) -> None: ...

    def dead_letter(
        self,
        *,
        body: bytes,
        original_routing_key: str,
        reason: str,
        retry_count: int,
    ) -> None: ...


EventHandler = Callable[[dict[str, object]], DeliveryResult]


def inspect_envelope(body: bytes) -> ParsedEnvelope | EnvelopeRejection:
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
    return ParsedEnvelope(event_id=event_id, event_type=event_type, body=parsed)


def retries_already_scheduled(headers: Mapping[str, object] | None) -> int | EnvelopeRejection:
    if not headers or HEADER_RETRY_COUNT not in headers or headers[HEADER_RETRY_COUNT] is None:
        return 0
    raw = headers[HEADER_RETRY_COUNT]
    if isinstance(raw, str) and raw.isdigit():
        raw = int(raw)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        return EnvelopeRejection(REASON_MALFORMED)
    return raw


def next_retry_attempt(already: int) -> int | None:
    if already >= MAX_AUTOMATIC_RETRIES:
        return None
    return already + 1


def original_routing_key(headers: Mapping[str, object] | None, delivery_routing_key: str) -> str:
    if headers:
        stored = headers.get(HEADER_ORIGINAL_ROUTING_KEY)
        if isinstance(stored, str) and stored:
            return stored
    return delivery_routing_key


def settle_delivery(
    channel: DeliveryChannel,
    delivery_tag: int,
    body: bytes,
    handler: EventHandler,
    *,
    router: FailureRouter,
    headers: dict[str, object] | None = None,
    routing_key: str = "",
) -> None:
    """Ack, retry, or dead-letter. Never nack with requeue=true."""

    business_key = original_routing_key(headers, routing_key)
    scheduled = retries_already_scheduled(headers)
    if isinstance(scheduled, EnvelopeRejection):
        logger.error("permanent failure dead-lettered before handler reason=%s", scheduled.reason)
        _dead_letter(channel, delivery_tag, router, body, business_key, scheduled.reason, 0)
        return
    inspected = inspect_envelope(body)
    if isinstance(inspected, EnvelopeRejection):
        logger.error("permanent failure dead-lettered before handler reason=%s", inspected.reason)
        _dead_letter(channel, delivery_tag, router, body, business_key, inspected.reason, scheduled)
        return
    try:
        result = handler(inspected.body)
    except Exception as exc:
        logger.error(
            "consumer handler failed event_id=%s error_type=%s",
            inspected.event_id,
            type(exc).__name__,
        )
        result = DeliveryResult(DeliveryOutcome.TRANSIENT, REASON_HANDLER_FAILED)
    if result.outcome is DeliveryOutcome.SUCCESS:
        if result.reason == "duplicate":
            logger.info(
                "duplicate delivery acked without a second sales order event_id=%s",
                inspected.event_id,
            )
        channel.basic_ack(delivery_tag=delivery_tag)
        return
    if result.outcome is DeliveryOutcome.PERMANENT:
        logger.error(
            "permanent failure dead-lettered event_id=%s reason=%s",
            inspected.event_id,
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, result.reason or "permanent", scheduled)
        return
    attempt = next_retry_attempt(scheduled)
    if attempt is None:
        logger.error(
            "retries exhausted dead-lettered event_id=%s reason=%s",
            inspected.event_id,
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, REASON_RETRIES_EXHAUSTED, scheduled)
        return
    logger.error(
        "transient failure scheduled retry attempt=%s event_id=%s reason=%s",
        attempt,
        inspected.event_id,
        result.reason,
    )
    router.schedule_retry(
        attempt=attempt,
        body=body,
        original_routing_key=business_key,
        reason=result.reason or REASON_HANDLER_FAILED,
    )
    channel.basic_ack(delivery_tag=delivery_tag)


def _dead_letter(
    channel: DeliveryChannel,
    delivery_tag: int,
    router: FailureRouter,
    body: bytes,
    business_key: str,
    reason: str,
    retry_count: int,
) -> None:
    router.dead_letter(
        body=body,
        original_routing_key=business_key,
        reason=reason,
        retry_count=retry_count,
    )
    channel.basic_ack(delivery_tag=delivery_tag)


def _uuid_field(value: object) -> uuid.UUID | None:
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None

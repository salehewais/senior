"""Ack, retry, or dead-letter one delivery.

Manual ack happens after the handler returns, which is after the projection
transaction commits. requeue=true is not used. A nack on the main queue would
drop the message, because that queue has no dead-letter argument.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping
from typing import Protocol

from projections.envelope import EnvelopeRejection, ParsedEnvelope, inspect_envelope
from projections.metrics import bounded_event_type, record_message
from projections.outcomes import (
    HEADER_ORIGINAL_ROUTING_KEY,
    HEADER_RETRY_COUNT,
    MAX_AUTOMATIC_RETRIES,
    REASON_HANDLER_FAILED,
    REASON_RETRIES_EXHAUSTED,
    ApplyResult,
    Outcome,
)
from projections.tracing import consumer_span

logger = logging.getLogger("reporting.consumer")


class DeliveryChannel(Protocol):
    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None: ...

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None: ...


class FailureRouter(Protocol):
    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None: ...

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None: ...


Handler = Callable[[dict[str, object]], ApplyResult]


def retries_already_scheduled(headers: Mapping[str, object] | None) -> int | EnvelopeRejection:
    from projections.outcomes import REASON_MALFORMED

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
    handler: Handler,
    *,
    router: FailureRouter,
    headers: dict[str, object] | None = None,
    routing_key: str = "",
    property_message_id: str | None = None,
) -> None:
    """Ack after a committed apply. The body wins when AMQP properties disagree."""

    del property_message_id
    started = time.perf_counter()
    event_type = "unknown"
    processed = False
    failed = False
    retry = False
    dlq = False
    result_label = "error"
    try:
        business_key = original_routing_key(headers, routing_key)
        scheduled = retries_already_scheduled(headers)
        if isinstance(scheduled, EnvelopeRejection):
            logger.error("permanent failure dead-lettered before handler reason=%s", scheduled.reason)
            _dead_letter(channel, delivery_tag, router, body, business_key, scheduled.reason, 0)
            failed = True
            dlq = True
            return
        inspected = inspect_envelope(body)
        if isinstance(inspected, EnvelopeRejection):
            logger.error("permanent failure dead-lettered before handler reason=%s", inspected.reason)
            _dead_letter(channel, delivery_tag, router, body, business_key, inspected.reason, scheduled)
            failed = True
            dlq = True
            return
        event_type = inspected.event_type
        with consumer_span(headers, body, event_type=bounded_event_type(event_type)):
            processed, failed, retry, dlq, result_label = _apply(
                channel,
                delivery_tag,
                body,
                handler,
                router=router,
                business_key=business_key,
                scheduled=scheduled,
                inspected=inspected,
            )
    finally:
        record_message(
            event_type=event_type,
            seconds=time.perf_counter() - started,
            processed=processed,
            failed=failed,
            retry=retry,
            dlq=dlq,
            queue="q.reporting.projection",
            result=result_label,
        )


def _apply(
    channel: DeliveryChannel,
    delivery_tag: int,
    body: bytes,
    handler: Handler,
    *,
    router: FailureRouter,
    business_key: str,
    scheduled: int,
    inspected: ParsedEnvelope,
) -> tuple[bool, bool, bool, bool, str]:
    result = _run_handler(handler, inspected)
    if result.outcome is Outcome.SUCCESS:
        if result.reason:
            logger.info(
                "delivery acked event_id=%s event_type=%s correlation_id=%s reason=%s",
                inspected.event_id,
                inspected.event_type,
                inspected.correlation_id,
                result.reason,
            )
        if result.reason == "duplicate":
            label = "duplicate"
        elif result.reason == "stale":
            label = "stale"
        else:
            label = "applied"
        channel.basic_ack(delivery_tag=delivery_tag)
        return True, False, False, False, label
    if result.outcome is Outcome.PERMANENT:
        logger.error(
            "permanent failure dead-lettered event_id=%s correlation_id=%s reason=%s",
            inspected.event_id,
            inspected.correlation_id,
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, result.reason or "permanent", scheduled)
        return False, True, False, True, "error"
    attempt = next_retry_attempt(scheduled)
    if attempt is None:
        logger.error(
            "retries exhausted dead-lettered event_id=%s correlation_id=%s reason=%s",
            inspected.event_id,
            inspected.correlation_id,
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, REASON_RETRIES_EXHAUSTED, scheduled)
        return False, True, False, True, "error"
    logger.error(
        "transient failure scheduled retry attempt=%s event_id=%s correlation_id=%s reason=%s",
        attempt,
        inspected.event_id,
        inspected.correlation_id,
        result.reason,
    )
    router.schedule_retry(
        attempt=attempt,
        body=body,
        original_routing_key=business_key,
        reason=result.reason or REASON_HANDLER_FAILED,
    )
    channel.basic_ack(delivery_tag=delivery_tag)
    return False, True, True, False, "error"


def _run_handler(handler: Handler, inspected: ParsedEnvelope) -> ApplyResult:
    try:
        return handler(inspected.body)
    except Exception as exc:
        logger.error(
            "consumer handler failed correlation_id=%s event_id=%s error_type=%s",
            inspected.correlation_id,
            inspected.event_id,
            type(exc).__name__,
        )
        return ApplyResult(Outcome.RETRY, REASON_HANDLER_FAILED)


def _dead_letter(
    channel: DeliveryChannel,
    delivery_tag: int,
    router: FailureRouter,
    body: bytes,
    business_key: str,
    reason: str,
    retry_count: int,
) -> None:
    router.dead_letter(body=body, original_routing_key=business_key, reason=reason, retry_count=retry_count)
    channel.basic_ack(delivery_tag=delivery_tag)

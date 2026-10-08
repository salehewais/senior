"""One consumer. The process entrypoint listens on q.order.inventory.

That queue is the order service's queue: it receives InventoryUpdated.
q.reporting.projection belongs to reporting. The same settlement path can
serve either queue; pass the queue name and the event types that consumer
understands.

Ack happens only after the outcome is durable. Success and duplicates ack.
A transient failure is published to the next commerce.retry queue and then
acked, so the message is not dropped and not requeued onto the same queue.
A permanent failure (malformed envelope, unknown event type, schema version
this consumer does not understand, or a payload that can never apply) is
published to commerce.dlx immediately. The retry budget is not spent on it.
An unexpected handler exception is transient.

Shutdown stops the consume loop. The callback runs inside
process_data_events, so the delivery already in hand is settled before the
loop notices the stop. Then the channel and connection close. An unacked
delivery returns to the queue once, as a redelivery, which is not requeue=true
on a poison message.

Connect, declare, the failure publish, and the consumer idle wait are bounded.
Database calls on the inventory handler use the engine's connect timeout and
statement timeout.
"""

from __future__ import annotations

import logging
import signal
import threading
from collections.abc import Callable
from typing import Protocol

from sqlalchemy import text

from order_service.application.consuming import (
    CATALOG_EVENT_TYPES,
    INVENTORY_EVENT_TYPES,
    REASON_HANDLER_FAILED,
    REASON_RETRIES_EXHAUSTED,
    DeliveryOutcome,
    DeliveryResult,
    EnvelopeRejection,
    FailureRouter,
    coerce_handler_result,
    inspect_envelope,
    next_retry_attempt,
    original_routing_key,
    retries_already_scheduled,
)
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.messaging.connection import (
    broker_deadline,
    close_connection,
    open_connection,
)
from order_service.infrastructure.messaging.inventory_handler import InventoryUpdatedHandler
from order_service.infrastructure.messaging.retry import RepublishingRouter
from order_service.infrastructure.messaging.topology import (
    QUEUE_INVENTORY,
    QUEUE_REPORTING,
    TOPOLOGY_NAME,
    declare_topology,
)
from order_service.infrastructure.settings import Settings, get_settings

logger = logging.getLogger("order_service.consumer")

# docs/rabbitmq.md: start at 10. One consumer, not a throughput setting.
PREFETCH_COUNT = 10

EventHandler = Callable[[dict[str, object]], DeliveryResult | DeliveryOutcome | None]


class DeliveryChannel(Protocol):
    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None: ...

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None: ...


class LoggingEventHandler:
    """Structured log of the event type. The payload is omitted on purpose.

    This does not apply a projection. Pair it with apply_once when the effect
    must not run twice. The shipping process uses InventoryUpdatedHandler.
    """

    def __call__(self, envelope: dict[str, object]) -> DeliveryResult:
        logger.info(
            "consumed event_type=%s event_id=%s correlation_id=%s aggregate_id=%s",
            envelope.get("event_type"),
            envelope.get("event_id"),
            envelope.get("correlation_id"),
            envelope.get("aggregate_id"),
        )
        return DeliveryResult(DeliveryOutcome.SUCCESS)


def settle_delivery(
    channel: DeliveryChannel,
    delivery_tag: int,
    body: bytes,
    handler: EventHandler,
    *,
    router: FailureRouter,
    headers: dict[str, object] | None = None,
    routing_key: str = "",
    accepted_event_types: frozenset[str] = CATALOG_EVENT_TYPES,
    property_message_id: str | None = None,
) -> None:
    """Ack, retry, or dead-letter. Never nack with requeue=true.

    property_message_id is accepted so a caller can see it was not used.
    docs/events.md: if AMQP properties disagree with the body, the body wins.
    """

    del property_message_id
    business_key = original_routing_key(headers, routing_key)
    scheduled = retries_already_scheduled(headers)
    if isinstance(scheduled, EnvelopeRejection):
        logger.error("permanent failure dead-lettered before handler reason=%s", scheduled.reason)
        _dead_letter(channel, delivery_tag, router, body, business_key, scheduled.reason, 0)
        return
    inspected = inspect_envelope(body, accepted_event_types=accepted_event_types)
    if isinstance(inspected, EnvelopeRejection):
        logger.error("permanent failure dead-lettered before handler reason=%s", inspected.reason)
        _dead_letter(channel, delivery_tag, router, body, business_key, inspected.reason, scheduled)
        return
    try:
        result = coerce_handler_result(handler(inspected.body))
    except Exception as exc:
        logger.error(
            "consumer handler failed correlation_id=%s event_id=%s error_type=%s",
            inspected.body.get("correlation_id"),
            inspected.event_id,
            type(exc).__name__,
        )
        result = DeliveryResult(DeliveryOutcome.TRANSIENT, REASON_HANDLER_FAILED)
    if result.outcome is DeliveryOutcome.SUCCESS:
        if result.reason == "duplicate":
            logger.info(
                "duplicate delivery acked without a second effect event_id=%s event_type=%s",
                inspected.event_id,
                inspected.event_type,
            )
        channel.basic_ack(delivery_tag=delivery_tag)
        return
    if result.outcome is DeliveryOutcome.PERMANENT:
        logger.error(
            "permanent failure dead-lettered event_id=%s correlation_id=%s reason=%s",
            inspected.event_id,
            inspected.body.get("correlation_id"),
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, result.reason or "permanent", scheduled)
        return
    attempt = next_retry_attempt(scheduled)
    if attempt is None:
        logger.error(
            "retries exhausted dead-lettered event_id=%s correlation_id=%s reason=%s",
            inspected.event_id,
            inspected.body.get("correlation_id"),
            result.reason,
        )
        _dead_letter(channel, delivery_tag, router, body, business_key, REASON_RETRIES_EXHAUSTED, scheduled)
        return
    logger.error(
        "transient failure scheduled retry attempt=%s event_id=%s correlation_id=%s reason=%s",
        attempt,
        inspected.event_id,
        inspected.body.get("correlation_id"),
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
    router.dead_letter(body=body, original_routing_key=business_key, reason=reason, retry_count=retry_count)
    channel.basic_ack(delivery_tag=delivery_tag)


def _as_bytes(body: bytes | str) -> bytes:
    if isinstance(body, str):
        return body.encode("utf-8")
    return bytes(body)


def run_consumer(
    settings: Settings,
    handler: EventHandler,
    stop: threading.Event,
    *,
    queue_name: str = QUEUE_REPORTING,
    ready: threading.Event | None = None,
    accepted_event_types: frozenset[str] = CATALOG_EVENT_TYPES,
    router: FailureRouter | None = None,
) -> None:
    timeout = settings.rabbitmq_timeout_seconds
    failure_router = router if router is not None else RepublishingRouter(settings, queue_name)
    connection = open_connection(settings)
    try:
        with broker_deadline(connection, timeout):
            channel = connection.channel()
            declare_topology(channel)
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)

            def _on_message(ch, method, properties, body) -> None:
                header_map: dict[str, object] = {}
                if properties is not None and properties.headers:
                    header_map = dict(properties.headers)
                message_id = properties.message_id if properties is not None else None
                try:
                    settle_delivery(
                        ch,
                        method.delivery_tag,
                        _as_bytes(body),
                        handler,
                        router=failure_router,
                        headers=header_map,
                        routing_key=method.routing_key or "",
                        accepted_event_types=accepted_event_types,
                        property_message_id=message_id,
                    )
                except Exception as exc:
                    # Leave the delivery unacked. Closing the connection returns
                    # it once. requeue=true here would spin if the broker publish
                    # of the retry kept failing.
                    logger.error(
                        "settlement failed; shutting down so the delivery is redelivered "
                        "error_type=%s",
                        type(exc).__name__,
                    )
                    stop.set()

            consumer_tag = channel.basic_consume(
                queue=queue_name,
                on_message_callback=_on_message,
                auto_ack=False,
            )
        logger.info(
            "consumer started topology=%s queue=%s prefetch=%s",
            TOPOLOGY_NAME,
            queue_name,
            PREFETCH_COUNT,
        )
        if ready is not None:
            ready.set()
        while not stop.is_set():
            # time_limit is the idle wait. It returns so shutdown can be noticed.
            connection.process_data_events(time_limit=0.5)
        if channel.is_open:
            with broker_deadline(connection, timeout):
                channel.basic_cancel(consumer_tag)
    finally:
        close_connection(connection, timeout_seconds=timeout)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = get_settings()
    engine = make_engine(settings)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    handler = InventoryUpdatedHandler(make_session_factory(engine))
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_consumer(
        settings,
        handler,
        stop,
        queue_name=QUEUE_INVENTORY,
        accepted_event_types=INVENTORY_EVENT_TYPES,
    )


if __name__ == "__main__":
    main()

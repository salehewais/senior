"""Consume q.odoo.order-confirmed and apply it through Odoo's API.

    python -m commerce_erp.workers.consumer

Manual ack happens after Odoo returns. The module commits the sales order
and the processed-event row in one odoo_db transaction, then the RPC returns,
then this process acks. If this process dies after that commit and before
the ack, the redelivery hits the same event_id and does not create a second
sales order.

If Odoo is down, the delivery is published to commerce.retry and acked.
The order service is not on this path. Its outbox already holds OrderConfirmed,
and this queue holds the copy. FastAPI keeps serving checkout.

Connect, declare, the failure publish, the Odoo call, and the idle wait are
bounded. This process does not open order_db, reporting_db, or odoo_db.
"""

from __future__ import annotations

import logging
import signal
import threading

import pika

from commerce_erp.clients.odoo_api import OdooCallError, OdooClient
from commerce_erp.domain.commands import COMMAND_TYPES
from commerce_erp.messaging.broker import broker_deadline, close_connection, open_connection
from commerce_erp.messaging.consuming import (
    HEADER_FAILURE_REASON,
    HEADER_ORIGINAL_ROUTING_KEY,
    HEADER_RETRY_COUNT,
    DeliveryOutcome,
    DeliveryResult,
    settle_delivery,
)
from commerce_erp.messaging.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_RETRY,
    QUEUE_CANCEL_SALES_ORDER,
    QUEUE_CREATE_SALES_ORDER,
    QUEUE_ODOO_CONFIRMED,
    QUEUE_RELEASE,
    QUEUE_RESERVE,
    declare_topology,
    retry_routing_key,
)
from commerce_erp.settings import Settings

logger = logging.getLogger("commerce_erp.consumer")

PREFETCH_COUNT = 10


class OdooApplyHandler:
    def __init__(self, client: OdooClient) -> None:
        self._client = client

    def __call__(self, envelope: dict[str, object]) -> DeliveryResult:
        try:
            result = self._client.apply_order_confirmed(envelope)
        except OdooCallError as exc:
            logger.error(
                "odoo apply failed event_id=%s correlation_id=%s error=%s",
                envelope.get("event_id"),
                envelope.get("correlation_id"),
                exc,
            )
            return DeliveryResult(DeliveryOutcome.TRANSIENT, "odoo-unavailable")
        outcome = result.get("outcome")
        if outcome in {"created", "ignored"}:
            logger.info(
                "sales order created event_id=%s aggregate_id=%s",
                envelope.get("event_id"),
                envelope.get("aggregate_id"),
            )
            return DeliveryResult(DeliveryOutcome.SUCCESS)
        if outcome == "duplicate":
            return DeliveryResult(DeliveryOutcome.SUCCESS, "duplicate")
        if outcome == "permanent":
            reason = result.get("reason")
            return DeliveryResult(DeliveryOutcome.PERMANENT, reason if isinstance(reason, str) else "permanent")
        return DeliveryResult(DeliveryOutcome.TRANSIENT, "odoo-unexpected-result")


class CommandApplyHandler:
    def __init__(self, client: OdooClient) -> None:
        self._client = client

    def __call__(self, envelope: dict[str, object]) -> DeliveryResult:
        try:
            result = self._client.apply_command(envelope)
        except OdooCallError as exc:
            logger.error(
                "odoo command failed event_id=%s correlation_id=%s error=%s",
                envelope.get("event_id"),
                envelope.get("correlation_id"),
                exc,
            )
            return DeliveryResult(DeliveryOutcome.TRANSIENT, "odoo-unavailable")
        outcome = result.get("outcome")
        if outcome == "succeeded":
            return DeliveryResult(DeliveryOutcome.SUCCESS)
        if outcome == "duplicate":
            return DeliveryResult(DeliveryOutcome.SUCCESS, "duplicate")
        if outcome == "permanent":
            reason = result.get("reason")
            return DeliveryResult(DeliveryOutcome.PERMANENT, reason if isinstance(reason, str) else "permanent")
        if outcome == "failed":
            reason = result.get("reason")
            return DeliveryResult(DeliveryOutcome.PERMANENT, reason if isinstance(reason, str) else "failed")
        return DeliveryResult(DeliveryOutcome.TRANSIENT, "odoo-unexpected-result")


class RepublishingRouter:
    def __init__(self, settings: Settings, queue_name: str) -> None:
        self._settings = settings
        self._queue_name = queue_name

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        self._publish(
            exchange=EXCHANGE_COMMERCE_RETRY,
            routing_key=retry_routing_key(self._queue_name, attempt),
            body=body,
            headers={
                HEADER_RETRY_COUNT: attempt,
                HEADER_ORIGINAL_ROUTING_KEY: original_routing_key,
                HEADER_FAILURE_REASON: reason,
            },
        )

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None:
        self._publish(
            exchange=EXCHANGE_COMMERCE_DLX,
            routing_key=DLQ_ROUTING_KEY[self._queue_name],
            body=body,
            headers={
                HEADER_RETRY_COUNT: retry_count,
                HEADER_ORIGINAL_ROUTING_KEY: original_routing_key,
                HEADER_FAILURE_REASON: reason,
            },
        )

    def _publish(self, *, exchange: str, routing_key: str, body: bytes, headers: dict[str, object]) -> None:
        timeout = self._settings.rabbitmq_timeout_seconds
        connection = open_connection(self._settings.rabbitmq_url, timeout)
        try:
            with broker_deadline(connection, timeout):
                channel = connection.channel()
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        content_encoding="utf-8",
                        delivery_mode=pika.DeliveryMode.Persistent,
                        headers=headers,
                    ),
                    mandatory=True,
                )
        finally:
            close_connection(connection, timeout_seconds=timeout)


def run_consumer(settings: Settings, handler: OdooApplyHandler, stop: threading.Event) -> None:
    timeout = settings.rabbitmq_timeout_seconds
    command_handler = CommandApplyHandler(handler._client)
    connection = open_connection(settings.rabbitmq_url, timeout)
    try:
        with broker_deadline(connection, timeout):
            channel = connection.channel()
            declare_topology(channel)
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)
            consumer_tags = [
                _consume(channel, settings, stop, QUEUE_ODOO_CONFIRMED, handler, accepted=None),
                _consume(channel, settings, stop, QUEUE_RESERVE, command_handler, accepted=COMMAND_TYPES),
                _consume(channel, settings, stop, QUEUE_RELEASE, command_handler, accepted=COMMAND_TYPES),
                _consume(channel, settings, stop, QUEUE_CREATE_SALES_ORDER, command_handler, accepted=COMMAND_TYPES),
                _consume(channel, settings, stop, QUEUE_CANCEL_SALES_ORDER, command_handler, accepted=COMMAND_TYPES),
            ]
        logger.info("odoo consumer started queue=%s prefetch=%s", QUEUE_ODOO_CONFIRMED, PREFETCH_COUNT)
        while not stop.is_set():
            connection.process_data_events(time_limit=0.5)
        if channel.is_open:
            with broker_deadline(connection, timeout):
                for consumer_tag in consumer_tags:
                    channel.basic_cancel(consumer_tag)
    finally:
        close_connection(connection, timeout_seconds=timeout)


def _consume(channel, settings: Settings, stop: threading.Event, queue_name: str, handler, accepted):
    router = RepublishingRouter(settings, queue_name)

    def _on_message(ch, method, properties, body) -> None:
        header_map: dict[str, object] = {}
        if properties is not None and properties.headers:
            header_map = dict(properties.headers)
        raw = body.encode("utf-8") if isinstance(body, str) else bytes(body)
        try:
            settle_delivery(
                ch,
                method.delivery_tag,
                raw,
                handler,
                router=router,
                headers=header_map,
                routing_key=method.routing_key or "",
                accepted_event_types=accepted,
            )
        except Exception as exc:
            logger.error(
                "settlement failed; shutting down so the delivery is redelivered error_type=%s",
                type(exc).__name__,
            )
            stop.set()

    return channel.basic_consume(queue=queue_name, on_message_callback=_on_message, auto_ack=False)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = Settings.from_environ()
    handler = OdooApplyHandler(OdooClient(settings))
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_consumer(settings, handler, stop)


if __name__ == "__main__":
    main()

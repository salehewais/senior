"""Consume q.reporting.projection. One process, prefetch 10, manual ack.

Shutdown stops new deliveries, lets the callback already inside
process_data_events finish or leave its message unacked, then closes the
connection. An unacked delivery is redelivered by the broker when the
connection closes. That is not requeue=true on a poison message.
"""

from __future__ import annotations

import logging
import signal
import threading

import pika
from django.conf import settings
from django.db import connection

from projections.apply import apply_envelope
from projections.broker import broker_deadline, close_connection, open_connection
from projections.delivery import settle_delivery
from projections.outcomes import HEADER_FAILURE_REASON, HEADER_ORIGINAL_ROUTING_KEY, HEADER_RETRY_COUNT
from projections.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_RETRY,
    PREFETCH_COUNT,
    QUEUE_REPORTING,
    declare_reporting_topology,
    retry_routing_key,
)

logger = logging.getLogger("reporting.consumer")


class RepublishingRouter:
    """Publish a failure on its own connection so the confirm cannot re-enter the consumer callback."""

    def __init__(self, url: str, timeout_seconds: float) -> None:
        self._url = url
        self._timeout = timeout_seconds

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        self._publish(
            exchange=EXCHANGE_COMMERCE_RETRY,
            routing_key=retry_routing_key(attempt),
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
            routing_key=DLQ_ROUTING_KEY,
            body=body,
            headers={
                HEADER_RETRY_COUNT: retry_count,
                HEADER_ORIGINAL_ROUTING_KEY: original_routing_key,
                HEADER_FAILURE_REASON: reason,
            },
        )

    def _publish(self, *, exchange: str, routing_key: str, body: bytes, headers: dict[str, object]) -> None:
        connection_mq = open_connection(self._url, self._timeout)
        try:
            with broker_deadline(connection_mq, self._timeout):
                channel = connection_mq.channel()
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
            close_connection(connection_mq, timeout_seconds=self._timeout)


def consume_until_stopped(connection_mq, channel, consumer_tag: str, stop: threading.Event, timeout: float) -> None:
    """Run until stop is set. The current callback finishes inside process_data_events."""

    while not stop.is_set():
        connection_mq.process_data_events(time_limit=0.5)
    if channel.is_open:
        with broker_deadline(connection_mq, timeout):
            channel.basic_cancel(consumer_tag)


def run_consumer(stop: threading.Event) -> None:
    timeout = float(settings.RABBITMQ_TIMEOUT_SECONDS)
    url = settings.RABBITMQ_URL
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    router = RepublishingRouter(url, timeout)
    connection_mq = open_connection(url, timeout)
    try:
        with broker_deadline(connection_mq, timeout):
            channel = connection_mq.channel()
            declare_reporting_topology(channel)
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)

            def _on_message(ch, method, properties, body) -> None:
                header_map: dict[str, object] = {}
                if properties is not None and properties.headers:
                    header_map = dict(properties.headers)
                message_id = properties.message_id if properties is not None else None
                raw = body.encode("utf-8") if isinstance(body, str) else bytes(body)
                try:
                    settle_delivery(
                        ch,
                        method.delivery_tag,
                        raw,
                        apply_envelope,
                        router=router,
                        headers=header_map,
                        routing_key=method.routing_key or "",
                        property_message_id=message_id,
                    )
                except Exception as exc:
                    logger.error(
                        "settlement failed; shutting down so the delivery is redelivered error_type=%s",
                        type(exc).__name__,
                    )
                    stop.set()

            consumer_tag = channel.basic_consume(
                queue=QUEUE_REPORTING,
                on_message_callback=_on_message,
                auto_ack=False,
            )
        logger.info("consumer started queue=%s prefetch=%s", QUEUE_REPORTING, PREFETCH_COUNT)
        consume_until_stopped(connection_mq, channel, consumer_tag, stop, timeout)
    finally:
        close_connection(connection_mq, timeout_seconds=timeout)
        connection.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_consumer(stop)

"""Consume q.reporting.projection. Prefetch 10 per process, manual ack.

A second replica is another consumer on the same queue. processed_events
dedupes event_id.

Shutdown stops new deliveries, lets the callback already inside
process_data_events finish or leave its message unacked, then closes the
connection. An unacked delivery is redelivered by the broker when the
connection closes. That is not requeue=true on a poison message.
"""

from __future__ import annotations

import logging
import signal
import threading

from django.conf import settings
from django.db import connection

from projections.domain.apply import apply_envelope
from projections.messaging.broker import broker_deadline, close_connection, open_connection
from projections.messaging.delivery import settle_delivery
from projections.messaging.router import RepublishingRouter
from projections.messaging.topology import PREFETCH_COUNT, QUEUE_REPORTING, declare_reporting_topology

logger = logging.getLogger("reporting.consumer")


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
    from projections.observability.metrics import serve_metrics

    serve_metrics()
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_consumer(stop)

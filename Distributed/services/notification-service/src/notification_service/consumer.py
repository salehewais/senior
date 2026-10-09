"""Consume q.notification.delivery. Prefetch 10, manual ack, no requeue."""

from __future__ import annotations

import logging
import signal
import threading

import pika
from prometheus_client import start_http_server

from notification_service.adapters import MockEmail, MockPush
from notification_service.apply import apply_notification
from notification_service.broker import broker_deadline, close_connection, open_connection
from notification_service.delivery import settle_delivery
from notification_service.envelope import ParsedEnvelope
from notification_service.outcomes import HEADER_FAILURE_REASON, HEADER_ORIGINAL_ROUTING_KEY, HEADER_RETRY_COUNT
from notification_service.settings import metrics_port, rabbitmq_timeout_seconds, rabbitmq_url
from notification_service.store import SqlStore
from notification_service.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_RETRY,
    PREFETCH_COUNT,
    QUEUE_NOTIFICATION,
    declare_notification_topology,
    retry_routing_key,
)

logger = logging.getLogger("notification.consumer")


class RepublishingRouter:
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
    while not stop.is_set():
        connection_mq.process_data_events(time_limit=0.5)
    if channel.is_open:
        with broker_deadline(connection_mq, timeout):
            channel.basic_cancel(consumer_tag)


def run_consumer(stop: threading.Event, store: SqlStore | None = None) -> None:
    timeout = rabbitmq_timeout_seconds()
    url = rabbitmq_url()
    database = store if store is not None else SqlStore.from_settings()
    if not database.ping():
        raise RuntimeError("notification_db did not answer. The consumer does not open order_db.")
    email = MockEmail()
    push = MockPush()
    router = RepublishingRouter(url, timeout)
    connection_mq = open_connection(url, timeout)
    try:
        with broker_deadline(connection_mq, timeout):
            channel = connection_mq.channel()
            declare_notification_topology(channel)
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)

            def _on_message(ch, method, properties, body) -> None:
                header_map: dict[str, object] = {}
                if properties is not None and properties.headers:
                    header_map = dict(properties.headers)
                raw = body.encode("utf-8") if isinstance(body, str) else bytes(body)

                def _handle(inspected: ParsedEnvelope):
                    return apply_notification(inspected, database, email, push)

                try:
                    settle_delivery(
                        ch,
                        method.delivery_tag,
                        raw,
                        _handle,
                        router=router,
                        headers=header_map,
                        routing_key=method.routing_key or "",
                    )
                except Exception:
                    logger.error("settlement failed; shutting down so the delivery is redelivered")
                    stop.set()

            consumer_tag = channel.basic_consume(
                queue=QUEUE_NOTIFICATION,
                on_message_callback=_on_message,
                auto_ack=False,
            )
        logger.info("consumer started queue=%s prefetch=%s", QUEUE_NOTIFICATION, PREFETCH_COUNT)
        consume_until_stopped(connection_mq, channel, consumer_tag, stop, timeout)
    finally:
        close_connection(connection_mq, timeout_seconds=timeout)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    start_http_server(metrics_port())
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_consumer(stop)


if __name__ == "__main__":
    main()

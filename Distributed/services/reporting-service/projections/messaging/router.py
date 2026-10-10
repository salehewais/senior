"""Publish retries and dead letters on a connection that is not the consumer's."""

from __future__ import annotations

import pika

from projections.domain.outcomes import HEADER_FAILURE_REASON, HEADER_ORIGINAL_ROUTING_KEY, HEADER_RETRY_COUNT
from projections.messaging.broker import broker_deadline, close_connection, open_connection
from projections.messaging.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_RETRY,
    retry_routing_key,
)


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

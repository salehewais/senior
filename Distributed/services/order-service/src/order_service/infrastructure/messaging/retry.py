"""Publish a failed delivery onto commerce.retry or commerce.dlx.

The publish uses its own connection. Doing it on the consumer channel would
let the confirm wait read the next delivery and run another callback on the
same stack. Connect, confirm, and close each stop at the broker timeout.
"""

from __future__ import annotations

import pika

from order_service.application.consuming import (
    HEADER_FAILURE_REASON,
    HEADER_ORIGINAL_ROUTING_KEY,
    HEADER_RETRY_COUNT,
)
from order_service.infrastructure.messaging.connection import (
    broker_deadline,
    close_connection,
    open_connection,
)
from order_service.infrastructure.messaging.topology import (
    DLQ_ROUTING_KEY,
    EXCHANGE_COMMERCE_DLX,
    EXCHANGE_COMMERCE_RETRY,
    retry_routing_key,
)
from order_service.infrastructure.settings import Settings


class RepublishingRouter:
    def __init__(self, settings: Settings, queue_name: str) -> None:
        self._settings = settings
        self._queue_name = queue_name

    def schedule_retry(
        self,
        *,
        attempt: int,
        body: bytes,
        original_routing_key: str,
        reason: str,
    ) -> None:
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

    def dead_letter(
        self,
        *,
        body: bytes,
        original_routing_key: str,
        reason: str,
        retry_count: int,
    ) -> None:
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
        connection = open_connection(self._settings, timeout_seconds=timeout)
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

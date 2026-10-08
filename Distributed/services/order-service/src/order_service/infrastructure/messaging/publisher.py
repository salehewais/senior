"""Publish to the commerce.events exchange and wait for a broker confirm.

The routing key comes from the envelope mapping. This module never publishes
to a queue name. Publisher confirms mean the broker has accepted the message
onto the exchange. They do not mean a consumer has acked it.

The connection is opened per publish and closed in a finally block, so a
stuck socket cannot be reused on the next request. Declare, confirm, and
publish all run on that connection and therefore share its timeouts.
"""

from __future__ import annotations

import json

import pika

from order_service.application.publishing import OutboundMessage
from order_service.infrastructure.messaging.connection import (
    broker_deadline,
    close_connection,
    open_connection,
)
from order_service.infrastructure.messaging.topology import EXCHANGE_COMMERCE_EVENTS, declare_topology
from order_service.infrastructure.settings import Settings


class PikaEventPublisher:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def publish(self, message: OutboundMessage) -> None:
        timeout = self._settings.rabbitmq_timeout_seconds
        connection = open_connection(self._settings)
        try:
            with broker_deadline(connection, timeout):
                channel = connection.channel()
                declare_topology(channel)
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange=EXCHANGE_COMMERCE_EVENTS,
                    routing_key=message.routing_key,
                    body=_body(message),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        content_encoding="utf-8",
                        delivery_mode=pika.DeliveryMode.Persistent,
                        message_id=str(message.event_id),
                        correlation_id=str(message.correlation_id),
                        type=message.event_type,
                        app_id="order-service",
                    ),
                    mandatory=True,
                )
        finally:
            close_connection(connection, timeout_seconds=timeout)


def _body(message: OutboundMessage) -> bytes:
    return json.dumps(message.body, separators=(",", ":")).encode("utf-8")

"""Publish to the commerce.events exchange and wait for a broker confirm.

The routing key comes from the envelope. This module never publishes to a
queue name. Publisher confirms mean the broker has accepted the message onto
the exchange. They do not mean a consumer has acked it.

PikaEventPublisher opens a connection per call. The outbox publisher holds
ConfirmingBroker for the life of the process and closes it on shutdown.
Declare, confirm, and publish each stop at the configured timeout.
"""

from __future__ import annotations

import json

import pika
from pika.adapters.blocking_connection import BlockingChannel

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
                _publish_confirmed(channel, message)
        finally:
            close_connection(connection, timeout_seconds=timeout)


class ConfirmingBroker:
    """One connection for the outbox publisher. ``publish`` returns after the broker confirms.

    A failed confirm closes the connection so the next attempt opens a new one.
    ``close`` is safe to call more than once, including when no connection was opened.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def publish(self, message: OutboundMessage) -> None:
        timeout = self._settings.rabbitmq_timeout_seconds
        try:
            channel = self._ensure_channel(timeout)
            connection = self._connection
            if connection is None:
                raise RuntimeError("RabbitMQ connection is not open.")
            with broker_deadline(connection, timeout):
                _publish_confirmed(channel, message)
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        connection = self._connection
        self._connection = None
        self._channel = None
        if connection is not None:
            close_connection(connection, timeout_seconds=self._settings.rabbitmq_timeout_seconds)

    def _ensure_channel(self, timeout: float) -> BlockingChannel:
        connection = self._connection
        channel = self._channel
        if connection is not None and connection.is_open and channel is not None and channel.is_open:
            return channel
        self.close()
        connection = open_connection(self._settings)
        self._connection = connection
        try:
            with broker_deadline(connection, timeout):
                opened = connection.channel()
                declare_topology(opened)
                opened.confirm_delivery()
                self._channel = opened
                return opened
        except Exception:
            self.close()
            raise


def _publish_confirmed(channel: BlockingChannel, message: OutboundMessage) -> None:
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


def _body(message: OutboundMessage) -> bytes:
    return json.dumps(message.body, separators=(",", ":")).encode("utf-8")

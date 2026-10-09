"""Blocking RabbitMQ connections with a deadline on every broker call."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pika

logger = logging.getLogger("commerce_erp.broker")


class BrokerCallTimeout(TimeoutError):
    """A declare, confirm, or close did not finish within the budget."""


def open_connection(url: str, timeout_seconds: float) -> pika.BlockingConnection:
    if timeout_seconds <= 0:
        raise ValueError("RabbitMQ timeout must be greater than zero.")
    params = pika.URLParameters(url)
    params.connection_attempts = 1
    params.retry_delay = 0
    params.socket_timeout = timeout_seconds
    params.stack_timeout = timeout_seconds
    params.blocked_connection_timeout = timeout_seconds
    params.heartbeat = 0
    params.client_properties = {"connection_name": "commerce-platform-topology"}
    return pika.BlockingConnection(params)


@contextmanager
def broker_deadline(connection: pika.BlockingConnection, timeout_seconds: float) -> Iterator[None]:
    if timeout_seconds <= 0:
        raise ValueError("RabbitMQ timeout must be greater than zero.")
    ioloop = connection._impl.ioloop

    def _expired() -> None:
        raise BrokerCallTimeout(f"RabbitMQ did not answer within {timeout_seconds} seconds.")

    handle = ioloop.call_later(timeout_seconds, _expired)
    try:
        yield
    finally:
        ioloop.remove_timeout(handle)


def close_connection(connection: pika.BlockingConnection, *, timeout_seconds: float) -> None:
    try:
        if connection.is_open:
            with broker_deadline(connection, timeout_seconds):
                connection.close()
    except Exception as exc:
        logger.debug("rabbitmq connection close failed error_type=%s", type(exc).__name__)

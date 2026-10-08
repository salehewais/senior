"""Blocking connections with an explicit timeout on every network step.

pika is the client because the use cases publish synchronously after commit.
aio-pika would put an event loop on the request thread, or hide the same
blocking wait in a background thread. socket_timeout and stack_timeout bound
the handshake. blocked_connection_timeout bounds a broker disk alarm.

pika's BlockingChannel then waits for declare-ok and publisher confirms in a
loop that has no deadline of its own. broker_deadline arms a timer on that
same loop so a quiet socket cannot hold a checkout open. The consumer is its
own process and uses the same client.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pika

from order_service.infrastructure.settings import Settings

logger = logging.getLogger("order_service.messaging")


class BrokerCallTimeout(TimeoutError):
    """A declare, confirm, or close did not finish within the budget."""


def open_connection(settings: Settings, *, timeout_seconds: float | None = None) -> pika.BlockingConnection:
    timeout = settings.rabbitmq_timeout_seconds if timeout_seconds is None else timeout_seconds
    if timeout <= 0:
        raise ValueError("RabbitMQ timeout must be greater than zero.")
    params = pika.URLParameters(settings.rabbitmq_url)
    # One attempt. pika's own retry loop would add a second, unbounded wait.
    params.connection_attempts = 1
    params.retry_delay = 0
    params.socket_timeout = timeout
    params.stack_timeout = timeout
    params.blocked_connection_timeout = timeout
    # Heartbeats are off. A heartbeat shorter than socket_timeout makes pika
    # treat a quiet consumer as a stalled socket. process_data_events wakes
    # on its own time limit instead.
    params.heartbeat = 0
    params.client_properties = {"connection_name": "commerce-platform-topology"}
    return pika.BlockingConnection(params)


@contextmanager
def broker_deadline(connection: pika.BlockingConnection, timeout_seconds: float) -> Iterator[None]:
    """Raise BrokerCallTimeout if the following broker calls outlive the budget.

    The timer is registered on the connection's I/O loop. BlockingChannel
    drains that loop while it waits for a frame, and the loop runs the timer.
    """

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


def close_connection(connection: pika.BlockingConnection, *, timeout_seconds: float = 5) -> None:
    try:
        if connection.is_open:
            with broker_deadline(connection, timeout_seconds):
                connection.close()
    except Exception as exc:
        logger.debug("rabbitmq connection close failed error_type=%s", type(exc).__name__)

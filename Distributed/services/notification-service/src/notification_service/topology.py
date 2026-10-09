"""Declare q.notification.delivery on the existing commerce exchanges.

The arguments match the reporting consumer: durable topic exchanges, five TTL
retry queues, a dead-letter queue, and no x-dead-letter-exchange on the
primary queue. Redeclaring the shared exchanges is idempotent.
"""

from __future__ import annotations

import pika

EXCHANGE_COMMERCE_EVENTS = "commerce.events"
EXCHANGE_COMMERCE_RETRY = "commerce.retry"
EXCHANGE_COMMERCE_DLX = "commerce.dlx"

QUEUE_NOTIFICATION = "q.notification.delivery"
DLQ_ROUTING_KEY = "notification.delivery"

RETRY_DELAYS_MS: tuple[int, ...] = (5_000, 30_000, 120_000, 600_000, 1_800_000)
PREFETCH_COUNT = 10

BINDINGS: tuple[str, ...] = (
    "order.confirmed",
    "order.cancelled",
    "order.shipped",
    "order.delivered",
    "payment.confirmed",
    "payment.failed",
)


def retry_routing_key(attempt: int) -> str:
    if attempt < 1 or attempt > len(RETRY_DELAYS_MS):
        raise ValueError(f"Retry attempt {attempt} is outside 1..{len(RETRY_DELAYS_MS)}.")
    return f"{DLQ_ROUTING_KEY}.retry.{attempt}"


def declare_notification_topology(channel: pika.channel.Channel) -> None:
    for name in (EXCHANGE_COMMERCE_EVENTS, EXCHANGE_COMMERCE_RETRY, EXCHANGE_COMMERCE_DLX):
        channel.exchange_declare(exchange=name, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NOTIFICATION, durable=True)
    for routing_key in BINDINGS:
        channel.queue_bind(queue=QUEUE_NOTIFICATION, exchange=EXCHANGE_COMMERCE_EVENTS, routing_key=routing_key)
    for attempt, ttl_ms in enumerate(RETRY_DELAYS_MS, start=1):
        retry_queue = f"{QUEUE_NOTIFICATION}.retry.{attempt}"
        channel.queue_declare(
            queue=retry_queue,
            durable=True,
            arguments={
                "x-message-ttl": ttl_ms,
                "x-dead-letter-exchange": EXCHANGE_COMMERCE_EVENTS,
            },
        )
        channel.queue_bind(
            queue=retry_queue,
            exchange=EXCHANGE_COMMERCE_RETRY,
            routing_key=retry_routing_key(attempt),
        )
        channel.queue_bind(
            queue=QUEUE_NOTIFICATION,
            exchange=EXCHANGE_COMMERCE_EVENTS,
            routing_key=retry_routing_key(attempt),
        )
    dlq = f"{QUEUE_NOTIFICATION}.dlq"
    channel.queue_declare(queue=dlq, durable=True)
    channel.queue_bind(queue=dlq, exchange=EXCHANGE_COMMERCE_DLX, routing_key=DLQ_ROUTING_KEY)

"""Declare the reporting queue's bindings and the retry ladder.

Phase 5 already declares this for q.reporting.projection. Repeating the same
arguments is idempotent, so this consumer can start before the order service.
The order-service inventory and Odoo queues are left alone.

A failed delivery is published to commerce.retry, then acked. Each retry queue
holds it for a TTL and dead-letters it back to commerce.events under the retry
routing key, which this queue is bound to. The sixth failure is published to
commerce.dlx. Primary queues have no x-dead-letter-exchange, matching Phase 5,
so nack requeue=false would drop the message. This consumer does not nack.
"""

from __future__ import annotations

import pika

EXCHANGE_COMMERCE_EVENTS = "commerce.events"
EXCHANGE_ERP_EVENTS = "erp.events"
EXCHANGE_COMMERCE_RETRY = "commerce.retry"
EXCHANGE_COMMERCE_DLX = "commerce.dlx"

QUEUE_REPORTING = "q.reporting.projection"
DLQ_ROUTING_KEY = "reporting.projection"

# docs/rabbitmq.md. Attempt 6 is the DLQ, not another delay.
RETRY_DELAYS_MS: tuple[int, ...] = (5_000, 30_000, 120_000, 600_000, 1_800_000)

# docs/rabbitmq.md: start at 10. Fixed per process. A second replica does not raise it.
PREFETCH_COUNT = 10

_EXCHANGES = (
    EXCHANGE_COMMERCE_EVENTS,
    EXCHANGE_ERP_EVENTS,
    EXCHANGE_COMMERCE_RETRY,
    EXCHANGE_COMMERCE_DLX,
)

_BINDINGS: tuple[tuple[str, str], ...] = (
    (EXCHANGE_COMMERCE_EVENTS, "order.*"),
    (EXCHANGE_COMMERCE_EVENTS, "product.*"),
    (EXCHANGE_COMMERCE_EVENTS, "customer.*"),
    (EXCHANGE_COMMERCE_EVENTS, "payment.*"),
    (EXCHANGE_ERP_EVENTS, "inventory.updated"),
)


def retry_routing_key(attempt: int) -> str:
    if attempt < 1 or attempt > len(RETRY_DELAYS_MS):
        raise ValueError(f"Retry attempt {attempt} is outside 1..{len(RETRY_DELAYS_MS)}.")
    return f"{DLQ_ROUTING_KEY}.retry.{attempt}"


def declare_reporting_topology(channel: pika.channel.Channel) -> None:
    for name in _EXCHANGES:
        channel.exchange_declare(exchange=name, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_REPORTING, durable=True)
    for exchange, routing_key in _BINDINGS:
        channel.queue_bind(queue=QUEUE_REPORTING, exchange=exchange, routing_key=routing_key)
    for attempt, ttl_ms in enumerate(RETRY_DELAYS_MS, start=1):
        retry_queue = f"{QUEUE_REPORTING}.retry.{attempt}"
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
            queue=QUEUE_REPORTING,
            exchange=EXCHANGE_COMMERCE_EVENTS,
            routing_key=retry_routing_key(attempt),
        )
    dlq = f"{QUEUE_REPORTING}.dlq"
    channel.queue_declare(queue=dlq, durable=True)
    channel.queue_bind(queue=dlq, exchange=EXCHANGE_COMMERCE_DLX, routing_key=DLQ_ROUTING_KEY)

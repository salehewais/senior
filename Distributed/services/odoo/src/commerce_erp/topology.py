"""Declare the same queue arguments as the order service.

RabbitMQ refuses to redeclare a queue whose arguments differ. This module
matches services/order-service topology.py. Odoo consumes only
q.odoo.order-confirmed. It publishes InventoryUpdated to erp.events.
It does not publish order-status events to commerce.events.
"""

from __future__ import annotations

import pika

EXCHANGE_COMMERCE_EVENTS = "commerce.events"
EXCHANGE_ERP_EVENTS = "erp.events"
EXCHANGE_COMMERCE_RETRY = "commerce.retry"
EXCHANGE_COMMERCE_DLX = "commerce.dlx"

QUEUE_REPORTING = "q.reporting.projection"
QUEUE_ODOO_CONFIRMED = "q.odoo.order-confirmed"
QUEUE_INVENTORY = "q.order.inventory"

DLQ_ROUTING_KEY = {
    QUEUE_REPORTING: "reporting.projection",
    QUEUE_ODOO_CONFIRMED: "odoo.order-confirmed",
    QUEUE_INVENTORY: "order.inventory",
}

RETRY_DELAYS_MS: tuple[int, ...] = (5_000, 30_000, 120_000, 600_000, 1_800_000)

_RETRY_RETURN_EXCHANGE = {
    QUEUE_REPORTING: EXCHANGE_COMMERCE_EVENTS,
    QUEUE_ODOO_CONFIRMED: EXCHANGE_COMMERCE_EVENTS,
    QUEUE_INVENTORY: EXCHANGE_ERP_EVENTS,
}

_EVENT_EXCHANGES = (
    EXCHANGE_COMMERCE_EVENTS,
    EXCHANGE_ERP_EVENTS,
    EXCHANGE_COMMERCE_RETRY,
    EXCHANGE_COMMERCE_DLX,
)

_BINDINGS: tuple[tuple[str, str, str], ...] = (
    (QUEUE_REPORTING, EXCHANGE_COMMERCE_EVENTS, "order.*"),
    (QUEUE_REPORTING, EXCHANGE_COMMERCE_EVENTS, "product.*"),
    (QUEUE_REPORTING, EXCHANGE_COMMERCE_EVENTS, "customer.*"),
    (QUEUE_REPORTING, EXCHANGE_COMMERCE_EVENTS, "payment.*"),
    (QUEUE_REPORTING, EXCHANGE_ERP_EVENTS, "inventory.updated"),
    (QUEUE_ODOO_CONFIRMED, EXCHANGE_COMMERCE_EVENTS, "order.confirmed"),
    (QUEUE_INVENTORY, EXCHANGE_ERP_EVENTS, "inventory.updated"),
)


def declare_topology(channel: pika.channel.Channel) -> None:
    for name in _EVENT_EXCHANGES:
        channel.exchange_declare(exchange=name, exchange_type="topic", durable=True)
    for queue_name in (QUEUE_REPORTING, QUEUE_ODOO_CONFIRMED, QUEUE_INVENTORY):
        channel.queue_declare(queue=queue_name, durable=True)
    for queue_name, exchange, routing_key in _BINDINGS:
        channel.queue_bind(queue=queue_name, exchange=exchange, routing_key=routing_key)
    _declare_retry_queues(channel)
    _declare_retry_return_bindings(channel)
    _declare_dead_letter_queues(channel)


def _declare_retry_queues(channel: pika.channel.Channel) -> None:
    for queue_name, return_exchange in _RETRY_RETURN_EXCHANGE.items():
        prefix = DLQ_ROUTING_KEY[queue_name]
        for attempt, ttl_ms in enumerate(RETRY_DELAYS_MS, start=1):
            retry_queue = f"{queue_name}.retry.{attempt}"
            channel.queue_declare(
                queue=retry_queue,
                durable=True,
                arguments={
                    "x-message-ttl": ttl_ms,
                    "x-dead-letter-exchange": return_exchange,
                },
            )
            channel.queue_bind(
                queue=retry_queue,
                exchange=EXCHANGE_COMMERCE_RETRY,
                routing_key=f"{prefix}.retry.{attempt}",
            )


def _declare_retry_return_bindings(channel: pika.channel.Channel) -> None:
    for queue_name, return_exchange in _RETRY_RETURN_EXCHANGE.items():
        prefix = DLQ_ROUTING_KEY[queue_name]
        for attempt in range(1, len(RETRY_DELAYS_MS) + 1):
            channel.queue_bind(
                queue=queue_name,
                exchange=return_exchange,
                routing_key=f"{prefix}.retry.{attempt}",
            )


def retry_routing_key(queue_name: str, attempt: int) -> str:
    if attempt < 1 or attempt > len(RETRY_DELAYS_MS):
        raise ValueError(f"Retry attempt {attempt} is outside 1..{len(RETRY_DELAYS_MS)}.")
    return f"{DLQ_ROUTING_KEY[queue_name]}.retry.{attempt}"


def _declare_dead_letter_queues(channel: pika.channel.Channel) -> None:
    for queue_name, routing_key in DLQ_ROUTING_KEY.items():
        dlq = f"{queue_name}.dlq"
        channel.queue_declare(queue=dlq, durable=True)
        channel.queue_bind(queue=dlq, exchange=EXCHANGE_COMMERCE_DLX, routing_key=routing_key)

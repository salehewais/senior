"""Map committed domain events onto the catalog envelope and publish them.

Publish-after-commit is not the transactional outbox. The database commit has
already succeeded. If this process dies before the broker confirms, or the
broker rejects the publish, the event is gone. Phase 6 inserts the same
envelope in the order transaction and retries until RabbitMQ accepts it.
A failure here is logged with correlation_id and event_id only. The payload
is not logged: CustomerUpdated carries an email address.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from order_service.domain.events import (
    CustomerUpdated,
    DomainEvent,
    OrderCancelled,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderProcessingStarted,
    OrderShipped,
    ProductCreated,
    ProductUpdated,
)

logger = logging.getLogger("order_service.publishing")

PRODUCER = "order-service"
SCHEMA_VERSION = 1

# Keys are the contract in docs/rabbitmq.md. Queue names are not.
ROUTING_KEYS: dict[str, str] = {
    "OrderCreated": "order.created",
    "OrderConfirmed": "order.confirmed",
    "OrderCancelled": "order.cancelled",
    "OrderProcessingStarted": "order.processing-started",
    "OrderShipped": "order.shipped",
    "OrderDelivered": "order.delivered",
    "ProductCreated": "product.created",
    "ProductUpdated": "product.updated",
    "CustomerUpdated": "customer.updated",
}


class RecordsEvents(Protocol):
    def pending_events(self) -> Sequence[DomainEvent]: ...

    def collect_events(self) -> Sequence[DomainEvent]: ...


@dataclass(frozen=True, slots=True)
class OutboundMessage:
    """One envelope ready for the broker. The body is the source of truth."""

    event_id: uuid.UUID
    event_type: str
    routing_key: str
    correlation_id: uuid.UUID
    body: dict[str, object]


class EventPublisher(Protocol):
    def publish(self, message: OutboundMessage) -> None:
        """Publish to the commerce.events exchange. Raise if the broker does not confirm."""


def publish_after_commit(publisher: EventPublisher | None, *aggregates: RecordsEvents) -> None:
    """Send events recorded on these aggregates. Never call this before commit.

    ``publisher`` is None in tests that are not about the broker. Those events
    are still dropped, which is the Phase 1 behavior. The HTTP process passes
    a real publisher. A raise from the publisher does not propagate: the sale
    stays committed.
    """

    if publisher is None:
        return
    events: list[DomainEvent] = []
    for aggregate in aggregates:
        events.extend(aggregate.pending_events())
    for event in events:
        try:
            publisher.publish(to_outbound(event))
        except Exception as exc:
            logger.error(
                "publish failed after commit; the row is committed and this event can be lost "
                "until the outbox exists correlation_id=%s event_id=%s event_type=%s error_type=%s",
                event.correlation_id,
                event.event_id,
                event.event_type,
                type(exc).__name__,
            )
    for aggregate in aggregates:
        aggregate.collect_events()


def to_outbound(event: DomainEvent) -> OutboundMessage:
    event_type = event.event_type
    try:
        routing_key = ROUTING_KEYS[event_type]
    except KeyError as exc:
        raise TypeError(f"{event_type} has no routing key in the catalog.") from exc
    body: dict[str, object] = {
        "event_id": str(event.event_id),
        "event_type": event_type,
        "occurred_at": _occurred_at(event.occurred_at),
        "producer": PRODUCER,
        "aggregate_id": str(event.aggregate_id),
        "correlation_id": str(event.correlation_id),
        "causation_id": str(event.causation_id),
        "version": SCHEMA_VERSION,
        "payload": _payload(event),
    }
    return OutboundMessage(
        event_id=event.event_id,
        event_type=event_type,
        routing_key=routing_key,
        correlation_id=event.correlation_id,
        body=body,
    )


def _payload(event: DomainEvent) -> dict[str, object]:
    if isinstance(event, OrderCreated):
        return _order_lines(event, "PENDING")
    if isinstance(event, OrderConfirmed):
        return _order_lines(event, "CONFIRMED")
    if isinstance(event, OrderCancelled):
        return {
            "order_id": str(event.aggregate_id),
            "status": "CANCELLED",
            "reason": event.reason,
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, OrderProcessingStarted):
        return {
            "order_id": str(event.aggregate_id),
            "status": "PROCESSING",
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, OrderShipped):
        return {
            "order_id": str(event.aggregate_id),
            "status": "SHIPPED",
            "tracking_reference": event.tracking_reference,
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, OrderDelivered):
        return {
            "order_id": str(event.aggregate_id),
            "status": "DELIVERED",
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, ProductCreated | ProductUpdated):
        return {
            "product_id": str(event.aggregate_id),
            "sku": event.sku,
            "name": event.name,
            "unit_price": event.unit_price.as_dict(),
            "active": event.active,
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, CustomerUpdated):
        return {
            "customer_id": str(event.aggregate_id),
            "email": event.email,
            "display_name": event.display_name,
            "aggregate_version": event.aggregate_version,
        }
    raise TypeError(f"{event.event_type} has no payload mapping.")


def _order_lines(event: OrderCreated | OrderConfirmed, status: str) -> dict[str, object]:
    return {
        "order_id": str(event.aggregate_id),
        "customer_id": str(event.customer_id.value),
        "status": status,
        "items": [
            {
                "product_id": str(item.product_id.value),
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": item.unit_price.as_dict(),
            }
            for item in event.items
        ],
        "total": event.total.as_dict(),
        "aggregate_version": event.aggregate_version,
    }


def _occurred_at(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    text = value.astimezone(UTC).isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text

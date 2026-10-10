"""Map domain events onto the catalog envelope.

The unit of work stores that envelope in the outbox before commit. The
publisher process sends the stored body later. This module does not open a
broker connection. CustomerUpdated carries an email, so nothing here logs a
payload.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from order_service.application.saga.contract import COMMAND_ROUTING_KEYS, EXCHANGE_COMMERCE_COMMANDS
from order_service.domain.events import (
    CustomerUpdated,
    DomainEvent,
    OrderCancelled,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderProcessingStarted,
    OrderShipped,
    PaymentConfirmed,
    PaymentFailed,
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
    "PaymentConfirmed": "payment.confirmed",
    "PaymentFailed": "payment.failed",
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
    exchange: str = "commerce.events"


class EventPublisher(Protocol):
    def publish(self, message: OutboundMessage) -> None:
        """Publish to the commerce.events exchange. Raise if the broker does not confirm."""


def to_outbound(event: DomainEvent, trace_carrier: Mapping[str, str] | None = None) -> OutboundMessage:
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
    # traceparent is the technical id. correlation_id above is unchanged.
    # The caller supplies the carrier. This module does not read OpenTelemetry.
    if trace_carrier:
        body.update(trace_carrier)
    return OutboundMessage(
        event_id=event.event_id,
        event_type=event_type,
        routing_key=routing_key,
        correlation_id=event.correlation_id,
        body=body,
    )


def aggregate_type_for(event: DomainEvent) -> str:
    if isinstance(
        event,
        OrderCreated | OrderConfirmed | OrderCancelled | OrderProcessingStarted | OrderShipped | OrderDelivered,
    ):
        return "order"
    if isinstance(event, ProductCreated | ProductUpdated):
        return "product"
    if isinstance(event, CustomerUpdated):
        return "customer"
    if isinstance(event, PaymentConfirmed | PaymentFailed):
        return "order"
    raise TypeError(f"{event.event_type} has no aggregate type.")


def outbound_from_envelope(payload: object, *, column_event_type: str) -> OutboundMessage:
    """Build a broker message from the stored envelope. The payload is authoritative.

    A mismatch between the ``event_type`` column and ``payload.event_type`` is
    logged with ids only. The column is not used to rebuild the body.
    """

    if not isinstance(payload, dict):
        raise TypeError("outbox payload is not a JSON object")
    payload_type = payload.get("event_type")
    if payload_type != column_event_type:
        logger.error(
            "outbox event_type column disagrees with payload; sending the payload "
            "event_id=%s column_event_type=%s payload_event_type=%s correlation_id=%s",
            payload.get("event_id"),
            column_event_type,
            payload_type,
            payload.get("correlation_id"),
        )
    if not isinstance(payload_type, str):
        raise TypeError("outbox payload has no catalog routing key")
    if payload_type in COMMAND_ROUTING_KEYS:
        routing_key = COMMAND_ROUTING_KEYS[payload_type]
        exchange = EXCHANGE_COMMERCE_COMMANDS
    elif payload_type in ROUTING_KEYS:
        routing_key = ROUTING_KEYS[payload_type]
        exchange = "commerce.events"
    else:
        raise TypeError("outbox payload has no catalog routing key")
    try:
        event_id = uuid.UUID(str(payload.get("event_id")))
        correlation_id = uuid.UUID(str(payload.get("correlation_id")))
    except ValueError as exc:
        raise TypeError("outbox payload event_id or correlation_id is not a UUID") from exc
    return OutboundMessage(
        event_id=event_id,
        event_type=payload_type,
        routing_key=routing_key,
        correlation_id=correlation_id,
        body=payload,
        exchange=exchange,
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
    if isinstance(event, PaymentConfirmed):
        return {
            "order_id": str(event.aggregate_id),
            "payment_reference": event.payment_reference,
            "amount": event.amount.as_dict(),
            "aggregate_version": event.aggregate_version,
        }
    if isinstance(event, PaymentFailed):
        return {
            "order_id": str(event.aggregate_id),
            "reason_code": event.reason_code,
            "aggregate_version": event.aggregate_version,
        }
    raise TypeError(f"{event.event_type} has no payload mapping.")


def command_message(
    *,
    event_id: uuid.UUID,
    event_type: str,
    occurred_at: datetime,
    aggregate_id: uuid.UUID,
    correlation_id: uuid.UUID,
    causation_id: uuid.UUID,
    payload: dict[str, object],
    trace_carrier: Mapping[str, str] | None = None,
) -> OutboundMessage:
    """One saga command envelope. It is not a catalog event and not a report fact."""

    try:
        routing_key = COMMAND_ROUTING_KEYS[event_type]
    except KeyError as exc:
        raise TypeError(f"{event_type} is not a saga command.") from exc
    body: dict[str, object] = {
        "event_id": str(event_id),
        "event_type": event_type,
        "occurred_at": _occurred_at(occurred_at),
        "producer": PRODUCER,
        "aggregate_id": str(aggregate_id),
        "correlation_id": str(correlation_id),
        "causation_id": str(causation_id),
        "version": SCHEMA_VERSION,
        "payload": payload,
    }
    if trace_carrier:
        body.update(trace_carrier)
    return OutboundMessage(
        event_id=event_id,
        event_type=event_type,
        routing_key=routing_key,
        correlation_id=correlation_id,
        body=body,
        exchange=EXCHANGE_COMMERCE_COMMANDS,
    )


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

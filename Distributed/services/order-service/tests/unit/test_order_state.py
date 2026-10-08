import uuid
from datetime import UTC, datetime

import pytest

from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.entities.order_status import (
    ALLOWED_TRANSITIONS,
    OrderStatus,
    require_transition,
)
from order_service.domain.events import (
    OrderCancelled,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderProcessingStarted,
    OrderShipped,
)
from order_service.domain.exceptions import DomainValidationError, InvalidStateTransition
from order_service.domain.ids import CustomerId, ProductId
from order_service.domain.value_objects import Money, Quantity

NOW = datetime(2026, 10, 8, tzinfo=UTC)
CORRELATION = uuid.UUID("018f1c2a-3333-7c11-8a22-444444444444")
CAUSATION = uuid.UUID("018f1c2a-5555-7c11-8a22-666666666666")


def _item(amount: int = 1500, currency: str = "USD", quantity: int = 2) -> OrderItem:
    return OrderItem(
        product_id=ProductId.generate(),
        sku="MUG-01",
        quantity=Quantity.of_line(quantity),
        unit_price=Money(amount, currency),
    )


def _order(*items: OrderItem) -> Order:
    return Order.create(
        customer_id=CustomerId.generate(),
        items=items or (_item(),),
        now=NOW,
        correlation_id=CORRELATION,
        causation_id=CAUSATION,
    )


def test_create_prices_the_lines_and_records_order_created() -> None:
    order = _order(_item(1500, quantity=2))
    assert order.status is OrderStatus.PENDING
    assert order.version == 1
    assert order.total == Money(3000, "USD")
    assert order.saga_status is None
    event = order.pending_events()[0]
    assert isinstance(event, OrderCreated)
    assert event.aggregate_version == 1
    assert event.total == Money(3000, "USD")


def test_happy_path_reaches_delivered_with_contiguous_versions() -> None:
    order = _order()
    order.confirm(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    order.start_processing(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    order.ship(tracking_reference=" TRK-100 ", now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    order.deliver(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    assert order.status is OrderStatus.DELIVERED
    assert order.version == 5
    assert order.tracking_reference == "TRK-100"
    kinds = [type(event) for event in order.pending_events()]
    assert kinds == [
        OrderCreated,
        OrderConfirmed,
        OrderProcessingStarted,
        OrderShipped,
        OrderDelivered,
    ]


def test_pending_order_can_be_cancelled() -> None:
    order = _order()
    order.cancel(reason="customer_request", now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    assert order.status is OrderStatus.CANCELLED
    assert order.cancel_reason == "customer_request"
    assert isinstance(order.pending_events()[-1], OrderCancelled)


@pytest.mark.parametrize(
    ("setup", "action"),
    [
        ("confirmed", "cancel"),
        ("confirmed", "confirm"),
        ("pending", "ship"),
        ("pending", "deliver"),
        ("pending", "process"),
        ("delivered", "confirm"),
        ("cancelled", "confirm"),
        ("shipped", "cancel"),
    ],
)
def test_illegal_transitions_are_rejected(setup: str, action: str) -> None:
    order = _order()
    if setup in {"confirmed", "delivered", "shipped"}:
        order.confirm(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    if setup in {"delivered", "shipped"}:
        order.start_processing(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    if setup in {"delivered", "shipped"}:
        order.ship(tracking_reference=None, now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    if setup == "delivered":
        order.deliver(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    if setup == "cancelled":
        order.cancel(reason="staff_request", now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)

    status_before = order.status
    version_before = order.version
    with pytest.raises(InvalidStateTransition):
        _act(order, action)
    assert order.status is status_before
    assert order.version == version_before


def test_only_the_documented_edges_are_legal() -> None:
    expected = {
        (OrderStatus.PENDING, OrderStatus.CONFIRMED),
        (OrderStatus.PENDING, OrderStatus.CANCELLED),
        (OrderStatus.CONFIRMED, OrderStatus.PROCESSING),
        (OrderStatus.PROCESSING, OrderStatus.SHIPPED),
        (OrderStatus.SHIPPED, OrderStatus.DELIVERED),
    }
    assert ALLOWED_TRANSITIONS == expected
    for current in OrderStatus:
        for target in OrderStatus:
            if (current, target) in expected:
                require_transition(current, target)
            else:
                with pytest.raises(InvalidStateTransition):
                    require_transition(current, target)


def test_failed_cancel_does_not_change_a_confirmed_order() -> None:
    order = _order()
    order.confirm(now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    version = order.version
    with pytest.raises(InvalidStateTransition) as caught:
        order.cancel(
            reason="customer_request",
            now=NOW,
            correlation_id=CORRELATION,
            causation_id=CAUSATION,
        )
    assert "CONFIRMED" in str(caught.value)
    assert "CANCELLED" in str(caught.value)
    assert order.version == version
    assert order.status is OrderStatus.CONFIRMED


def test_unknown_cancel_reason_is_not_a_transition() -> None:
    order = _order()
    with pytest.raises(DomainValidationError):
        order.cancel(reason="changed my mind", now=NOW, correlation_id=CORRELATION, causation_id=CAUSATION)
    assert order.status is OrderStatus.PENDING


def test_mixed_currencies_are_rejected() -> None:
    with pytest.raises(DomainValidationError):
        _order(_item(currency="USD"), _item(currency="EUR"))


def test_empty_order_is_rejected() -> None:
    with pytest.raises(DomainValidationError):
        Order.create(
            customer_id=CustomerId.generate(),
            items=(),
            now=NOW,
            correlation_id=CORRELATION,
            causation_id=CAUSATION,
        )


def _act(order: Order, action: str) -> None:
    kwargs = {"now": NOW, "correlation_id": CORRELATION, "causation_id": CAUSATION}
    if action == "confirm":
        order.confirm(**kwargs)
    elif action == "cancel":
        order.cancel(reason="customer_request", **kwargs)
    elif action == "process":
        order.start_processing(**kwargs)
    elif action == "ship":
        order.ship(tracking_reference=None, **kwargs)
    elif action == "deliver":
        order.deliver(**kwargs)
    else:
        raise AssertionError(action)

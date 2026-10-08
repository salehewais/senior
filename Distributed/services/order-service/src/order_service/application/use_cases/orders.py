"""Order use cases. Prices come from the catalog row, never from the caller."""

from __future__ import annotations

import uuid

from order_service.application.actor import Actor
from order_service.application.authorization import can_view_order, cancel_reason_for, require_role
from order_service.application.clock import Clock
from order_service.application.dto import OrderView, order_view
from order_service.application.pagination import decode_cursor, encode_cursor
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.exceptions import NotFoundError, ProductNotOrderableError
from order_service.domain.ids import CustomerId, OrderId, ProductId
from order_service.domain.roles import Role
from order_service.domain.value_objects import Quantity


class CreateOrder:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        actor: Actor,
        lines: list[tuple[uuid.UUID, int]],
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        # The subject of the access token is the customer. A body field cannot point this at someone else.
        require_role(actor, Role.CUSTOMER)
        customer = uow.customers.get(CustomerId(actor.account_id))
        if customer is None:
            raise NotFoundError("Customer not found.")
        items: list[OrderItem] = []
        for product_id, quantity in lines:
            product = uow.products.get(ProductId(product_id))
            if product is None:
                raise NotFoundError("Product not found.")
            if not product.active:
                raise ProductNotOrderableError(f"Product {product.sku} is not available to order.")
            items.append(
                OrderItem(
                    product_id=product.id,
                    sku=product.sku,
                    quantity=Quantity.of_line(quantity),
                    unit_price=product.unit_price,
                )
            )
        order = Order.create(
            customer_id=customer.id,
            items=tuple(items),
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        # Same transaction as the order. The broker is a different process.
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


class GetOrder:
    def execute(self, uow: UnitOfWork, *, actor: Actor, order_id: uuid.UUID) -> OrderView:
        # A customer looking up someone else's order gets the same 404 as a missing id.
        return order_view(_require_visible(uow, actor, order_id))


class ListOrders:
    def execute(
        self,
        uow: UnitOfWork,
        *,
        actor: Actor,
        limit: int,
        cursor: str | None,
    ) -> tuple[list[OrderView], str | None]:
        if actor.role == Role.CUSTOMER:
            customer_filter: uuid.UUID | None = actor.account_id
        else:
            require_role(actor, Role.ADMIN, Role.MANAGER)
            customer_filter = None
        created_before = None
        id_before = None
        if cursor is not None:
            created_before, id_before = decode_cursor(cursor)
        rows = uow.orders.list_page(
            limit=limit + 1,
            created_before=created_before,
            id_before=id_before,
            customer_id=customer_filter,
        )
        page = rows[:limit]
        next_cursor = None
        if len(rows) > limit and page:
            last = page[-1]
            next_cursor = encode_cursor(last.created_at, last.id.value)
        return [order_view(row) for row in page], next_cursor


class ConfirmOrder:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        actor: Actor,
        order_id: uuid.UUID,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        order = _require_visible(uow, actor, order_id)
        order.confirm(
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


class CancelOrder:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        actor: Actor,
        order_id: uuid.UUID,
        reason: str,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        order = _require_visible(uow, actor, order_id)
        order.cancel(
            reason=cancel_reason_for(actor, reason),
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


class StartProcessing:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        order_id: uuid.UUID,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        order = _require_order(uow, order_id)
        order.start_processing(
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


class ShipOrder:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        order_id: uuid.UUID,
        tracking_reference: str | None,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        order = _require_order(uow, order_id)
        order.ship(
            tracking_reference=tracking_reference,
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


class DeliverOrder:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        order_id: uuid.UUID,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> OrderView:
        order = _require_order(uow, order_id)
        order.deliver(
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.orders.add(order)
        uow.stage_events(order)
        uow.commit()
        return order_view(order)


def _require_order(uow: UnitOfWork, order_id: uuid.UUID) -> Order:
    order = uow.orders.get(OrderId(order_id))
    if order is None:
        raise NotFoundError("Order not found.")
    return order


def _require_visible(uow: UnitOfWork, actor: Actor, order_id: uuid.UUID) -> Order:
    order = uow.orders.get(OrderId(order_id))
    if order is None or not can_view_order(actor, order):
        raise NotFoundError("Order not found.")
    return order

"""Commit a confirmed order in the in-memory order_db and return the row plus its events.

The reporting walkthrough reads this JSON. It does not open Postgres, RabbitMQ, or Redis.
Create and confirm are two transactions, matching ConfirmOrder: the confirm commit
holds the CONFIRMED row, the saga row, and the OrderConfirmed outbox row together.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.saga.orchestrator import advance
from order_service.application.saga.results import StepResult, absent, succeeded
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import ConfirmOrder, CreateOrder
from order_service.domain.entities.saga_status import SagaStatus
from order_service.domain.ids import OrderId
from order_service.domain.roles import Role
from order_service.infrastructure.saga.payment import SimulatedPayment

ORDER_EVENTS = ("OrderCreated", "OrderConfirmed", "PaymentConfirmed", "PaymentFailed", "OrderDelivered")
_SAGA_NOW = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)


class _SuccessInventory:
    def lookup_reservation(self, order_id: str) -> StepResult:
        del order_id
        return absent()

    def reserve(self, command: dict[str, object]) -> StepResult:
        del command
        return succeeded("rsv-1")

    def release(self, command: dict[str, object]) -> StepResult:
        del command
        return succeeded("rsv-1")


class _SuccessErp:
    def lookup_sales_order(self, order_id: str) -> StepResult:
        del order_id
        return absent()

    def create_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        return succeeded("so-1")

    def cancel_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        return succeeded("so-1")


def export_confirmed_order() -> dict[str, object]:
    store, order_id = _confirmed_store()
    return _snapshot(store, order_id)


def export_completed_saga_order() -> dict[str, object]:
    """Saga COMPLETED. The order row stays CONFIRMED. PaymentConfirmed is in the outbox. No OrderDelivered."""

    store, order_id = _confirmed_store()
    _complete_saga(store, order_id)
    return _snapshot(store, order_id)


def _confirmed_store() -> tuple[MemoryStore, uuid.UUID]:
    store = MemoryStore()
    clock = FixedClock()
    admin = Actor(account_id=uuid.uuid4(), role=Role.ADMIN)
    customer_uow = InMemoryUnitOfWork(store)
    customer = CreateCustomer(clock).execute(
        customer_uow,
        email="ada@example.com",
        display_name="Ada",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    customer_uow.close()
    product_uow = InMemoryUnitOfWork(store)
    product = CreateProduct(clock).execute(
        product_uow,
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=admin,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    product_uow.close()
    buyer = Actor(account_id=customer.id, role=Role.CUSTOMER)
    create_uow = InMemoryUnitOfWork(store)
    created = CreateOrder(clock).execute(
        create_uow,
        actor=buyer,
        lines=[(product.id, 2)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    create_uow.close()
    confirm_uow = InMemoryUnitOfWork(store)
    ConfirmOrder(clock).execute(
        confirm_uow,
        actor=buyer,
        order_id=created.id,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    confirm_uow.close()
    return store, created.id


def _complete_saga(store: MemoryStore, order_id: uuid.UUID) -> None:
    saga_id = next(row.id for row in store.sagas.values() if row.order_id == order_id)
    inventory = _SuccessInventory()
    payment = SimulatedPayment()
    erp = _SuccessErp()
    for _ in range(8):
        uow = InMemoryUnitOfWork(store)
        saga = uow.sagas.get(saga_id)
        order = uow.orders.get(OrderId(order_id))
        if saga is None or order is None:
            raise AssertionError("confirmed order has no saga row")
        records = advance(saga, order, inventory=inventory, payment=payment, erp=erp, now=_SAGA_NOW)
        uow.sagas.add(saga)
        uow.orders.add(order)
        uow.stage_events(order)
        uow.stage_outbox(records)
        uow.commit()
        status = saga.status
        uow.close()
        if status is SagaStatus.COMPLETED:
            return
    raise AssertionError("saga did not reach COMPLETED")


def _snapshot(store: MemoryStore, order_id: uuid.UUID) -> dict[str, object]:
    order = store.orders[order_id]
    saga = next(row for row in store.sagas.values() if row.order_id == order.id.value)
    events = [
        row.payload
        for row in sorted(
            (row for row in store.outbox.values() if row.event_type in ORDER_EVENTS),
            key=lambda row: int(row.payload["payload"]["aggregate_version"]),  # type: ignore[index]
        )
    ]
    return {
        "order": {
            "order_id": str(order.id.value),
            "status": order.status.value,
            "version": order.version,
            "saga_status": order.saga_status,
            "total_amount_minor": order.total.amount_minor,
            "currency": order.total.currency,
        },
        "saga": {
            "saga_id": str(saga.id),
            "order_id": str(saga.order_id),
            "status": saga.status.value,
        },
        "events": events,
    }

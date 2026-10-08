import uuid

import pytest
from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import (
    CancelOrder,
    ConfirmOrder,
    CreateOrder,
    ListOrders,
)
from order_service.domain.exceptions import (
    InvalidStateTransition,
    NotFoundError,
    ProductNotOrderableError,
)
from order_service.domain.roles import Role
from order_service.domain.value_objects import Money


def _admin() -> Actor:
    return Actor(account_id=uuid.uuid4(), role=Role.ADMIN)


def _buyer(customer_id: uuid.UUID) -> Actor:
    return Actor(account_id=customer_id, role=Role.CUSTOMER)


def _catalog(store: MemoryStore, clock: FixedClock):
    uow = InMemoryUnitOfWork(store)
    customer = CreateCustomer(clock).execute(
        uow,
        email="ada@example.com",
        display_name="Ada",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    uow = InMemoryUnitOfWork(store)
    product = CreateProduct(clock).execute(
        uow,
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    return customer, product


def test_create_order_copies_the_catalog_price() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    uow = InMemoryUnitOfWork(store)
    order = CreateOrder(clock).execute(
        uow,
        actor=_buyer(customer.id),
        lines=[(product.id, 2)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    assert order.total == Money(3000, "USD") or (
        order.total.amount_minor == 3000 and order.total.currency == "USD"
    )
    assert order.items[0].unit_price.amount_minor == 1500
    assert order.status == "PENDING"
    assert order.version == 1
    uow.close()


def test_inactive_product_cannot_be_ordered() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    stored = next(iter(store.products.values()))
    stored.active = False
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(ProductNotOrderableError):
        CreateOrder(clock).execute(
            uow,
            actor=_buyer(customer.id),
            lines=[(product.id, 1)],
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert store.orders == {}


def test_confirm_then_cancel_conflicts_and_rolls_back_the_attempt() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    uow = InMemoryUnitOfWork(store)
    created = CreateOrder(clock).execute(
        uow,
        actor=_buyer(customer.id),
        lines=[(product.id, 1)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    uow = InMemoryUnitOfWork(store)
    confirmed = ConfirmOrder(clock).execute(
        uow,
        actor=_buyer(customer.id),
        order_id=created.id,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    assert confirmed.status == "CONFIRMED"
    assert confirmed.version == 2
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(InvalidStateTransition):
        CancelOrder(clock).execute(
            uow,
            actor=_buyer(customer.id),
            order_id=created.id,
            reason="customer_request",
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert store.orders[created.id].status.value == "CONFIRMED"
    assert store.orders[created.id].version == 2


def test_missing_customer_is_not_found() -> None:
    store = MemoryStore()
    clock = FixedClock()
    _, product = _catalog(store, clock)
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(NotFoundError):
        CreateOrder(clock).execute(
            uow,
            actor=_buyer(uuid.uuid4()),
            lines=[(product.id, 1)],
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()


def test_order_list_cursor_does_not_repeat_the_first_page() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    created = []
    for _ in range(3):
        uow = InMemoryUnitOfWork(store)
        created.append(
            CreateOrder(clock).execute(
                uow,
                actor=_buyer(customer.id),
                lines=[(product.id, 1)],
                correlation_id=uuid.uuid4(),
                causation_id=uuid.uuid4(),
            )
        )
        uow.close()
    uow = InMemoryUnitOfWork(store)
    buyer = _buyer(customer.id)
    first, cursor = ListOrders().execute(uow, actor=buyer, limit=2, cursor=None)
    second, next_cursor = ListOrders().execute(uow, actor=buyer, limit=2, cursor=cursor)
    uow.close()
    assert cursor is not None
    assert next_cursor is None
    assert [item.id for item in first] == [created[2].id, created[1].id]
    assert [item.id for item in second] == [created[0].id]

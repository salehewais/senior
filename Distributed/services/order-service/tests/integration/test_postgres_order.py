"""Postgres checks. Skipped when the Phase 1 database is not reachable."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from tests.support.clock import FixedClock

from order_service.application.actor import Actor
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import CreateOrder
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.ids import CustomerId, OrderId, ProductId
from order_service.domain.roles import Role
from order_service.domain.value_objects import Quantity
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.models import OutboxRow
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.settings import Settings


@pytest.fixture(scope="module")
def sessions():
    engine = make_engine(Settings())
    missing_outbox = False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            try:
                connection.execute(text("SELECT 1 FROM outbox LIMIT 0"))
            except ProgrammingError:
                missing_outbox = True
    except OperationalError:
        engine.dispose()
        pytest.skip("order_db is not running. Start services/order-service/compose.yaml.")
    if missing_outbox:
        engine.dispose()
        pytest.skip("outbox table is missing. From services/order-service run: alembic upgrade head")
    factory = make_session_factory(engine)
    yield factory
    engine.dispose()


def _outbox_row(
    sessions,
    event_id: uuid.UUID | None,
    *,
    aggregate_id: uuid.UUID | None = None,
    event_type: str | None = None,
):
    session = sessions()
    try:
        if event_id is not None:
            row = session.get(OutboxRow, event_id)
        else:
            row = session.scalar(
                select(OutboxRow).where(
                    OutboxRow.aggregate_id == aggregate_id,
                    OutboxRow.event_type == event_type,
                )
            )
        if row is None:
            return None
        return (row.status, row.published_at, dict(row.payload), row.id)
    except ProgrammingError as exc:
        pytest.skip(f"outbox table is missing. Run alembic upgrade head. {exc}")
    finally:
        session.rollback()
        session.close()


def test_uncommitted_order_disappears_on_rollback(sessions) -> None:
    clock = FixedClock()
    suffix = uuid.uuid4().hex[:8]
    setup = SqlUnitOfWork(sessions())
    customer = CreateCustomer(clock).execute(
        setup,
        email=f"ada-{suffix}@example.com",
        display_name="Ada",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    product = CreateProduct(clock).execute(
        setup,
        sku=f"SKU-{suffix}",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=Actor(account_id=uuid.uuid4(), role=Role.ADMIN),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    setup.close()

    abandoned = SqlUnitOfWork(sessions())
    customer_row = abandoned.customers.get(CustomerId(customer.id))
    product_row = abandoned.products.get(ProductId(product.id))
    assert customer_row is not None and product_row is not None
    order = Order.create(
        customer_id=customer_row.id,
        items=(
            OrderItem(
                product_id=product_row.id,
                sku=product_row.sku,
                quantity=Quantity.of_line(1),
                unit_price=product_row.unit_price,
            ),
        ),
        now=clock.now(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    event_id = order.pending_events()[0].event_id
    abandoned.orders.add(order)
    abandoned.stage_events(order)
    abandoned._session.flush()
    abandoned.rollback()
    abandoned.close()

    check = SqlUnitOfWork(sessions())
    assert check.orders.get(order.id) is None
    check.close()
    assert _outbox_row(sessions, event_id) is None


def test_committed_order_and_items_are_visible_together(sessions) -> None:
    clock = FixedClock()
    suffix = uuid.uuid4().hex[:8]
    uow = SqlUnitOfWork(sessions())
    customer = CreateCustomer(clock).execute(
        uow,
        email=f"grace-{suffix}@example.com",
        display_name="Grace",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    product = CreateProduct(clock).execute(
        uow,
        sku=f"MUG-{suffix}",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=Actor(account_id=uuid.uuid4(), role=Role.ADMIN),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    order = CreateOrder(clock).execute(
        uow,
        actor=Actor(account_id=customer.id, role=Role.CUSTOMER),
        lines=[(product.id, 2)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()

    check = SqlUnitOfWork(sessions())
    stored = check.orders.get(OrderId(order.id))
    assert stored is not None
    assert stored.total.amount_minor == 3000
    assert len(stored.items) == 1
    assert stored.items[0].sku == f"MUG-{suffix}"
    assert stored.items[0].unit_price.amount_minor == 1500
    check.close()
    outbox = _outbox_row(sessions, None, aggregate_id=order.id, event_type="OrderCreated")
    assert outbox is not None
    assert outbox[0] == "pending"
    assert outbox[1] is None
    assert outbox[2]["event_type"] == "OrderCreated"
    assert outbox[2]["event_id"] == str(outbox[3])

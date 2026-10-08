"""The business write and the outbox row share one transaction. The broker is not in it."""

import uuid

import pytest
from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.outbox import OutboxRecord
from order_service.application.publishing import ROUTING_KEYS
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import (
    CancelOrder,
    ConfirmOrder,
    CreateOrder,
    DeliverOrder,
    ShipOrder,
    StartProcessing,
)
from order_service.domain.exceptions import ProductNotOrderableError
from order_service.domain.roles import Role
from order_service.infrastructure.messaging.outbox_publisher import PendingOutbox, publish_batch


class RecordingBroker:
    def __init__(self) -> None:
        self.routing_keys: list[str] = []

    def publish(self, message) -> None:
        self.routing_keys.append(message.routing_key)


def _admin() -> Actor:
    return Actor(account_id=uuid.uuid4(), role=Role.ADMIN)


def _buyer(customer_id: uuid.UUID) -> Actor:
    return Actor(account_id=customer_id, role=Role.CUSTOMER)


def _catalog(store: MemoryStore, clock: FixedClock):
    customer = CreateCustomer(clock).execute(
        InMemoryUnitOfWork(store),
        email="ada@example.com",
        display_name="Ada",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    product = CreateProduct(clock).execute(
        InMemoryUnitOfWork(store),
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    return customer, product


def _rows(store: MemoryStore, event_type: str) -> list[OutboxRecord]:
    return [row for row in store.outbox.values() if row.event_type == event_type]


def test_create_and_confirm_write_pending_outbox_rows() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    correlation_id = uuid.uuid4()
    causation_id = uuid.uuid4()
    uow = InMemoryUnitOfWork(store)
    created = CreateOrder(clock).execute(
        uow,
        actor=_buyer(customer.id),
        lines=[(product.id, 2)],
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    uow.close()
    assert created.status == "PENDING"
    assert store.orders[created.id].status.value == "PENDING"
    created_rows = _rows(store, "OrderCreated")
    assert len(created_rows) == 1
    row = created_rows[0]
    assert row.status == "pending"
    assert row.published_at is None
    assert row.retry_count == 0
    assert row.aggregate_type == "order"
    assert row.aggregate_id == created.id
    envelope = row.payload
    assert row.id == uuid.UUID(str(envelope["event_id"]))
    assert envelope["event_type"] == "OrderCreated"
    assert envelope["producer"] == "order-service"
    assert envelope["version"] == 1
    assert envelope["aggregate_id"] == str(created.id)
    assert envelope["correlation_id"] == str(correlation_id)
    assert envelope["causation_id"] == str(causation_id)
    assert "occurred_at" in envelope
    payload = envelope["payload"]
    assert isinstance(payload, dict)
    assert payload["status"] == "PENDING"
    assert payload["aggregate_version"] == 1
    assert payload["total"] == {"amount_minor": 3000, "currency": "USD"}
    assert type(payload["total"]["amount_minor"]) is int
    assert payload["items"][0]["unit_price"]["amount_minor"] == 1500

    confirm_correlation = uuid.uuid4()
    uow = InMemoryUnitOfWork(store)
    confirmed = ConfirmOrder(clock).execute(
        uow,
        actor=_buyer(customer.id),
        order_id=created.id,
        correlation_id=confirm_correlation,
        causation_id=uuid.uuid4(),
    )
    uow.close()
    assert confirmed.status == "CONFIRMED"
    assert store.orders[created.id].version == 2
    confirmed_rows = _rows(store, "OrderConfirmed")
    assert len(confirmed_rows) == 1
    confirmed_row = confirmed_rows[0]
    assert confirmed_row.status == "pending"
    assert confirmed_row.payload["event_type"] == "OrderConfirmed"
    assert confirmed_row.payload["correlation_id"] == str(confirm_correlation)
    assert confirmed_row.payload["payload"]["aggregate_version"] == 2
    assert confirmed_row.payload["payload"]["status"] == "CONFIRMED"
    assert confirmed_row.id != row.id
    # The create fact is still the envelope written at insert time.
    assert _rows(store, "OrderCreated")[0].payload["payload"]["status"] == "PENDING"


def test_rollback_and_rejected_use_case_leave_no_outbox_row() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    before = set(store.outbox)

    class RefusingUnitOfWork(InMemoryUnitOfWork):
        def commit(self) -> None:
            raise RuntimeError("order_db refused the commit")

    uow = RefusingUnitOfWork(store)
    with pytest.raises(RuntimeError):
        CreateOrder(clock).execute(
            uow,
            actor=_buyer(customer.id),
            lines=[(product.id, 1)],
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert set(store.orders) == set()
    assert set(store.outbox) == before

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
    assert set(store.outbox) == before


def test_order_transition_envelopes_keep_catalog_routing_keys() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    buyer = _buyer(customer.id)
    uow = InMemoryUnitOfWork(store)
    created = CreateOrder(clock).execute(
        uow,
        actor=buyer,
        lines=[(product.id, 1)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    for use_case, kwargs in (
        (ConfirmOrder(clock), {"actor": buyer, "order_id": created.id}),
        (StartProcessing(clock), {"order_id": created.id}),
        (ShipOrder(clock), {"order_id": created.id, "tracking_reference": "TRK-100"}),
        (DeliverOrder(clock), {"order_id": created.id}),
    ):
        step = InMemoryUnitOfWork(store)
        use_case.execute(step, correlation_id=uuid.uuid4(), causation_id=uuid.uuid4(), **kwargs)
        step.close()

    shipped = next(row for row in store.outbox.values() if row.event_type == "OrderShipped")
    assert shipped.payload["payload"]["tracking_reference"] == "TRK-100"
    assert shipped.payload["payload"]["aggregate_version"] == 4
    assert shipped.status == "pending"

    order_rows = sorted(
        (row for row in store.outbox.values() if row.aggregate_type == "order"),
        key=lambda row: (row.created_at, row.id),
    )
    assert {row.event_type for row in order_rows} == {
        "OrderCreated",
        "OrderConfirmed",
        "OrderProcessingStarted",
        "OrderShipped",
        "OrderDelivered",
    }
    broker = RecordingBroker()
    publish_batch(_MemoryLease(store), broker, limit=100, max_attempts=5, now=clock.now)
    assert [key for key in broker.routing_keys if key.startswith("order.")] == [
        ROUTING_KEYS[row.event_type] for row in order_rows
    ]
    assert "q.reporting.projection" not in broker.routing_keys
    assert all(row.status == "published" for row in store.outbox.values())

    uow = InMemoryUnitOfWork(store)
    pending = CreateOrder(clock).execute(
        uow,
        actor=buyer,
        lines=[(product.id, 1)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    uow = InMemoryUnitOfWork(store)
    CancelOrder(clock).execute(
        uow,
        actor=buyer,
        order_id=pending.id,
        reason="customer_request",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    cancelled = next(row for row in store.outbox.values() if row.event_type == "OrderCancelled")
    assert cancelled.payload["payload"]["reason"] == "customer_request"
    assert cancelled.payload["payload"]["aggregate_version"] == 2
    assert ROUTING_KEYS["OrderCancelled"] == "order.cancelled"


def test_product_and_customer_envelopes_are_stored_whole() -> None:
    store = MemoryStore()
    uow = InMemoryUnitOfWork(store)
    CreateProduct(FixedClock()).execute(
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
    product_row = _rows(store, "ProductCreated")[0]
    assert product_row.aggregate_type == "product"
    assert product_row.status == "pending"
    price = product_row.payload["payload"]["unit_price"]
    assert price == {"amount_minor": 1500, "currency": "USD"}
    assert type(price["amount_minor"]) is int

    uow = InMemoryUnitOfWork(store)
    CreateCustomer(FixedClock()).execute(
        uow,
        email="ada@example.com",
        display_name="Ada",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    customer_row = _rows(store, "CustomerUpdated")[0]
    assert customer_row.aggregate_type == "customer"
    assert customer_row.payload["payload"]["email"] == "ada@example.com"
    assert customer_row.payload["event_id"] == str(customer_row.id)


class _MemoryLease:
    """Publishes whatever the memory store still has pending, then marks those records published."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store
        self._claimed: list[uuid.UUID] = []

    def claim(self, limit: int) -> list[PendingOutbox]:
        rows = sorted(
            (row for row in self._store.outbox.values() if row.status == "pending"),
            key=lambda row: (row.created_at, row.id),
        )
        chosen = rows[:limit]
        self._claimed = [row.id for row in chosen]
        return [
            PendingOutbox(
                id=row.id,
                event_type=row.event_type,
                aggregate_type=row.aggregate_type,
                aggregate_id=row.aggregate_id,
                payload=row.payload,
                retry_count=row.retry_count,
                created_at=row.created_at,
            )
            for row in chosen
        ]

    def mark_published(self, event_id: uuid.UUID, published_at) -> None:
        current = self._store.outbox[event_id]
        self._store.outbox[event_id] = OutboxRecord(
            id=current.id,
            event_type=current.event_type,
            aggregate_type=current.aggregate_type,
            aggregate_id=current.aggregate_id,
            payload=current.payload,
            created_at=current.created_at,
            published_at=published_at,
            retry_count=current.retry_count,
            status="published",
        )

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        raise AssertionError(f"catalog routing should confirm event_id={event_id} status={status}")

    def finish(self) -> None:
        return None

    def abort(self) -> None:
        return None

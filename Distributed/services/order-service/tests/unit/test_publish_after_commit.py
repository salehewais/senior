"""Publish-after-commit. The broker is a fake. A raise must not undo the commit."""

import logging
import uuid

import pytest
from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.publishing import OutboundMessage
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import (
    CancelOrder,
    ConfirmOrder,
    CreateOrder,
    DeliverOrder,
    ShipOrder,
    StartProcessing,
)
from order_service.domain.roles import Role


class RecordingPublisher:
    def __init__(self, *, error: BaseException | None = None) -> None:
        self.messages: list[OutboundMessage] = []
        self._error = error

    def publish(self, message: OutboundMessage) -> None:
        self.messages.append(message)
        if self._error is not None:
            raise self._error


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


def test_create_and_confirm_commit_when_publish_raises(caplog: pytest.LogCaptureFixture) -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    correlation_id = uuid.uuid4()
    publisher = RecordingPublisher(error=ConnectionError("payload email=ada@example.com"))
    uow = InMemoryUnitOfWork(store)
    with caplog.at_level(logging.ERROR):
        created = CreateOrder(clock, publisher).execute(
            uow,
            actor=_buyer(customer.id),
            lines=[(product.id, 2)],
            correlation_id=correlation_id,
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert created.status == "PENDING"
    assert store.orders[created.id].status.value == "PENDING"
    assert store.orders[created.id].version == 1
    message = publisher.messages[0]
    assert message.routing_key == "order.created"
    assert message.routing_key != "q.reporting.projection"
    body = message.body
    assert body["event_type"] == "OrderCreated"
    assert body["producer"] == "order-service"
    assert body["version"] == 1
    assert body["aggregate_id"] == str(created.id)
    assert body["correlation_id"] == str(correlation_id)
    payload = body["payload"]
    assert payload["status"] == "PENDING"
    assert payload["aggregate_version"] == 1
    assert payload["total"] == {"amount_minor": 3000, "currency": "USD"}
    assert type(payload["total"]["amount_minor"]) is int
    assert payload["items"][0]["unit_price"]["amount_minor"] == 1500
    assert "ada@example.com" not in caplog.text
    assert str(message.event_id) in caplog.text
    assert str(correlation_id) in caplog.text

    confirm_publisher = RecordingPublisher(error=ConnectionError("broker down"))
    confirm_correlation = uuid.uuid4()
    uow = InMemoryUnitOfWork(store)
    confirmed = ConfirmOrder(clock, confirm_publisher).execute(
        uow,
        actor=_buyer(customer.id),
        order_id=created.id,
        correlation_id=confirm_correlation,
        causation_id=uuid.uuid4(),
    )
    uow.close()
    assert confirmed.status == "CONFIRMED"
    assert store.orders[created.id].status.value == "CONFIRMED"
    assert store.orders[created.id].version == 2
    confirmed_message = confirm_publisher.messages[0]
    assert confirmed_message.routing_key == "order.confirmed"
    assert confirmed_message.body["event_type"] == "OrderConfirmed"
    assert confirmed_message.body["payload"]["aggregate_version"] == 2
    assert confirmed_message.body["payload"]["status"] == "CONFIRMED"
    assert [item.event_type for item in confirm_publisher.messages] == ["OrderConfirmed"]


def test_failed_commit_does_not_publish() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    publisher = RecordingPublisher()

    class RefusingUnitOfWork(InMemoryUnitOfWork):
        def commit(self) -> None:
            raise RuntimeError("order_db refused the commit")

    before = set(store.orders)
    uow = RefusingUnitOfWork(store)
    with pytest.raises(RuntimeError):
        CreateOrder(clock, publisher).execute(
            uow,
            actor=_buyer(customer.id),
            lines=[(product.id, 1)],
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert publisher.messages == []
    assert set(store.orders) == before


def test_order_transition_routing_keys_match_the_catalog() -> None:
    store = MemoryStore()
    clock = FixedClock()
    customer, product = _catalog(store, clock)
    publisher = RecordingPublisher()
    buyer = _buyer(customer.id)
    uow = InMemoryUnitOfWork(store)
    created = CreateOrder(clock, publisher).execute(
        uow,
        actor=buyer,
        lines=[(product.id, 1)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    for use_case, kwargs in (
        (ConfirmOrder(clock, publisher), {"actor": buyer, "order_id": created.id}),
        (StartProcessing(clock, publisher), {"order_id": created.id}),
        (ShipOrder(clock, publisher), {"order_id": created.id, "tracking_reference": "TRK-100"}),
        (DeliverOrder(clock, publisher), {"order_id": created.id}),
    ):
        step = InMemoryUnitOfWork(store)
        use_case.execute(step, correlation_id=uuid.uuid4(), causation_id=uuid.uuid4(), **kwargs)
        step.close()
    assert [message.routing_key for message in publisher.messages] == [
        "order.created",
        "order.confirmed",
        "order.processing-started",
        "order.shipped",
        "order.delivered",
    ]
    shipped = publisher.messages[3].body["payload"]
    assert shipped["tracking_reference"] == "TRK-100"
    assert shipped["aggregate_version"] == 4

    cancel_publisher = RecordingPublisher()
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
    CancelOrder(clock, cancel_publisher).execute(
        uow,
        actor=buyer,
        order_id=pending.id,
        reason="customer_request",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    cancelled = cancel_publisher.messages[0]
    assert cancelled.routing_key == "order.cancelled"
    assert cancelled.body["payload"]["reason"] == "customer_request"
    assert cancelled.body["payload"]["aggregate_version"] == 2


def test_customer_publish_failure_log_omits_email(caplog: pytest.LogCaptureFixture) -> None:
    publisher = RecordingPublisher(error=ConnectionError("email=ada@example.com"))
    uow = InMemoryUnitOfWork(MemoryStore())
    with caplog.at_level(logging.ERROR):
        CreateCustomer(FixedClock(), publisher).execute(
            uow,
            email="ada@example.com",
            display_name="Ada",
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    message = publisher.messages[0]
    assert message.routing_key == "customer.updated"
    assert message.body["payload"]["email"] == "ada@example.com"
    assert "ada@example.com" not in caplog.text
    assert str(message.event_id) in caplog.text


def test_product_created_envelope_keeps_minor_units() -> None:
    publisher = RecordingPublisher()
    uow = InMemoryUnitOfWork(MemoryStore())
    CreateProduct(FixedClock(), publisher).execute(
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
    message = publisher.messages[0]
    assert message.routing_key == "product.created"
    price = message.body["payload"]["unit_price"]
    assert price == {"amount_minor": 1500, "currency": "USD"}
    assert type(price["amount_minor"]) is int

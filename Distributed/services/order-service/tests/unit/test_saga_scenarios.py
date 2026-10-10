"""The eight saga scenarios from the extension spec, section 1.6."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.saga.orchestrator import advance
from order_service.application.saga.results import StepResult, absent, failed, succeeded, unknown
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.entities.order_status import OrderStatus
from order_service.domain.entities.saga import SagaInstance
from order_service.domain.entities.saga_status import SagaStatus
from order_service.domain.exceptions import InvalidStateTransition
from order_service.domain.ids import CustomerId, OrderId, ProductId
from order_service.domain.value_objects import Money, Quantity
from order_service.infrastructure.saga.payment import (
    CHARGE_DECLINE,
    REFUND_FAIL,
    SimulatedPayment,
)

NOW = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)


class StockBook:
    def __init__(self) -> None:
        self.held = False
        self.reservation_id = "rsv-1"
        self.sales_order = False


class ScriptedInventory:
    def __init__(
        self,
        book: StockBook,
        *,
        reserve: str = "succeed",
        release: str = "succeed",
        lookup: str = "read",
        hold_on_unknown: bool = False,
        released_on_unknown: bool = False,
    ) -> None:
        self.book = book
        self.reserve_mode = reserve
        self.release_mode = release
        self.lookup_mode = lookup
        self.hold_on_unknown = hold_on_unknown
        self.released_on_unknown = released_on_unknown
        self.reserve_calls = 0
        self.release_calls = 0
        self.lookup_calls = 0

    def lookup_reservation(self, order_id: str) -> StepResult:
        del order_id
        self.lookup_calls += 1
        if self.lookup_mode == "unknown":
            return unknown("odoo-unavailable")
        if self.book.held:
            return succeeded(self.book.reservation_id)
        return absent()

    def reserve(self, command: dict[str, object]) -> StepResult:
        del command
        self.reserve_calls += 1
        if self.reserve_mode == "fail":
            return failed("insufficient_stock")
        if self.reserve_mode == "unknown":
            if self.hold_on_unknown:
                self.book.held = True
            return unknown("timeout")
        self.book.held = True
        return succeeded(self.book.reservation_id)

    def release(self, command: dict[str, object]) -> StepResult:
        del command
        self.release_calls += 1
        if self.release_mode == "fail":
            return failed("release_failed")
        if self.release_mode == "unknown":
            if self.released_on_unknown:
                self.book.held = False
            return unknown("timeout")
        self.book.held = False
        return succeeded(self.book.reservation_id)


class ScriptedErp:
    def __init__(
        self,
        book: StockBook,
        *,
        create: str = "succeed",
        cancel: str = "succeed",
        lookup: str = "read",
    ) -> None:
        self.book = book
        self.create_mode = create
        self.cancel_mode = cancel
        self.lookup_mode = lookup
        self.create_calls = 0
        self.cancel_calls = 0
        self.lookup_calls = 0

    def lookup_sales_order(self, order_id: str) -> StepResult:
        del order_id
        self.lookup_calls += 1
        if self.lookup_mode == "unknown":
            return unknown("odoo-unavailable")
        if self.book.sales_order:
            return succeeded("so-1")
        return absent()

    def create_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        self.create_calls += 1
        if self.create_mode == "fail":
            return failed("erp_create_failed")
        if self.create_mode == "unknown":
            return unknown("timeout")
        self.book.sales_order = True
        return succeeded("so-1")

    def cancel_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        self.cancel_calls += 1
        if self.cancel_mode == "fail":
            return failed("cancel_erp_failed")
        self.book.sales_order = False
        return succeeded("so-1")


def _seed() -> tuple[MemoryStore, uuid.UUID]:
    store = MemoryStore()
    order = Order.create(
        customer_id=CustomerId(uuid.uuid4()),
        items=(
            OrderItem(
                product_id=ProductId(uuid.uuid4()),
                sku="MUG-01",
                quantity=Quantity.of_line(2),
                unit_price=Money(1500, "USD"),
            ),
        ),
        now=NOW,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    order.confirm(now=NOW, correlation_id=order.pending_events()[0].correlation_id, causation_id=uuid.uuid4())
    correlation = order.pending_events()[0].correlation_id
    saga = SagaInstance.start(
        order_id=order.id.value,
        now=NOW,
        correlation_id=correlation,
        causation_id=uuid.uuid4(),
    )
    order.set_saga_status(saga.status.value)
    uow = InMemoryUnitOfWork(store)
    uow.orders.add(order)
    uow.sagas.add(saga)
    uow.stage_events(order)
    uow.commit()
    uow.close()
    return store, saga.id


def _step(store: MemoryStore, saga_id: uuid.UUID, inventory, payment, erp) -> SagaStatus:
    uow = InMemoryUnitOfWork(store)
    saga = uow.sagas.get(saga_id)
    assert saga is not None
    order = uow.orders.get(OrderId(saga.order_id))
    assert order is not None
    records = advance(saga, order, inventory=inventory, payment=payment, erp=erp, now=NOW)
    uow.sagas.add(saga)
    uow.orders.add(order)
    uow.stage_events(order)
    uow.stage_outbox(records)
    uow.commit()
    status = saga.status
    uow.close()
    return status


def _drive(store: MemoryStore, saga_id: uuid.UUID, inventory, payment, erp, *, limit: int = 8) -> SagaStatus:
    status = SagaStatus.STARTED
    for _ in range(limit):
        status = _step(store, saga_id, inventory, payment, erp)
        if status in {
            SagaStatus.COMPLETED,
            SagaStatus.COMPENSATED,
            SagaStatus.FAILED,
            SagaStatus.MANUAL_INTERVENTION_REQUIRED,
        }:
            break
    return status


def _order(store: MemoryStore, saga_id: uuid.UUID) -> Order:
    saga = store.sagas[saga_id]
    return store.orders[saga.order_id]


def _types(store: MemoryStore) -> set[str]:
    return {row.event_type for row in store.outbox.values()}


def test_legal_saga_transitions_reject_a_skip_to_completed() -> None:
    saga = SagaInstance.start(
        order_id=uuid.uuid4(),
        now=NOW,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    with pytest.raises(InvalidStateTransition):
        saga.complete(NOW)
    saga.reserve_succeeded("rsv-1", NOW)
    assert saga.status is SagaStatus.INVENTORY_RESERVED


def test_every_step_succeeds() -> None:
    store, saga_id = _seed()
    book = StockBook()
    status = _drive(store, saga_id, ScriptedInventory(book), SimulatedPayment(), ScriptedErp(book))
    order = _order(store, saga_id)

    assert status is SagaStatus.COMPLETED
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "COMPLETED"
    assert order.status is not OrderStatus.DELIVERED
    assert "ReserveInventory" in _types(store)
    assert "CreateErpOrder" in _types(store)
    assert "PaymentConfirmed" in _types(store)
    assert "ReleaseInventory" not in _types(store)
    reserve = next(row for row in store.outbox.values() if row.event_type == "ReserveInventory")
    assert reserve.payload["payload"]["idempotency_key"].endswith(":reserve")
    assert reserve.payload["payload"]["lines"][0]["sku"] == "MUG-01"


def test_inventory_reservation_fails() -> None:
    store, saga_id = _seed()
    book = StockBook()
    inventory = ScriptedInventory(book, reserve="fail")
    status = _drive(store, saga_id, inventory, SimulatedPayment(), ScriptedErp(book))
    order = _order(store, saga_id)

    assert status is SagaStatus.FAILED
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "FAILED"
    assert inventory.release_calls == 0
    assert "PaymentConfirmed" not in _types(store)
    assert "PaymentFailed" not in _types(store)
    assert "CreateErpOrder" not in _types(store)
    assert "ReleaseInventory" not in _types(store)


def test_payment_fails_after_inventory_reservation() -> None:
    store, saga_id = _seed()
    book = StockBook()
    inventory = ScriptedInventory(book)
    status = _drive(
        store,
        saga_id,
        inventory,
        SimulatedPayment(charge=CHARGE_DECLINE),
        ScriptedErp(book),
    )
    order = _order(store, saga_id)

    assert status is SagaStatus.COMPENSATED
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "COMPENSATED"
    assert book.held is False
    assert inventory.release_calls == 1
    assert "PaymentFailed" in _types(store)
    assert "ReleaseInventory" in _types(store)
    assert "CreateErpOrder" not in _types(store)
    failed_row = next(row for row in store.outbox.values() if row.event_type == "PaymentFailed")
    assert failed_row.payload["payload"]["reason_code"] == "declined"


def test_odoo_is_unavailable() -> None:
    store, saga_id = _seed()
    book = StockBook()
    inventory = ScriptedInventory(book, reserve="unknown", lookup="unknown")
    first = _step(store, saga_id, inventory, SimulatedPayment(), ScriptedErp(book))
    second = _step(store, saga_id, inventory, SimulatedPayment(), ScriptedErp(book))
    order = _order(store, saga_id)

    assert first is SagaStatus.STARTED
    assert second is SagaStatus.STARTED
    assert order.status is OrderStatus.CONFIRMED
    assert inventory.reserve_calls == 1
    assert inventory.lookup_calls == 1
    assert "PaymentConfirmed" not in _types(store)
    assert sum(1 for row in store.outbox.values() if row.event_type == "ReserveInventory") == 1


def test_an_event_arrives_twice() -> None:
    store, saga_id = _seed()
    book = StockBook()
    inventory = ScriptedInventory(book)
    payment = SimulatedPayment()
    first = _step(store, saga_id, inventory, payment, ScriptedErp(book))
    second = _step(store, saga_id, inventory, payment, ScriptedErp(book))

    assert first is SagaStatus.INVENTORY_RESERVED
    assert second is SagaStatus.PAYMENT_CONFIRMED
    assert inventory.reserve_calls == 1
    assert payment.charge_calls == 1
    assert sum(1 for row in store.outbox.values() if row.event_type == "ReserveInventory") == 1
    again = payment.charge(order_id="x", amount_minor=1, currency="USD", idempotency_key=f"{saga_id}:payment")
    assert again.reference == "sim-1"
    assert payment.charge_calls == 2


def test_process_crashes_halfway_through_the_saga() -> None:
    store, saga_id = _seed()
    book = StockBook()
    first_inventory = ScriptedInventory(book)
    _step(store, saga_id, first_inventory, SimulatedPayment(), ScriptedErp(book))
    del first_inventory
    restarted = ScriptedInventory(book)
    status = _step(store, saga_id, restarted, SimulatedPayment(), ScriptedErp(book))
    order = _order(store, saga_id)

    assert status is SagaStatus.PAYMENT_CONFIRMED
    assert restarted.reserve_calls == 0
    assert order.status is OrderStatus.CONFIRMED
    assert store.sagas[saga_id].has_step("reserve")
    assert store.sagas[saga_id].has_step("payment")


def test_compensation_fails() -> None:
    store, saga_id = _seed()
    book = StockBook()
    inventory = ScriptedInventory(book, release="fail")
    status = _drive(
        store,
        saga_id,
        inventory,
        SimulatedPayment(charge=CHARGE_DECLINE),
        ScriptedErp(book),
    )
    order = _order(store, saga_id)

    assert status is SagaStatus.MANUAL_INTERVENTION_REQUIRED
    assert status is not SagaStatus.COMPENSATED
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "MANUAL_INTERVENTION_REQUIRED"
    assert book.held is True
    assert store.sagas[saga_id].failure_reason == "release_failed"


def test_workflow_resumes_after_restart() -> None:
    store, saga_id = _seed()
    book = StockBook()
    first = ScriptedInventory(book, reserve="unknown", hold_on_unknown=True)
    status = _step(store, saga_id, first, SimulatedPayment(), ScriptedErp(book))
    assert status is SagaStatus.STARTED
    assert store.sagas[saga_id].pending_outcome == "unknown"
    del first
    restarted = ScriptedInventory(book, reserve="fail")
    status = _step(store, saga_id, restarted, SimulatedPayment(), ScriptedErp(book))
    order = _order(store, saga_id)

    assert status is SagaStatus.INVENTORY_RESERVED
    assert restarted.reserve_calls == 0
    assert restarted.lookup_calls == 1
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "INVENTORY_RESERVED"


def test_compensation_resumes_after_a_crash_without_a_second_release() -> None:
    """The release landed and the reply was lost. Restart looks the hold up and does not release again."""

    store, saga_id = _seed()
    book = StockBook()
    first = ScriptedInventory(book, release="unknown", released_on_unknown=True)
    payment = SimulatedPayment(charge=CHARGE_DECLINE)
    status = SagaStatus.STARTED
    for _ in range(6):
        status = _step(store, saga_id, first, payment, ScriptedErp(book))
        if store.sagas[saga_id].pending_outcome == "unknown":
            break

    assert status is SagaStatus.COMPENSATING
    assert store.sagas[saga_id].pending_step == "release"
    assert first.release_calls == 1
    assert book.held is False
    assert sum(1 for row in store.outbox.values() if row.event_type == "ReleaseInventory") == 1
    del first

    restarted = ScriptedInventory(book, release="fail")
    status = _drive(
        store,
        saga_id,
        restarted,
        SimulatedPayment(charge=CHARGE_DECLINE),
        ScriptedErp(book),
    )
    order = _order(store, saga_id)

    assert status is SagaStatus.COMPENSATED
    assert status is not SagaStatus.MANUAL_INTERVENTION_REQUIRED
    assert restarted.release_calls == 0
    assert restarted.lookup_calls == 1
    assert order.status is OrderStatus.CONFIRMED
    assert order.saga_status == "COMPENSATED"
    assert sum(1 for row in store.outbox.values() if row.event_type == "ReleaseInventory") == 1


def test_refund_failure_is_manual_intervention_and_not_a_guaranteed_refund() -> None:
    store, saga_id = _seed()
    book = StockBook()
    payment = SimulatedPayment(refund=REFUND_FAIL)
    erp = ScriptedErp(book, create="fail")
    status = _drive(store, saga_id, ScriptedInventory(book), payment, erp)

    assert status is SagaStatus.MANUAL_INTERVENTION_REQUIRED
    assert payment.refund_calls == 1
    assert book.held is True
    assert "CreateErpOrder" in _types(store)

"""Commit without the broker, then let the publisher and the reporting consumer meet.

Skipped when Postgres or RabbitMQ is down, including when nothing is listening on
5432 because another Postgres already owns that port and this project's database
is not reachable. The test does not start Docker and does not leave a consumer
thread running.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from tests.support.clock import FixedClock

from order_service.application.actor import Actor
from order_service.application.use_cases.catalog import CreateCustomer, CreateProduct
from order_service.application.use_cases.orders import CreateOrder
from order_service.domain.ids import OrderId
from order_service.domain.roles import Role
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.models import OutboxRow
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.messaging.connection import close_connection, open_connection
from order_service.infrastructure.messaging.consumer import run_consumer
from order_service.infrastructure.messaging.outbox_publisher import publish_once
from order_service.infrastructure.messaging.publisher import ConfirmingBroker
from order_service.infrastructure.messaging.topology import QUEUE_REPORTING, declare_topology
from order_service.infrastructure.settings import Settings


@dataclass(frozen=True, slots=True)
class _OutboxView:
    id: uuid.UUID
    status: str
    published_at: datetime | None
    envelope_event_id: str


def test_committed_order_stays_pending_until_the_publisher_and_is_acked_once() -> None:
    settings = Settings()
    engine = make_engine(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.execute(text("SELECT 1 FROM outbox LIMIT 0"))
    except OperationalError:
        engine.dispose()
        pytest.skip("order_db is not running. Start services/order-service/compose.yaml.")
    except ProgrammingError:
        engine.dispose()
        pytest.skip("outbox table is missing. From services/order-service run: alembic upgrade head")
    if not _broker_up(settings):
        engine.dispose()
        pytest.skip("RabbitMQ is not running. Start services/order-service/compose.yaml.")

    sessions = make_session_factory(engine)
    worker: threading.Thread | None = None
    broker: ConfirmingBroker | None = None
    stop = threading.Event()
    seen: list[str] = []
    errors: list[BaseException] = []
    try:
        suffix = uuid.uuid4().hex[:8]
        clock = FixedClock()
        setup = SqlUnitOfWork(sessions())
        try:
            customer = CreateCustomer(clock).execute(
                setup,
                email=f"ada-{suffix}@example.com",
                display_name="Ada",
                correlation_id=uuid.uuid4(),
                causation_id=uuid.uuid4(),
            )
            product = CreateProduct(clock).execute(
                setup,
                sku=f"MUG-{suffix}",
                name="Mug",
                amount_minor=1500,
                currency="USD",
                actor=Actor(account_id=uuid.uuid4(), role=Role.ADMIN),
                correlation_id=uuid.uuid4(),
                causation_id=uuid.uuid4(),
            )
            # The request path does not open RabbitMQ. The row is pending while the broker is untouched.
            order = CreateOrder(clock).execute(
                setup,
                actor=Actor(account_id=customer.id, role=Role.CUSTOMER),
                lines=[(product.id, 1)],
                correlation_id=uuid.uuid4(),
                causation_id=uuid.uuid4(),
            )
        finally:
            setup.close()

        pending = _load_outbox(sessions, order.id)
        assert pending is not None
        assert pending.status == "pending"
        assert pending.published_at is None
        assert pending.envelope_event_id == str(pending.id)
        check = SqlUnitOfWork(sessions())
        try:
            stored = check.orders.get(OrderId(order.id))
            assert stored is not None
            assert stored.status.value == "PENDING"
        finally:
            check.close()

        _purge(settings, QUEUE_REPORTING)
        ready = threading.Event()
        event_id = str(pending.id)

        def _handle(envelope: dict) -> None:
            if envelope.get("event_id") == event_id:
                seen.append(str(envelope.get("event_id")))

        def _run() -> None:
            try:
                run_consumer(settings, _handle, stop, ready=ready)
            except Exception as exc:
                errors.append(exc)
                ready.set()

        worker = threading.Thread(target=_run, name="outbox-ack-test", daemon=True)
        broker = ConfirmingBroker(settings)
        worker.start()
        assert ready.wait(10), errors or "consumer did not start"
        published = False
        for _ in range(30):
            publish_once(sessions, broker, settings)
            current = _load_outbox(sessions, order.id)
            if current is not None and current.status == "published":
                published = True
                break
        assert published, "publisher did not confirm the OrderCreated outbox row"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and seen != [event_id]:
            time.sleep(0.05)
        # A redelivery would append a second id. One ack leaves a single observation.
        time.sleep(0.3)
        assert seen == [event_id]
        finished = _load_outbox(sessions, order.id)
        assert finished is not None
        assert finished.status == "published"
        assert finished.published_at is not None
        assert finished.id == pending.id
        still = SqlUnitOfWork(sessions())
        try:
            stored = still.orders.get(OrderId(order.id))
            assert stored is not None
            assert stored.status.value == "PENDING"
        finally:
            still.close()
    finally:
        stop.set()
        if worker is not None:
            worker.join(10)
        if broker is not None:
            broker.close()
        engine.dispose()
    assert worker is not None and not worker.is_alive()
    assert errors == []


def _broker_up(settings: Settings) -> bool:
    try:
        connection = open_connection(settings, timeout_seconds=2)
    except Exception:
        return False
    close_connection(connection)
    return True


def _purge(settings: Settings, queue_name: str) -> None:
    connection = open_connection(settings, timeout_seconds=2)
    try:
        channel = connection.channel()
        declare_topology(channel)
        channel.queue_purge(queue_name)
    finally:
        close_connection(connection)


def _load_outbox(sessions, order_id: uuid.UUID) -> _OutboxView | None:
    session = sessions()
    try:
        row = session.scalar(
            select(OutboxRow).where(
                OutboxRow.aggregate_id == order_id,
                OutboxRow.event_type == "OrderCreated",
            )
        )
        if row is None:
            return None
        return _OutboxView(
            id=row.id,
            status=row.status,
            published_at=row.published_at,
            envelope_event_id=str(row.payload["event_id"]),
        )
    finally:
        session.close()

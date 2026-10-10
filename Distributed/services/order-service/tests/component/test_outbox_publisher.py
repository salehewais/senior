"""Publisher claims, confirms, and gives up. The fake stands in for SKIP LOCKED and the broker."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime

import pytest

from order_service.application.publishing import OutboundMessage
from order_service.infrastructure.messaging.outbox_publisher import PendingOutbox, publish_batch, run_publisher
from order_service.infrastructure.settings import Settings


@dataclass(frozen=True, slots=True)
class Stored:
    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    payload: dict
    created_at: datetime
    published_at: datetime | None
    retry_count: int
    status: str


class LockingOutbox:
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Stored] = {}
        self.locked: set[uuid.UUID] = set()

    def add(self, row: Stored) -> None:
        self.rows[row.id] = row

    def lease(self) -> _Lease:
        return _Lease(self)


class _Lease:
    def __init__(self, store: LockingOutbox) -> None:
        self._store = store
        self._mine: list[uuid.UUID] = []
        self._updates: dict[uuid.UUID, Stored] = {}
        self._closed = False

    def claim(self, limit: int) -> list[PendingOutbox]:
        pending = [
            row
            for row in self._store.rows.values()
            if row.status == "pending" and row.id not in self._store.locked
        ]
        pending.sort(key=lambda row: (row.created_at, row.id))
        chosen = pending[:limit]
        claimed: list[PendingOutbox] = []
        for row in chosen:
            self._store.locked.add(row.id)
            self._mine.append(row.id)
            claimed.append(
                PendingOutbox(
                    id=row.id,
                    event_type=row.event_type,
                    aggregate_type=row.aggregate_type,
                    aggregate_id=row.aggregate_id,
                    payload=row.payload,
                    retry_count=row.retry_count,
                    created_at=row.created_at,
                )
            )
        return claimed

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None:
        self._updates[event_id] = replace(
            self._store.rows[event_id],
            status="published",
            published_at=published_at,
        )

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        self._updates[event_id] = replace(
            self._store.rows[event_id],
            retry_count=retry_count,
            status=status,
            published_at=None,
        )

    def finish(self) -> None:
        if self._closed:
            return
        for event_id, updated in self._updates.items():
            self._store.rows[event_id] = updated
        self._unlock()
        self._closed = True

    def abort(self) -> None:
        if self._closed:
            return
        self._unlock()
        self._closed = True

    def _unlock(self) -> None:
        for event_id in self._mine:
            self._store.locked.discard(event_id)
        self._mine.clear()


class ProbeBroker:
    def __init__(self, store: LockingOutbox) -> None:
        self.store = store
        self.sent: list[OutboundMessage] = []
        self.saw_pending = True

    def publish(self, message: OutboundMessage) -> None:
        self.saw_pending = self.saw_pending and self.store.rows[message.event_id].status == "pending"
        self.sent.append(message)


class ExplodingBroker:
    def __init__(self, message: str) -> None:
        self.message = message
        self.attempts = 0

    def publish(self, message: OutboundMessage) -> None:
        self.attempts += 1
        raise ConnectionError(self.message)


def _envelope(event_id: uuid.UUID, event_type: str, *, email: str | None = None) -> dict:
    payload: dict = {"aggregate_version": 1}
    if email is not None:
        payload["email"] = email
    return {
        "event_id": str(event_id),
        "event_type": event_type,
        "occurred_at": "2026-10-08T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "causation_id": str(uuid.uuid4()),
        "version": 1,
        "payload": payload,
    }


def _row(event_type: str, created_at: datetime, *, email: str | None = None, retry_count: int = 0) -> Stored:
    event_id = uuid.uuid4()
    envelope = _envelope(event_id, event_type, email=email)
    return Stored(
        id=event_id,
        event_type=event_type,
        aggregate_type="customer" if event_type == "CustomerUpdated" else "order",
        aggregate_id=uuid.UUID(str(envelope["aggregate_id"])),
        payload=envelope,
        created_at=created_at,
        published_at=None,
        retry_count=retry_count,
        status="pending",
    )


def _now() -> datetime:
    return datetime(2026, 10, 8, 12, 5, tzinfo=UTC)


def test_row_stays_pending_until_the_broker_confirms() -> None:
    store = LockingOutbox()
    row = _row("OrderCreated", datetime(2026, 10, 8, 12, 0, tzinfo=UTC))
    store.add(row)
    broker = ProbeBroker(store)
    claimed = publish_batch(store.lease(), broker, limit=100, max_attempts=5, now=_now)
    assert claimed == 1
    assert broker.saw_pending
    assert [message.event_id for message in broker.sent] == [row.id]
    assert broker.sent[0].routing_key == "order.created"
    assert broker.sent[0].body["event_id"] == str(row.id)
    stored = store.rows[row.id]
    assert stored.status == "published"
    assert stored.published_at == _now()
    assert stored.retry_count == 0
    # A second claim does not invent a new event_id or send the row again.
    again = ProbeBroker(store)
    assert publish_batch(store.lease(), again, limit=100, max_attempts=5, now=_now) == 0
    assert again.sent == []


def test_broker_error_keeps_the_row_pending_and_counts_the_attempt(caplog: pytest.LogCaptureFixture) -> None:
    store = LockingOutbox()
    row = _row("CustomerUpdated", datetime(2026, 10, 8, 12, 0, tzinfo=UTC), email="ada@example.com")
    store.add(row)
    broker = ExplodingBroker("payload email=ada@example.com")
    with caplog.at_level(logging.WARNING):
        publish_batch(store.lease(), broker, limit=100, max_attempts=5, now=_now)
    stored = store.rows[row.id]
    assert stored.status == "pending"
    assert stored.retry_count == 1
    assert stored.published_at is None
    assert broker.attempts == 1
    assert "ada@example.com" not in caplog.text
    assert str(row.id) in caplog.text
    assert str(row.payload["correlation_id"]) in caplog.text
    assert row.event_type in caplog.text


def test_max_attempts_marks_the_row_failed_and_stops(caplog: pytest.LogCaptureFixture) -> None:
    store = LockingOutbox()
    row = _row("OrderCreated", datetime(2026, 10, 8, 12, 0, tzinfo=UTC), retry_count=4)
    store.add(row)
    broker = ExplodingBroker("email=ada@example.com down")
    with caplog.at_level(logging.ERROR):
        publish_batch(store.lease(), broker, limit=100, max_attempts=5, now=_now)
    stored = store.rows[row.id]
    assert stored.status == "failed"
    assert stored.retry_count == 5
    assert stored.published_at is None
    assert "ada@example.com" not in caplog.text
    assert "not the consumer DLQ" in caplog.text
    again = ExplodingBroker("again")
    assert publish_batch(store.lease(), again, limit=100, max_attempts=5, now=_now) == 0
    assert again.attempts == 0


def test_second_claim_skips_a_row_another_worker_locked() -> None:
    store = LockingOutbox()
    older = _row("OrderCreated", datetime(2026, 10, 8, 12, 0, tzinfo=UTC))
    newer = _row("OrderConfirmed", datetime(2026, 10, 8, 12, 1, tzinfo=UTC))
    store.add(older)
    store.add(newer)
    second_sent: list[uuid.UUID] = []

    class FirstBroker:
        def publish(self, message: OutboundMessage) -> None:
            assert store.rows[message.event_id].status == "pending"
            assert message.event_id == older.id
            publish_batch(store.lease(), _Second(), limit=1, max_attempts=5, now=_now)

    class _Second:
        def publish(self, message: OutboundMessage) -> None:
            second_sent.append(message.event_id)
            assert store.rows[message.event_id].status == "pending"

    publish_batch(store.lease(), FirstBroker(), limit=1, max_attempts=5, now=_now)
    assert second_sent == [newer.id]
    assert store.rows[older.id].status == "published"
    assert store.rows[newer.id].status == "published"
    assert older.id not in second_sent


def test_shutdown_finishes_one_batch_and_does_not_claim_another() -> None:
    import threading

    stop = threading.Event()
    calls: list[int] = []

    def _one_batch(_sessions, _broker, _settings) -> int:
        calls.append(1)
        stop.set()
        return 1

    class _Broker:
        def publish(self, message: OutboundMessage) -> None:
            raise AssertionError(message.event_id)

    run_publisher(
        Settings(outbox_poll_interval_seconds=30),
        session_factory=None,  # type: ignore[arg-type]
        broker=_Broker(),  # type: ignore[arg-type]
        stop=stop,
        publish_pending=_one_batch,
    )
    assert calls == [1]

    stop.set()
    calls.clear()
    run_publisher(
        Settings(outbox_poll_interval_seconds=30),
        session_factory=None,  # type: ignore[arg-type]
        broker=_Broker(),  # type: ignore[arg-type]
        stop=stop,
        publish_pending=_one_batch,
    )
    assert calls == []

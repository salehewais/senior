"""Duplicate event_id, retry budget, and permanent failures. No broker required."""

import copy
import json
import uuid
from datetime import UTC, datetime

from order_service.application.consuming import (
    CONSUMER_ORDER_INVENTORY,
    HEADER_RETRY_COUNT,
    INVENTORY_EVENT_TYPES,
    REASON_RETRIES_EXHAUSTED,
    DeliveryOutcome,
    ProcessedEvent,
    apply_once,
)
from order_service.application.inventory_update import apply_inventory_payload
from order_service.domain.entities.inventory_snapshot import InventorySnapshot
from order_service.domain.ids import ProductId
from order_service.infrastructure.messaging.consumer import settle_delivery


class FakeChannel:
    def __init__(self) -> None:
        self.acked: list[int] = []
        self.nacked: list[tuple[int, bool]] = []

    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None:
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None:
        self.nacked.append((delivery_tag, requeue))


class FakeRouter:
    def __init__(self) -> None:
        self.retries: list[int] = []
        self.dead: list[str] = []

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        self.retries.append(attempt)

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None:
        self.dead.append(reason)


class MemoryStore:
    def __init__(self) -> None:
        self.events: dict[uuid.UUID, ProcessedEvent] = {}
        self.snapshots: dict[ProductId, InventorySnapshot] = {}
        self._pending_event: ProcessedEvent | None = None
        self._pending_snapshots: dict[ProductId, InventorySnapshot] = {}

    def insert_if_new(self, record: ProcessedEvent) -> bool:
        if record.event_id in self.events:
            return False
        self._pending_event = record
        return True

    def get_snapshot(self, product_id: ProductId) -> InventorySnapshot | None:
        source = self._pending_snapshots.get(product_id, self.snapshots.get(product_id))
        if source is None:
            return None
        return copy.copy(source)

    def save_snapshot(self, snapshot: InventorySnapshot, updated_at: datetime) -> None:
        del updated_at
        self._pending_snapshots[snapshot.product_id] = snapshot

    def commit(self) -> None:
        if self._pending_event is not None:
            self.events[self._pending_event.event_id] = self._pending_event
        self.snapshots.update(self._pending_snapshots)
        self._pending_event = None
        self._pending_snapshots = {}

    def rollback(self) -> None:
        self._pending_event = None
        self._pending_snapshots = {}


def _record(event_id: uuid.UUID, aggregate_id: uuid.UUID) -> ProcessedEvent:
    return ProcessedEvent(
        event_id=event_id,
        event_type="InventoryUpdated",
        aggregate_id=aggregate_id,
        processed_at=datetime(2026, 10, 8, tzinfo=UTC),
        consumer_name=CONSUMER_ORDER_INVENTORY,
    )


def _inventory_body(*, event_id: uuid.UUID, product_id: uuid.UUID, version: int, on_hand: int) -> dict[str, object]:
    return {
        "event_id": str(event_id),
        "event_type": "InventoryUpdated",
        "version": 1,
        "aggregate_id": str(product_id),
        "correlation_id": str(uuid.uuid4()),
        "payload": {
            "product_id": str(product_id),
            "sku": "MUG-01",
            "quantity_on_hand": on_hand,
            "quantity_reserved": 1,
            "warehouse_code": "MAIN",
            "aggregate_version": version,
        },
    }


def test_duplicate_event_id_does_not_apply_twice() -> None:
    store = MemoryStore()
    event_id = uuid.uuid4()
    product_id = uuid.uuid4()
    record = _record(event_id, product_id)
    body = _inventory_body(event_id=event_id, product_id=product_id, version=4, on_hand=10)
    calls: list[int] = []

    def effect() -> None:
        calls.append(1)
        apply_inventory_payload(body, store, updated_at=record.processed_at)

    assert apply_once(store, record, effect).outcome is DeliveryOutcome.SUCCESS
    second = apply_once(store, record, effect)
    assert second.outcome is DeliveryOutcome.SUCCESS
    assert second.reason == "duplicate"
    assert calls == [1]
    assert store.snapshots[ProductId(product_id)].on_hand.value == 10
    assert len(store.events) == 1


def test_transient_failure_does_not_record_the_event() -> None:
    store = MemoryStore()
    event_id = uuid.uuid4()
    record = _record(event_id, uuid.uuid4())

    def boom() -> None:
        raise RuntimeError("database unavailable")

    failed = apply_once(store, record, boom)
    assert failed.outcome is DeliveryOutcome.TRANSIENT
    assert store.events == {}
    assert apply_once(store, record, lambda: None).outcome is DeliveryOutcome.SUCCESS

    def should_not_run() -> None:
        raise AssertionError("second apply")

    assert apply_once(store, record, should_not_run).reason == "duplicate"


def test_older_snapshot_is_acked_and_ignored() -> None:
    store = MemoryStore()
    product_id = uuid.uuid4()
    first_id = uuid.uuid4()
    stale_id = uuid.uuid4()
    first = _inventory_body(event_id=first_id, product_id=product_id, version=4, on_hand=10)
    stale = _inventory_body(event_id=stale_id, product_id=product_id, version=2, on_hand=99)
    when = datetime(2026, 10, 8, tzinfo=UTC)
    first_result = apply_once(
        store,
        _record(first_id, product_id),
        lambda: apply_inventory_payload(first, store, updated_at=when),
    )
    stale_result = apply_once(
        store,
        _record(stale_id, product_id),
        lambda: apply_inventory_payload(stale, store, updated_at=when),
    )
    assert first_result.outcome is DeliveryOutcome.SUCCESS
    assert stale_result.outcome is DeliveryOutcome.SUCCESS
    saved = store.snapshots[ProductId(product_id)]
    assert saved.source_version == 4
    assert saved.on_hand.value == 10
    assert set(store.events) == {first_id, stale_id}


def test_after_max_attempts_a_transient_failure_is_dead_lettered() -> None:
    channel = FakeChannel()
    router = FakeRouter()
    body = json.dumps(
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "InventoryUpdated",
            "version": 1,
            "aggregate_id": str(uuid.uuid4()),
        }
    ).encode()
    settle_delivery(
        channel,
        5,
        body,
        lambda _envelope: DeliveryOutcome.TRANSIENT,
        router=router,
        headers={HEADER_RETRY_COUNT: 5},
        accepted_event_types=INVENTORY_EVENT_TYPES,
    )
    assert router.retries == []
    assert router.dead == [REASON_RETRIES_EXHAUSTED]
    assert channel.acked == [5]
    assert channel.nacked == []


def _must_not_run(_envelope: dict) -> None:
    raise AssertionError("handler must not run")


def test_malformed_json_is_permanent_and_skips_the_retry_budget() -> None:
    channel = FakeChannel()
    router = FakeRouter()
    settle_delivery(
        channel,
        2,
        b"{not-json",
        _must_not_run,
        router=router,
        headers={HEADER_RETRY_COUNT: 0},
        accepted_event_types=INVENTORY_EVENT_TYPES,
    )
    assert router.dead == ["malformed-envelope"]
    assert router.retries == []
    assert channel.nacked == []


def test_unknown_type_and_schema_version_are_permanent() -> None:
    channel = FakeChannel()
    router = FakeRouter()
    product_id = str(uuid.uuid4())
    unknown_type = json.dumps(
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "NotACatalogEvent",
            "version": 1,
            "aggregate_id": product_id,
        }
    ).encode()
    unknown_version = json.dumps(
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "InventoryUpdated",
            "version": 2,
            "aggregate_id": product_id,
        }
    ).encode()
    settle_delivery(
        channel,
        1,
        unknown_type,
        _must_not_run,
        router=router,
        accepted_event_types=INVENTORY_EVENT_TYPES,
    )
    settle_delivery(
        channel,
        2,
        unknown_version,
        _must_not_run,
        router=router,
        accepted_event_types=INVENTORY_EVENT_TYPES,
    )
    assert router.dead == ["unknown-event-type", "unknown-schema-version"]
    assert router.retries == []


def test_invalid_inventory_payload_is_permanent_and_not_recorded() -> None:
    store = MemoryStore()
    event_id = uuid.uuid4()
    product_id = uuid.uuid4()
    body = _inventory_body(event_id=event_id, product_id=product_id, version=1, on_hand=1)
    payload = body["payload"]
    assert isinstance(payload, dict)
    payload["quantity_on_hand"] = -1
    result = apply_once(
        store,
        _record(event_id, product_id),
        lambda: apply_inventory_payload(body, store, updated_at=datetime(2026, 10, 8, tzinfo=UTC)),
    )
    assert result.outcome is DeliveryOutcome.PERMANENT
    assert store.events == {}
    assert store.snapshots == {}

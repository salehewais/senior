"""Duplicate delivery, retry, and dead-letter. No broker and no Postgres."""

from __future__ import annotations

import json
import uuid

from tests.conftest import confirmed_body

from notification_service.domain.outcomes import REASON_DUPLICATE, REASON_RETRIES_EXHAUSTED
from notification_service.messaging.envelope import inspect_envelope
from notification_service.messaging.settlement import settle_delivery
from notification_service.persistence.store import MemoryStore
from notification_service.services.channels import MockEmail, MockPush
from notification_service.services.notifications import apply_notification


class FakeChannel:
    def __init__(self) -> None:
        self.acked: list[int] = []
        self.nacked: list[tuple[int, bool]] = []

    def basic_ack(self, delivery_tag: int = 0, multiple: bool = False) -> None:
        del multiple
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag: int = 0, multiple: bool = False, requeue: bool = True) -> None:
        del multiple
        self.nacked.append((delivery_tag, requeue))


class FakeRouter:
    def __init__(self) -> None:
        self.retries: list[int] = []
        self.dead: list[str] = []

    def schedule_retry(self, *, attempt: int, body: bytes, original_routing_key: str, reason: str) -> None:
        del body, original_routing_key, reason
        self.retries.append(attempt)

    def dead_letter(self, *, body: bytes, original_routing_key: str, reason: str, retry_count: int) -> None:
        del body, original_routing_key, retry_count
        self.dead.append(reason)


def test_duplicate_event_is_not_delivered_twice() -> None:
    store = MemoryStore()
    account_id = uuid.uuid4()
    store.register_token(account_id, "device-1", "android")
    email = MockEmail()
    push = MockPush()
    body = confirmed_body(uuid.uuid4(), account_id)
    inspected = inspect_envelope(body)
    assert not isinstance(inspected, Exception)
    first = apply_notification(inspected, store, email, push)
    second = apply_notification(inspected, store, email, push)
    assert first.reason == ""
    assert second.reason == REASON_DUPLICATE
    assert email.attempts == 1
    assert push.attempts == 1
    assert len(store.deliveries) == 2
    assert {row.channel for row in store.deliveries} == {"email", "push"}


def test_duplicate_delivery_is_acked_once() -> None:
    store = MemoryStore()
    account_id = uuid.uuid4()
    store.register_token(account_id, "device-1", "android")
    email = MockEmail()
    push = MockPush()
    body = confirmed_body(uuid.uuid4(), account_id)

    def handler(parsed):
        return apply_notification(parsed, store, email, push)

    first_channel = FakeChannel()
    first_router = FakeRouter()
    settle_delivery(
        first_channel,
        1,
        body,
        handler,
        router=first_router,
        routing_key="order.confirmed",
    )
    assert first_channel.acked == [1]
    assert first_channel.nacked == []
    assert first_router.retries == []
    assert first_router.dead == []

    second_channel = FakeChannel()
    second_router = FakeRouter()
    settle_delivery(
        second_channel,
        2,
        body,
        handler,
        router=second_router,
        routing_key="order.confirmed",
    )
    assert second_channel.acked == [2]
    assert len(second_channel.acked) == 1
    assert second_channel.nacked == []
    assert second_router.retries == []
    assert second_router.dead == []
    assert email.attempts == 1
    assert push.attempts == 1
    assert len(store.deliveries) == 2


def test_mock_email_and_push_record_the_delivery() -> None:
    store = MemoryStore()
    account_id = uuid.uuid4()
    store.register_token(account_id, "push-token", "ios")
    email = MockEmail()
    push = MockPush()
    inspected = inspect_envelope(confirmed_body(uuid.uuid4(), account_id))
    result = apply_notification(inspected, store, email, push)
    assert result.reason == ""
    email_row = next(row for row in store.deliveries if row.channel == "email")
    push_row = next(row for row in store.deliveries if row.channel == "push")
    assert email_row.account_id == account_id
    assert email_row.destination == f"account:{account_id}"
    assert email_row.summary == "OrderConfirmed"
    assert push_row.destination == "push-token"
    assert push_row.summary == "OrderConfirmed"


def test_failing_mock_adapter_retries_then_dead_letters() -> None:
    store = MemoryStore()
    account_id = uuid.uuid4()
    email = MockEmail(fail=True)
    push = MockPush()
    body = confirmed_body(uuid.uuid4(), account_id)
    inspected = inspect_envelope(body)

    def handler(parsed):
        return apply_notification(parsed, store, email, push)

    for already in range(5):
        channel = FakeChannel()
        router = FakeRouter()
        headers = {"x-retry-count": already} if already else None
        settle_delivery(
            channel,
            already + 1,
            body,
            handler,
            router=router,
            headers=headers,
            routing_key="order.confirmed",
        )
        assert channel.nacked == []
        assert channel.acked == [already + 1]
        assert router.dead == []
        assert router.retries == [already + 1]
    channel = FakeChannel()
    router = FakeRouter()
    settle_delivery(
        channel,
        6,
        body,
        handler,
        router=router,
        headers={"x-retry-count": 5},
        routing_key="order.confirmed",
    )
    assert router.retries == []
    assert router.dead == [REASON_RETRIES_EXHAUSTED]
    assert channel.acked == [6]
    assert channel.nacked == []
    assert store.deliveries == []
    assert store.processed == {}
    assert email.attempts == 6
    assert push.attempts == 0
    assert json.loads(body)["event_type"] == inspected.event_type

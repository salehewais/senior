"""Ack is manual. A failure is routed onward and never requeued in place."""

import json
import logging
import uuid

import pytest

from order_service.application.consuming import HEADER_RETRY_COUNT, DeliveryOutcome
from order_service.infrastructure.messaging.consumer import (
    PREFETCH_COUNT,
    LoggingEventHandler,
    settle_delivery,
)


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


def _envelope(**overrides: object) -> bytes:
    body: dict[str, object] = {
        "event_id": str(uuid.uuid4()),
        "event_type": "OrderCreated",
        "version": 1,
        "aggregate_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
    }
    body.update(overrides)
    return json.dumps(body).encode()


def test_prefetch_is_the_documented_starting_value() -> None:
    assert PREFETCH_COUNT == 10


def test_handler_success_acks() -> None:
    channel = FakeChannel()
    seen: list[dict] = []
    settle_delivery(channel, 4, _envelope(), seen.append, router=FakeRouter())
    assert channel.acked == [4]
    assert channel.nacked == []
    assert seen[0]["event_type"] == "OrderCreated"


def test_handler_failure_schedules_retry_and_does_not_requeue(caplog: pytest.LogCaptureFixture) -> None:
    channel = FakeChannel()
    router = FakeRouter()

    def boom(_envelope: dict) -> None:
        raise RuntimeError("projection failed email=secret@example.com")

    with caplog.at_level(logging.ERROR):
        body = _envelope(
            event_id="018f1c2a-7b3d-7c11-8a22-111111111111",
            correlation_id="018f1c2a-3333-7c11-8a22-444444444444",
        )
        settle_delivery(channel, 7, body, boom, router=router)
    assert channel.acked == [7]
    assert channel.nacked == []
    assert router.retries == [1]
    assert router.dead == []
    assert "018f1c2a-7b3d-7c11-8a22-111111111111" in caplog.text
    assert "secret@example.com" not in caplog.text


def test_unreadable_body_is_dead_lettered_and_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    channel = FakeChannel()
    router = FakeRouter()
    with caplog.at_level(logging.ERROR):
        settle_delivery(channel, 1, b'{"email":"secret@example.com"', lambda _envelope: None, router=router)
    assert channel.acked == [1]
    assert channel.nacked == []
    assert router.dead == ["malformed-envelope"]
    assert router.retries == []
    assert "secret@example.com" not in caplog.text


def test_body_event_id_wins_over_amqp_message_id() -> None:
    channel = FakeChannel()
    seen: list[dict] = []
    event_id = "018f1c2a-7b3d-7c11-8a22-111111111111"
    settle_delivery(
        channel,
        3,
        _envelope(event_id=event_id),
        seen.append,
        router=FakeRouter(),
        property_message_id="not-the-body",
    )
    assert seen[0]["event_id"] == event_id
    assert channel.acked == [3]


def test_logging_handler_omits_the_payload(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        LoggingEventHandler()(
            {
                "event_type": "CustomerUpdated",
                "event_id": "e-2",
                "correlation_id": "c-2",
                "aggregate_id": "a-2",
                "payload": {"email": "secret@example.com"},
            }
        )
    assert "CustomerUpdated" in caplog.text
    assert "secret@example.com" not in caplog.text


def test_explicit_transient_uses_the_retry_header() -> None:
    channel = FakeChannel()
    router = FakeRouter()
    settle_delivery(
        channel,
        9,
        _envelope(),
        lambda _envelope: DeliveryOutcome.TRANSIENT,
        router=router,
        headers={HEADER_RETRY_COUNT: 2},
    )
    assert router.retries == [3]
    assert channel.nacked == []
    assert channel.acked == [9]

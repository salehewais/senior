"""Envelope inspection without Django or a broker."""

from __future__ import annotations

import json
import uuid

from projections.domain.envelope import EnvelopeRejection, ParsedEnvelope, inspect_envelope
from projections.domain.outcomes import REASON_MALFORMED, REASON_UNKNOWN_TYPE


def _body(**overrides: object) -> bytes:
    order_id = str(uuid.uuid4())
    document: dict[str, object] = {
        "event_id": str(uuid.uuid4()),
        "event_type": "OrderCreated",
        "occurred_at": "2026-10-08T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": order_id,
        "correlation_id": str(uuid.uuid4()),
        "causation_id": str(uuid.uuid4()),
        "version": 1,
        "payload": {"order_id": order_id, "aggregate_version": 1},
    }
    document.update(overrides)
    return json.dumps(document).encode("utf-8")


def test_inspect_envelope_reads_identity_from_the_json_body() -> None:
    inspected = inspect_envelope(_body())
    assert isinstance(inspected, ParsedEnvelope)
    assert inspected.event_type == "OrderCreated"


def test_malformed_json_is_rejected() -> None:
    inspected = inspect_envelope(b"not-json")
    assert isinstance(inspected, EnvelopeRejection)
    assert inspected.reason == REASON_MALFORMED


def test_unknown_event_type_is_rejected() -> None:
    inspected = inspect_envelope(_body(event_type="OrderCorrected"))
    assert isinstance(inspected, EnvelopeRejection)
    assert inspected.reason == REASON_UNKNOWN_TYPE

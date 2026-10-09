"""Cardinality and redaction. A sample must not accept a forbidden label."""

import json
import logging
import uuid
from datetime import UTC, datetime

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from order_service.application.publishing import to_outbound
from order_service.domain.events import CustomerUpdated
from order_service.observability.jsonlog import JsonFormatter
from order_service.observability.metrics import (
    FORBIDDEN_LABELS,
    declared_metrics,
    define_counter,
    inc,
    orders_created_total,
)


def test_defining_a_metric_rejects_a_forbidden_label() -> None:
    with pytest.raises(ValueError, match="order_id"):
        define_counter("unit_forbidden_order_id_total", "must not be created", ("service", "order_id"))


def test_recording_a_sample_rejects_a_forbidden_label() -> None:
    before = orders_created_total._value.get()
    with pytest.raises(ValueError, match="email"):
        inc(orders_created_total, email="ada@example.com")
    assert orders_created_total._value.get() == before
    for metric in orders_created_total.collect():
        for sample in metric.samples:
            assert "email" not in sample.labels
            assert "ada@example.com" not in sample.labels.values()


def test_declared_metrics_have_no_forbidden_labels() -> None:
    for metric in declared_metrics():
        assert not FORBIDDEN_LABELS.intersection(metric._labelnames)


def test_password_like_field_is_not_emitted() -> None:
    stream_text: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            stream_text.append(self.format(record))

    handler = _Capture()
    handler.setFormatter(JsonFormatter("order-service"))
    logger = logging.getLogger("test.observability.redaction")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.info(
        "login password=%s authorization=%s",
        "hunter2-secret",
        "Bearer eyJsecret",
        extra={"password": "hunter2-secret", "authorization": "Bearer eyJsecret"},
    )
    assert len(stream_text) == 1
    line = stream_text[0]
    assert "hunter2-secret" not in line
    assert "eyJsecret" not in line
    payload = json.loads(line)
    assert payload["service"] == "order-service"
    assert payload["level"] == "INFO"
    assert "timestamp" in payload
    assert payload["message"]
    assert "password" not in payload
    assert "authorization" not in payload


def test_traceparent_does_not_replace_correlation_id() -> None:
    provider = TracerProvider()
    try:
        trace.set_tracer_provider(provider)
    except Exception:
        provider = trace.get_tracer_provider()
    correlation_id = uuid.UUID("018f1c2a-3333-7c11-8a22-444444444444")
    event = CustomerUpdated(
        event_id=uuid.uuid4(),
        occurred_at=datetime(2026, 10, 9, tzinfo=UTC),
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        correlation_id=correlation_id,
        causation_id=uuid.uuid4(),
        email="ada@example.com",
        display_name="Ada",
    )
    tracer = trace.get_tracer("test.observability")
    with tracer.start_as_current_span("order.request"):
        message = to_outbound(event)
    assert message.body["correlation_id"] == str(correlation_id)
    traceparent = message.body.get("traceparent")
    assert isinstance(traceparent, str)
    assert str(correlation_id) not in traceparent
    assert "ada@example.com" not in traceparent

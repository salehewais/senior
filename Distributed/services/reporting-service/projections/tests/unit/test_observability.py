"""Reporting metrics reject forbidden labels, and logs drop password-like values."""

import json
import logging

import pytest

from projections.observability.jsonlog import JsonFormatter
from projections.observability.metrics import (
    FORBIDDEN_LABELS,
    declared_metrics,
    define_counter,
    inc,
    messages_failed_total,
)


def test_defining_a_metric_rejects_a_forbidden_label() -> None:
    with pytest.raises(ValueError, match="message_id"):
        define_counter("reporting_forbidden_message_total", "must not be created", ("message_id",))


def test_recording_a_sample_rejects_a_forbidden_label() -> None:
    with pytest.raises(ValueError, match="email"):
        inc(messages_failed_total, service="reporting-service", event_type="OrderCreated", email="ada@example.com")


def test_declared_metrics_have_no_forbidden_labels() -> None:
    for metric in declared_metrics():
        assert not FORBIDDEN_LABELS.intersection(metric._labelnames)


def test_password_like_field_is_not_emitted() -> None:
    lines: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            lines.append(self.format(record))

    handler = _Capture()
    handler.setFormatter(JsonFormatter("reporting-service"))
    logger = logging.getLogger("test.reporting.redaction")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.info("login password=%s", "hunter2-secret", extra={"password": "hunter2-secret"})
    payload = json.loads(lines[0])
    assert "hunter2-secret" not in lines[0]
    assert payload["service"] == "reporting-service"
    assert payload["level"] == "INFO"
    assert "timestamp" in payload
    assert "password" not in payload

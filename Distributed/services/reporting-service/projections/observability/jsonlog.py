"""JSON logs for the reporting service.

Do not log passwords, JWT secrets, database passwords, Authorization headers,
or full customer payloads. Allow-listed fields only. correlation_id is not
replaced by trace_id.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime

_FIELDS = (
    "request_id",
    "correlation_id",
    "trace_id",
    "span_id",
    "event_id",
    "event_type",
    "http_method",
    "http_route",
    "http_status",
    "error_type",
)

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|secret|authorization|database_password|jwt_secret|jwt|token)"
    r"(\s*[:=]\s*)(?:Bearer\s+\S+|\S+)"
)


def scrub_text(text: str) -> str:
    return _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}[redacted]", text)


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str = "reporting-service") -> None:
        super().__init__()
        self._service = service

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "service": self._service,
            "level": record.levelname,
            "message": scrub_text(record.getMessage()),
        }
        for key in _FIELDS:
            value = getattr(record, key, None)
            if value is not None and value != "":
                payload[key] = value
        trace_id, span_id = _span_ids()
        if trace_id and "trace_id" not in payload:
            payload["trace_id"] = trace_id
        if span_id and "span_id" not in payload:
            payload["span_id"] = span_id
        return json.dumps(payload, default=str, separators=(",", ":"))


def _span_ids() -> tuple[str, str]:
    try:
        from opentelemetry import trace
    except ImportError:
        return "", ""
    context = trace.get_current_span().get_span_context()
    if not context.is_valid:
        return "", ""
    return format(context.trace_id, "032x"), format(context.span_id, "016x")

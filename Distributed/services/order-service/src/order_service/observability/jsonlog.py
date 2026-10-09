"""One JSON object per log line.

Do not log passwords, JWT secrets, database passwords, Authorization headers,
or full customer payloads. The formatter drops fields that are not on the
allow-list and redacts password-like assignments that reach the message text.
`correlation_id` stays the business id. `trace_id` is added only when a span
is current. One does not replace the other.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime

from order_service.observability.context import (
    correlation_id_var,
    event_id_var,
    event_type_var,
    request_id_var,
)

# Keys that may appear on the JSON line. Anything else on the record is ignored,
# including password, authorization, token, and customer payload fields.
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

_configured = False


def scrub_text(text: str) -> str:
    """Replace values assigned to password-like names. The name itself stays."""

    return _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}[redacted]", text)


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str) -> None:
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
            value = _field(record, key)
            if value is not None and value != "":
                payload[key] = value
        trace_id, span_id = _span_ids()
        if trace_id and "trace_id" not in payload:
            payload["trace_id"] = trace_id
        if span_id and "span_id" not in payload:
            payload["span_id"] = span_id
        if record.exc_info:
            payload["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else "error"
        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(service: str) -> None:
    """Attach the JSON formatter once per process. Other handlers, such as pytest, stay."""

    global _configured
    if _configured:
        return
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(service))
    root.addHandler(handler)
    _configured = True


def _field(record: logging.LogRecord, key: str) -> object | None:
    if key == "request_id":
        return getattr(record, key, None) or request_id_var.get()
    if key == "correlation_id":
        return getattr(record, key, None) or correlation_id_var.get()
    if key == "event_id":
        return getattr(record, key, None) or event_id_var.get()
    if key == "event_type":
        return getattr(record, key, None) or event_type_var.get()
    return getattr(record, key, None)


def _span_ids() -> tuple[str, str]:
    try:
        from opentelemetry import trace
    except ImportError:
        return "", ""
    span = trace.get_current_span()
    context = span.get_span_context()
    if not context.is_valid:
        return "", ""
    return format(context.trace_id, "032x"), format(context.span_id, "016x")

"""Ids for the request or message currently being handled.

These are log fields. They are not Prometheus labels.
"""

from __future__ import annotations

from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
event_id_var: ContextVar[str] = ContextVar("event_id", default="")
event_type_var: ContextVar[str] = ContextVar("event_type", default="")

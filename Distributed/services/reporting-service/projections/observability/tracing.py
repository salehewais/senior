"""Trace the reporting consumer. Django and Odoo are not auto-instrumented.

The order HTTP span, the Postgres span, and the outbox publish span are the
order-service path. This module only continues traceparent on a consumed
message so that span can sit in the same trace. A missing collector does not
stop projection.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager

_configured = False


def configure_tracing(service_name: str) -> None:
    global _configured
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint or _configured:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return
    name = os.environ.get("OTEL_SERVICE_NAME", "").strip() or service_name
    insecure_endpoint = endpoint.removeprefix("http://").removeprefix("https://").rstrip("/")
    provider = TracerProvider(resource=Resource.create({"service.name": name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=insecure_endpoint, insecure=True)))
    trace.set_tracer_provider(provider)
    _configured = True


@contextmanager
def consumer_span(headers: Mapping[str, object] | None, body: bytes, *, event_type: str) -> Iterator[None]:
    try:
        from opentelemetry import trace
        from opentelemetry.propagate import extract
        from opentelemetry.trace import SpanKind
    except ImportError:
        yield
        return
    carrier = _carrier(headers)
    if "traceparent" not in carrier:
        carrier.update(_carrier_from_body(body))
    try:
        context = extract(carrier)
        tracer = trace.get_tracer("reporting.consumer")
        span_cm = tracer.start_as_current_span("consume", context=context, kind=SpanKind.CONSUMER)
    except Exception:
        yield
        return
    with span_cm as span:
        if span.is_recording():
            span.set_attribute("messaging.system", "rabbitmq")
            span.set_attribute("messaging.operation", "process")
            span.set_attribute("event_type", event_type)
        yield


def _carrier(mapping: Mapping[str, object] | None) -> dict[str, str]:
    carrier: dict[str, str] = {}
    if not mapping:
        return carrier
    folded = {str(key).lower(): value for key, value in mapping.items()}
    for key in ("traceparent", "tracestate"):
        value = folded.get(key)
        if isinstance(value, bytes):
            value = value.decode("utf-8", "replace")
        if isinstance(value, str) and value:
            carrier[key] = value
    return carrier


def _carrier_from_body(body: bytes) -> dict[str, str]:
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    return _carrier(parsed)

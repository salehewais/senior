"""OpenTelemetry for the order path.

The collector is not on the checkout path. If `OTEL_EXPORTER_OTLP_ENDPOINT` is
empty, or the collector is down, spans are dropped and the order still commits.
`X-Correlation-Id` is not the trace id. The envelope keeps `correlation_id`
and, when a span is current, also `traceparent`.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager

_configured = False


def configure_tracing(service_name: str, engine: object | None = None) -> None:
    """Export OTLP/gRPC when the endpoint is set. Otherwise leave the no-op tracer in place."""

    global _configured
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint:
        return
    if _configured:
        _instrument_engine(engine)
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
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=insecure_endpoint, insecure=True))
    )
    trace.set_tracer_provider(provider)
    _configured = True
    _instrument_engine(engine)


def instrument_fastapi(app: object) -> None:
    if not _configured:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        return
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")


def _instrument_engine(engine: object | None) -> None:
    if engine is None or not _configured:
        return
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    except ImportError:
        return
    SQLAlchemyInstrumentor().instrument(engine=engine)


def current_trace_carrier() -> dict[str, str]:
    """W3C headers for the active span. Empty when there is no span."""

    try:
        from opentelemetry import trace
        from opentelemetry.propagate import inject
    except ImportError:
        return {}
    span = trace.get_current_span()
    if not span.get_span_context().is_valid:
        return {}
    carrier: dict[str, str] = {}
    inject(carrier)
    return {key: value for key, value in carrier.items() if key in {"traceparent", "tracestate"} and value}


@contextmanager
def publisher_span(body: Mapping[str, object], event_type: str) -> Iterator[dict[str, str]]:
    """Child of the trace stored on the envelope. Yields AMQP headers for the broker."""

    headers: dict[str, str] = {}
    try:
        from opentelemetry import trace
        from opentelemetry.propagate import extract, inject
        from opentelemetry.trace import SpanKind
    except ImportError:
        yield headers
        return
    carrier = _carrier_from_mapping(body)
    try:
        context = extract(carrier)
        tracer = trace.get_tracer("order_service.outbox")
        span_cm = tracer.start_as_current_span(
            "outbox.publish",
            context=context,
            kind=SpanKind.PRODUCER,
        )
    except Exception:
        yield headers
        return
    with span_cm as span:
        if span.is_recording():
            span.set_attribute("messaging.system", "rabbitmq")
            span.set_attribute("messaging.destination.name", "commerce.events")
            span.set_attribute("event_type", event_type if isinstance(event_type, str) else "unknown")
        inject(headers)
        yield {key: value for key, value in headers.items() if key in {"traceparent", "tracestate"}}


@contextmanager
def consumer_span(
    headers: Mapping[str, object] | None,
    body: bytes,
    *,
    event_type: str,
) -> Iterator[None]:
    """Continue the publisher's traceparent. Fall back to the envelope so a retry still links."""

    try:
        from opentelemetry import trace
        from opentelemetry.propagate import extract
        from opentelemetry.trace import SpanKind
    except ImportError:
        yield
        return
    carrier = _carrier_from_mapping(headers or {})
    if "traceparent" not in carrier:
        carrier.update(_carrier_from_body(body))
    try:
        context = extract(carrier)
        tracer = trace.get_tracer("order_service.consumer")
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


def _carrier_from_mapping(mapping: Mapping[str, object] | None) -> dict[str, str]:
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
    return _carrier_from_mapping(parsed)

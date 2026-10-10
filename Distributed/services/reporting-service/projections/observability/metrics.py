"""Prometheus metrics for report HTTP and the projection consumer.

Same label rule as the order service: no user_id, order_id, request_id,
message_id, or email. event_type is a catalog name or unknown.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable

from prometheus_client import REGISTRY, Counter, Histogram
from prometheus_client.metrics_core import GaugeMetricFamily
from prometheus_client.registry import Collector

FORBIDDEN_LABELS = frozenset({"user_id", "order_id", "request_id", "message_id", "email"})

EVENT_TYPES = frozenset(
    {
        "OrderCreated",
        "OrderConfirmed",
        "OrderCancelled",
        "OrderProcessingStarted",
        "OrderShipped",
        "OrderDelivered",
        "ProductCreated",
        "ProductUpdated",
        "CustomerUpdated",
        "PaymentConfirmed",
        "PaymentFailed",
        "InventoryUpdated",
    }
)

SERVICE = "reporting-service"


def define_counter(name: str, documentation: str, labelnames: Iterable[str] = ()):
    labels = tuple(labelnames)
    _reject(labels)
    return Counter(name, documentation, labelnames=labels)


def define_histogram(name: str, documentation: str, labelnames: Iterable[str] = ()):
    labels = tuple(labelnames)
    _reject(labels)
    return Histogram(name, documentation, labelnames=labels)


def _reject(names: Iterable[str]) -> None:
    bad = FORBIDDEN_LABELS.intersection(names)
    if bad:
        raise ValueError(f"forbidden prometheus label: {', '.join(sorted(bad))}")


def bounded_event_type(value: object) -> str:
    if isinstance(value, str) and value in EVENT_TYPES:
        return value
    return "unknown"


def inc(metric, **labels: str) -> None:
    _reject(labels)
    if labels:
        metric.labels(**labels).inc()
    else:
        metric.inc()


def observe(metric, value: float, **labels: str) -> None:
    _reject(labels)
    if labels:
        metric.labels(**labels).observe(value)
    else:
        metric.observe(value)


http_requests_total = define_counter(
    "http_requests_total",
    "HTTP responses by service, templated route, and status code.",
    ("service", "route", "status"),
)
http_request_duration_seconds = define_histogram(
    "http_request_duration_seconds",
    "HTTP response latency in seconds.",
    ("service", "route", "status"),
)


def _gauge(name: str, documentation: str, labelnames: Iterable[str] = ()):
    from prometheus_client import Gauge

    labels = tuple(labelnames)
    _reject(labels)
    return Gauge(name, documentation, labelnames=labels)


http_requests_in_progress = _gauge(
    "http_requests_in_progress",
    "HTTP requests currently inside the reporting service.",
    ("service",),
)
http_errors_total = define_counter(
    "http_errors_total",
    "HTTP responses with status 500 or higher.",
    ("service", "route", "status"),
)

messages_consumed_total = define_counter(
    "messages_consumed_total",
    "Deliveries taken from the reporting queue.",
    ("service", "event_type"),
)
messages_processed_total = define_counter(
    "messages_processed_total",
    "Deliveries acked after a successful projection apply.",
    ("service", "event_type"),
)
messages_failed_total = define_counter(
    "messages_failed_total",
    "Deliveries the reporting consumer failed to apply.",
    ("service", "event_type"),
)
message_retry_total = define_counter(
    "message_retry_total",
    "Deliveries scheduled onto the retry exchange.",
    ("service", "event_type"),
)
message_dlq_total = define_counter(
    "message_dlq_total",
    "Deliveries published to the dead-letter exchange.",
    ("service", "event_type"),
)
message_processing_duration_seconds = define_histogram(
    "message_processing_duration_seconds",
    "Time to settle one reporting delivery.",
    ("service", "event_type"),
)
consumer_messages_total = define_counter(
    "consumer_messages_total",
    "Settled deliveries by queue and result.",
    ("queue", "result"),
)

DECLARED = (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    http_errors_total,
    messages_consumed_total,
    messages_processed_total,
    messages_failed_total,
    message_retry_total,
    message_dlq_total,
    message_processing_duration_seconds,
    consumer_messages_total,
)


def declared_metrics():
    return DECLARED


def record_http(route: str, status: int, seconds: float) -> None:
    labels = {"service": SERVICE, "route": route, "status": str(status)}
    inc(http_requests_total, **labels)
    observe(http_request_duration_seconds, seconds, **labels)
    if status >= 500:
        inc(http_errors_total, **labels)


def record_message(
    *,
    event_type: str,
    seconds: float,
    processed: bool,
    failed: bool,
    retry: bool,
    dlq: bool,
    queue: str,
    result: str,
) -> None:
    kind = bounded_event_type(event_type)
    labels = {"service": SERVICE, "event_type": kind}
    inc(messages_consumed_total, **labels)
    observe(message_processing_duration_seconds, seconds, **labels)
    if processed:
        inc(messages_processed_total, **labels)
    if failed:
        inc(messages_failed_total, **labels)
    if retry:
        inc(message_retry_total, **labels)
    if dlq:
        inc(message_dlq_total, **labels)
    if queue and result in {"applied", "duplicate", "stale", "error"}:
        inc(consumer_messages_total, queue=queue, result=result)


_collector_registered = False


def register_projection_max_version(read_max_version: Callable[[], float]) -> None:
    """Register the ORM gauge. The reader lives in domain so this module does not import models."""

    global _collector_registered
    if _collector_registered:
        return

    class _ProjectionGauges(Collector):
        def describe(self):
            yield GaugeMetricFamily(
                "projection_max_version",
                "Highest aggregate_version stored on order projections.",
            )

        def collect(self):
            try:
                value = read_max_version()
            except Exception:
                return
            family = GaugeMetricFamily(
                "projection_max_version",
                "Highest aggregate_version stored on order projections.",
            )
            family.add_metric([], float(value or 0))
            yield family

    REGISTRY.register(_ProjectionGauges())
    _collector_registered = True


def serve_metrics(port: int | None = None) -> None:
    from prometheus_client import start_http_server

    listen = port if port is not None else int(os.environ.get("METRICS_PORT", "9100"))
    start_http_server(listen)

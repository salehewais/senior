"""Prometheus metrics. Labels stay on the catalog, not on a person or an order."""

from __future__ import annotations

from collections.abc import Iterable

from prometheus_client import Counter, Histogram

from notification_service.envelope import NOTIFICATION_EVENTS

FORBIDDEN_LABELS = frozenset({"user_id", "order_id", "request_id", "message_id", "email", "token"})
SERVICE = "notification-service"
QUEUE = "q.notification.delivery"


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
    if isinstance(value, str) and value in NOTIFICATION_EVENTS:
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
messages_consumed_total = define_counter(
    "messages_consumed_total",
    "Deliveries taken from the notification queue.",
    ("service", "event_type"),
)
messages_processed_total = define_counter(
    "messages_processed_total",
    "Deliveries acked after a successful notification apply.",
    ("service", "event_type"),
)
messages_failed_total = define_counter(
    "messages_failed_total",
    "Deliveries the notification consumer failed to apply.",
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
    "Time to settle one notification delivery.",
    ("service", "event_type"),
)
consumer_messages_total = define_counter(
    "consumer_messages_total",
    "Settled deliveries by queue and result.",
    ("queue", "result"),
)


def record_http(route: str, status: int, seconds: float) -> None:
    labels = {"service": SERVICE, "route": route, "status": str(status)}
    inc(http_requests_total, **labels)
    observe(http_request_duration_seconds, seconds, **labels)


def record_message(
    *,
    event_type: str,
    seconds: float,
    processed: bool,
    failed: bool,
    retry: bool,
    dlq: bool,
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
    if result in {"applied", "duplicate", "error"}:
        inc(consumer_messages_total, queue=QUEUE, result=result)

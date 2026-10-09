"""Prometheus metrics for the order service.

A label is part of the series identity. `user_id`, `order_id`, `request_id`,
`message_id`, and `email` are rejected so one checkout cannot create a series.
Route labels are framework templates. `event_type` is the catalog name or
`unknown`.

`order_processing_duration_seconds` is omitted. Confirm and ship are separate
requests, and the order row does not keep the confirm time after a later
update, so a confirm-to-ship histogram would be a guess.
"""

from __future__ import annotations

import os
from collections.abc import Iterable

from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from prometheus_client.metrics_core import GaugeMetricFamily
from prometheus_client.registry import Collector

FORBIDDEN_LABELS = frozenset({"user_id", "order_id", "request_id", "message_id", "email"})

# Catalog names only. A delivery with any other type uses the label "unknown".
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

SERVICE = "order-service"


def define_counter(name: str, documentation: str, labelnames: Iterable[str] = ()):
    labels = tuple(labelnames)
    _reject_forbidden(labels)
    return Counter(name, documentation, labelnames=labels)


def define_histogram(name: str, documentation: str, labelnames: Iterable[str] = ()):
    labels = tuple(labelnames)
    _reject_forbidden(labels)
    return Histogram(name, documentation, labelnames=labels)


def define_gauge(name: str, documentation: str, labelnames: Iterable[str] = ()):
    labels = tuple(labelnames)
    _reject_forbidden(labels)
    return Gauge(name, documentation, labelnames=labels)


def _reject_forbidden(names: Iterable[str]) -> None:
    bad = FORBIDDEN_LABELS.intersection(names)
    if bad:
        raise ValueError(f"forbidden prometheus label: {', '.join(sorted(bad))}")


def bounded_event_type(value: object) -> str:
    if isinstance(value, str) and value in EVENT_TYPES:
        return value
    return "unknown"


def inc(metric, **labels: str) -> None:
    """Record one sample. A forbidden label raises and does not change the series."""

    _reject_forbidden(labels)
    if labels:
        metric.labels(**labels).inc()
    else:
        metric.inc()


def observe(metric, value: float, **labels: str) -> None:
    _reject_forbidden(labels)
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
http_requests_in_progress = define_gauge(
    "http_requests_in_progress",
    "HTTP requests currently inside the order service.",
    ("service",),
)
http_errors_total = define_counter(
    "http_errors_total",
    "HTTP responses with status 500 or higher.",
    ("service", "route", "status"),
)

orders_created_total = define_counter("orders_created_total", "Orders committed in PENDING.")
orders_confirmed_total = define_counter("orders_confirmed_total", "Orders committed in CONFIRMED.")
orders_cancelled_total = define_counter("orders_cancelled_total", "Orders committed in CANCELLED.")
orders_shipped_total = define_counter("orders_shipped_total", "Orders committed in SHIPPED.")
orders_delivered_total = define_counter("orders_delivered_total", "Orders committed in DELIVERED.")

outbox_events_created_total = define_counter(
    "outbox_events_created_total",
    "Outbox rows committed with the business write.",
    ("event_type",),
)
outbox_events_published_total = define_counter(
    "outbox_events_published_total",
    "Outbox rows the broker confirmed.",
    ("event_type",),
)
outbox_events_failed_total = define_counter(
    "outbox_events_failed_total",
    "Outbox rows that reached status failed and will not be retried.",
    ("event_type",),
)
outbox_publish_failures_total = define_counter(
    "outbox_publish_failures_total",
    "Broker confirms that failed. The row may still be pending.",
    ("event_type",),
)
outbox_publish_duration_seconds = define_histogram(
    "outbox_publish_duration_seconds",
    "Time spent waiting for one broker confirm.",
    ("event_type",),
)

messages_consumed_total = define_counter(
    "messages_consumed_total",
    "Deliveries taken from a queue.",
    ("service", "event_type"),
)
messages_processed_total = define_counter(
    "messages_processed_total",
    "Deliveries acked after a successful apply, including duplicates.",
    ("service", "event_type"),
)
messages_failed_total = define_counter(
    "messages_failed_total",
    "Deliveries that failed in the handler, including permanent failures.",
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
    "Time to settle one delivery.",
    ("service", "event_type"),
)

# Doc-stable consumer series. queue is a topology name, result is a small enum.
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
    orders_created_total,
    orders_confirmed_total,
    orders_cancelled_total,
    orders_shipped_total,
    orders_delivered_total,
    outbox_events_created_total,
    outbox_events_published_total,
    outbox_events_failed_total,
    outbox_publish_failures_total,
    outbox_publish_duration_seconds,
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


def record_outbox_created(event_type: str) -> None:
    inc(outbox_events_created_total, event_type=bounded_event_type(event_type))


def record_outbox_published(event_type: str, seconds: float) -> None:
    kind = bounded_event_type(event_type)
    inc(outbox_events_published_total, event_type=kind)
    observe(outbox_publish_duration_seconds, seconds, event_type=kind)


def record_outbox_attempt_failed(event_type: str, *, terminal: bool, seconds: float) -> None:
    kind = bounded_event_type(event_type)
    inc(outbox_publish_failures_total, event_type=kind)
    observe(outbox_publish_duration_seconds, seconds, event_type=kind)
    if terminal:
        inc(outbox_events_failed_total, event_type=kind)


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


_engine_holder: dict[str, object] = {"engine": None, "ready": False}
_collector_registered = False


def bind_database_engine(engine: object) -> None:
    """Point scrape-time gauges at the order_db engine. Safe to call more than once.

    Registration collects once. That first collect must not open order_db, or
    importing the app would connect during startup and during tests.
    """

    _engine_holder["engine"] = engine
    global _collector_registered
    if _collector_registered:
        return
    _engine_holder["ready"] = False
    REGISTRY.register(_DatabaseGauges())
    _collector_registered = True
    _engine_holder["ready"] = True


class _DatabaseGauges(Collector):
    """Gauges that must be read from order_db at scrape time, not remembered in the process."""

    def collect(self):
        yield _gauge(
            "payment_circuit_state",
            "0 closed, 1 half-open, 2 open. No payment provider is wired in this phase, so the value stays 0.",
            0.0,
        )
        if not _engine_holder.get("ready"):
            return
        engine = _engine_holder.get("engine")
        if engine is None:
            return
        try:
            from sqlalchemy import text

            with engine.connect() as connection:  # type: ignore[attr-defined]
                pending, failed, age = connection.execute(
                    text(
                        """
                        SELECT
                          COUNT(*) FILTER (WHERE status = 'pending'),
                          COUNT(*) FILTER (WHERE status = 'failed'),
                          COALESCE(
                            EXTRACT(EPOCH FROM (
                              clock_timestamp() - MIN(created_at) FILTER (WHERE status = 'pending')
                            )),
                            0
                          )
                        FROM outbox
                        """
                    )
                ).one()
                max_version = connection.execute(text("SELECT COALESCE(MAX(version), 0) FROM orders")).scalar_one()
        except Exception:
            return
        pending_value = float(pending)
        yield _gauge("outbox_events_pending", "Outbox rows still status pending.", pending_value)
        yield _gauge(
            "outbox_unpublished_count",
            "Same value as outbox_events_pending. Stable name from the Prometheus design.",
            pending_value,
        )
        yield _gauge("outbox_failed_rows", "Outbox rows with status failed.", float(failed))
        yield _gauge(
            "outbox_oldest_pending_age_seconds",
            "Seconds since the oldest pending outbox row was created. Zero when none are pending.",
            float(age),
        )
        yield _gauge(
            "orders_max_version",
            "Highest orders.version in order_db. Compared with the reporting projection.",
            float(max_version),
        )


def _gauge(name: str, documentation: str, value: float) -> GaugeMetricFamily:
    _reject_forbidden(())
    family = GaugeMetricFamily(name, documentation)
    family.add_metric([], value)
    return family


def serve_metrics(port: int | None = None) -> None:
    """HTTP /metrics for a worker process that is not the FastAPI app."""

    from prometheus_client import start_http_server

    listen = port if port is not None else int(os.environ.get("METRICS_PORT", "9100"))
    start_http_server(listen)

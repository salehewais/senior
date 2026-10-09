"""Correlation ids, request metrics, and a JSON error envelope. Stack traces stay in the log."""

from __future__ import annotations

import logging
import time
import uuid

from django.http import HttpRequest, HttpResponse

from projections.http import correlation_id_of, error_response
from projections.metrics import SERVICE, http_requests_in_progress, record_http

logger = logging.getLogger("reporting.http")


class ObservabilityMiddleware:
    """Times the request after the correlation id middleware has run.

    This class is listed first, so it is the outer middleware. It does not
    read the body. /metrics is the scrape path and is not counted as traffic.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        started = time.perf_counter()
        skip = request.path == "/metrics"
        if not skip:
            http_requests_in_progress.labels(service=SERVICE).inc()
        status = 500
        try:
            response = self.get_response(request)
            status = response.status_code
            return response
        finally:
            if not skip:
                http_requests_in_progress.labels(service=SERVICE).dec()
                route = _route(request)
                record_http(route, status, time.perf_counter() - started)
                logger.info(
                    "http request",
                    extra={
                        "correlation_id": correlation_id_of(request),
                        "http_method": request.method,
                        "http_route": route,
                        "http_status": status,
                    },
                )


def _route(request: HttpRequest) -> str:
    match = getattr(request, "resolver_match", None)
    route = getattr(match, "route", None)
    if isinstance(route, str) and route:
        return "/" + route.lstrip("/")
    return "unmatched"


class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        raw = request.headers.get("X-Correlation-Id")
        try:
            request.correlation_id = str(uuid.UUID(raw)) if raw else str(uuid.uuid4())
        except (ValueError, TypeError, AttributeError):
            request.correlation_id = str(uuid.uuid4())
        response = self.get_response(request)
        response["X-Correlation-Id"] = request.correlation_id
        return response


class ApiErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            return self.get_response(request)
        except Exception:
            logger.exception("unhandled error correlation_id=%s", correlation_id_of(request))
            return error_response(
                500,
                "INTERNAL",
                "The server could not complete the request.",
                correlation_id_of(request),
            )

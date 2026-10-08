"""Correlation ids and a JSON error envelope. Stack traces stay in the log."""

from __future__ import annotations

import logging
import uuid

from django.http import HttpRequest, HttpResponse

from projections.http import correlation_id_of, error_response

logger = logging.getLogger("reporting.http")


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

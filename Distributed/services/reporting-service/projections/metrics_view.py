"""Scrape target. Not behind staff auth. The gateway does not route this path."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from projections.metrics import register_projection_gauges


def metrics(_request: HttpRequest) -> HttpResponse:
    # Register on the first scrape, not during AppConfig.ready, so startup does not query.
    register_projection_gauges()
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)

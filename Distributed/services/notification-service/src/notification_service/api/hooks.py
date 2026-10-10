"""Correlation id and HTTP metrics for every request."""

from __future__ import annotations

import time
import uuid

from flask import Flask, Response, g, request

from notification_service.observability.metrics import record_http


def register_hooks(app: Flask) -> None:
    @app.before_request
    def _begin() -> None:
        g.started = time.perf_counter()
        incoming = request.headers.get("X-Correlation-Id", "")
        g.correlation_id = incoming if _safe_correlation(incoming) else str(uuid.uuid4())

    @app.after_request
    def _finish(response: Response) -> Response:
        response.headers["X-Correlation-Id"] = g.correlation_id
        if request.path != "/metrics":
            rule = request.url_rule.rule if request.url_rule is not None else "unmatched"
            record_http(rule, response.status_code, time.perf_counter() - g.started)
        return response


def _safe_correlation(value: str) -> bool:
    if not value or len(value) > 200:
        return False
    return all(char.isalnum() or char in "-_" for char in value)

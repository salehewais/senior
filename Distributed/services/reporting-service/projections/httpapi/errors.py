"""JSON error envelope shared with the order service."""

from __future__ import annotations

import uuid

from django.http import HttpRequest, JsonResponse


def correlation_id_of(request: HttpRequest) -> str:
    existing = getattr(request, "correlation_id", None)
    if isinstance(existing, str) and existing:
        return existing
    return str(uuid.uuid4())


def error_body(*, code: str, message: str, correlation_id: str, details: list[dict[str, str]] | None = None):
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id,
            "details": details or [],
        }
    }


def error_response(
    status: int,
    code: str,
    message: str,
    correlation_id: str,
    details: list[dict[str, str]] | None = None,
) -> JsonResponse:
    return JsonResponse(
        error_body(code=code, message=message, correlation_id=correlation_id, details=details),
        status=status,
    )

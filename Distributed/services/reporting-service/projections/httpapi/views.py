"""Report routes. Admin and manager only. Customers are forbidden."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from projections.httpapi.auth import Forbidden, Unauthenticated, VerifierNotConfigured, authenticate, require_staff
from projections.httpapi.errors import correlation_id_of, error_response
from projections.httpapi.queries import (
    inventory_page,
    orders_page,
    parse_limit,
    revenue_report,
)
from projections.httpapi.queries import orders_summary as summary_document


def not_found(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    del exception
    return error_response(404, "NOT_FOUND", "Not found.", correlation_id_of(request))


def _staff(view: Callable[[HttpRequest], JsonResponse]) -> Callable[[HttpRequest], JsonResponse]:
    def wrapped(request: HttpRequest) -> JsonResponse:
        correlation_id = correlation_id_of(request)
        try:
            actor = authenticate(request.headers.get("Authorization"))
            require_staff(actor)
        except VerifierNotConfigured as exc:
            return error_response(503, "DEPENDENCY_UNAVAILABLE", exc.message, correlation_id)
        except Unauthenticated as exc:
            return error_response(401, "UNAUTHENTICATED", exc.message, correlation_id)
        except Forbidden as exc:
            return error_response(403, "FORBIDDEN", exc.message, correlation_id)
        return view(request)

    return wrapped


def _limit_and_cursor(request: HttpRequest) -> tuple[int, str | None] | JsonResponse:
    try:
        limit = parse_limit(request.GET.get("limit"))
        cursor = request.GET.get("cursor")
        if cursor is not None:
            from projections.httpapi.queries import decode_cursor

            decode_cursor(cursor)
    except ValueError as exc:
        field = str(exc)
        return error_response(
            400,
            "VALIDATION_ERROR",
            "The request body or query is not valid.",
            correlation_id_of(request),
            [{"field": field, "issue": "must be a positive integer up to 100" if field == "limit" else "is not valid"}],
        )
    return limit, cursor


@require_GET
def reporting_page(request: HttpRequest) -> HttpResponse:
    """Public HTML. The report JSON routes still require a staff token."""

    return render(request, "reporting.html")


@require_GET
@_staff
def orders_summary(request: HttpRequest) -> JsonResponse:
    del request
    return JsonResponse(summary_document())


@require_GET
@_staff
def orders(request: HttpRequest) -> JsonResponse:
    parsed = _limit_and_cursor(request)
    if isinstance(parsed, JsonResponse):
        return parsed
    limit, cursor = parsed
    return JsonResponse(orders_page(limit=limit, cursor=cursor))


@require_GET
@_staff
def inventory(request: HttpRequest) -> JsonResponse:
    parsed = _limit_and_cursor(request)
    if isinstance(parsed, JsonResponse):
        return parsed
    limit, cursor = parsed
    return JsonResponse(inventory_page(limit=limit, cursor=cursor))


@require_GET
@_staff
def revenue(request: HttpRequest) -> JsonResponse:
    del request
    return JsonResponse(revenue_report())

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from order_service.domain.exceptions import DomainError
from order_service.domain.ids import uuid7
from order_service.observability.context import correlation_id_var, request_id_var
from order_service.observability.metrics import SERVICE, http_requests_in_progress, record_http

logger = logging.getLogger("order_service")

_STATUS = {
    "VALIDATION_ERROR": 400,
    "UNAUTHENTICATED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INVALID_STATE_TRANSITION": 409,
    "CONFLICT": 409,
    "CONCURRENT_MODIFICATION": 409,
    "PRODUCT_NOT_ORDERABLE": 409,
    "IDEMPOTENCY_IN_PROGRESS": 409,
    "RATE_LIMITED": 429,
    "DEPENDENCY_UNAVAILABLE": 503,
}


def error_body(
    *,
    code: str,
    message: str,
    correlation_id: str,
    details: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id,
            "details": details or [],
        }
    }


def correlation_id_of(request: Request) -> str:
    value = getattr(request.state, "correlation_id", None)
    return str(value) if value is not None else str(uuid.uuid4())


def install_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = uuid7()
        raw = request.headers.get("x-correlation-id")
        try:
            request.state.correlation_id = uuid.UUID(raw) if raw else uuid7()
        except (ValueError, AttributeError, TypeError):
            request.state.correlation_id = uuid7()
        request_token = request_id_var.set(str(request.state.request_id))
        correlation_token = correlation_id_var.set(str(request.state.correlation_id))
        path = request.url.path
        skip_metrics = path == "/metrics" or path.startswith("/metrics/")
        started = time.perf_counter()
        status = 500
        if not skip_metrics:
            http_requests_in_progress.labels(service=SERVICE).inc()
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-Id"] = str(request.state.request_id)
            response.headers["X-Correlation-Id"] = str(request.state.correlation_id)
            return response
        finally:
            if not skip_metrics:
                http_requests_in_progress.labels(service=SERVICE).dec()
                record_http(_route_template(request), status, time.perf_counter() - started)
                logger.info(
                    "http request",
                    extra={
                        "http_method": request.method,
                        "http_route": _route_template(request),
                        "http_status": status,
                    },
                )
            request_id_var.reset(request_token)
            correlation_id_var.reset(correlation_token)


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str) and path:
        return path
    return "unmatched"


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=_STATUS.get(exc.code, 400),
            content=error_body(
                code=exc.code,
                message=exc.message,
                correlation_id=correlation_id_of(request),
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for item in exc.errors():
            field = ".".join(str(part) for part in item.get("loc", ()) if part != "body")
            details.append({"field": field or "body", "issue": str(item.get("msg", "invalid"))})
        return JSONResponse(
            status_code=400,
            content=error_body(
                code="VALIDATION_ERROR",
                message="The request body or query is not valid.",
                correlation_id=correlation_id_of(request),
                details=details,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            code, message = "NOT_FOUND", "Not found."
        else:
            code, message = "INTERNAL", "The server could not complete the request."
        return JSONResponse(
            status_code=exc.status_code if exc.status_code < 500 else 500,
            content=error_body(
                code=code,
                message=message,
                correlation_id=correlation_id_of(request),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error correlation_id=%s", correlation_id_of(request))
        return JSONResponse(
            status_code=500,
            content=error_body(
                code="INTERNAL",
                message="The server could not complete the request.",
                correlation_id=correlation_id_of(request),
            ),
        )

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from order_service.infrastructure.database.engine import database_ready
from order_service.presentation.errors import error_body

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    """The process is up. It does not check the database."""
    return {"status": "live"}


@router.get("/health/ready")
def ready(request: Request):
    """Traffic is acceptable only when order_db answers. A dead database must not receive orders."""
    engine = request.app.state.engine
    correlation_id = str(getattr(request.state, "correlation_id", ""))
    if engine is None:
        return JSONResponse(
            status_code=503,
            content=error_body(
                code="DEPENDENCY_UNAVAILABLE",
                message="The order database is not configured.",
                correlation_id=correlation_id,
            ),
        )
    if not database_ready(engine):
        return JSONResponse(
            status_code=503,
            content=error_body(
                code="DEPENDENCY_UNAVAILABLE",
                message="The order database is unavailable.",
                correlation_id=correlation_id,
            ),
        )
    return {"status": "ready"}

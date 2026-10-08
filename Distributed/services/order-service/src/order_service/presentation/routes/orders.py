import uuid

from fastapi import APIRouter, Query, Request

from order_service.application.use_cases.orders import (
    CancelOrder,
    ConfirmOrder,
    CreateOrder,
    DeliverOrder,
    GetOrder,
    ListOrders,
    ShipOrder,
    StartProcessing,
)
from order_service.presentation.dependencies import ActorDep, InternalDep, UnitOfWorkDep
from order_service.presentation.schemas import (
    CancelOrderBody,
    CreateOrderBody,
    OrderListResponse,
    OrderResponse,
    ShipOrderBody,
)

router = APIRouter(tags=["orders"])


def _trace(request: Request) -> tuple[uuid.UUID, uuid.UUID]:
    return request.state.correlation_id, request.state.request_id


@router.post("/api/v1/orders", status_code=201)
def create_order(body: CreateOrderBody, request: Request, actor: ActorDep, uow: UnitOfWorkDep) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = CreateOrder(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        actor=actor,
        lines=[(line.product_id, line.quantity) for line in body.items],
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)


@router.get("/api/v1/orders")
def list_orders(
    actor: ActorDep,
    uow: UnitOfWorkDep,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = None,
) -> OrderListResponse:
    views, next_cursor = ListOrders().execute(uow, actor=actor, limit=limit, cursor=cursor)
    return OrderListResponse(
        items=[OrderResponse.from_view(view) for view in views],
        next_cursor=next_cursor,
    )


@router.get("/api/v1/orders/{order_id}")
def get_order(order_id: uuid.UUID, actor: ActorDep, uow: UnitOfWorkDep) -> OrderResponse:
    return OrderResponse.from_view(GetOrder().execute(uow, actor=actor, order_id=order_id))


@router.post("/api/v1/orders/{order_id}/confirm")
def confirm_order(order_id: uuid.UUID, request: Request, actor: ActorDep, uow: UnitOfWorkDep) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = ConfirmOrder(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        actor=actor,
        order_id=order_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)


@router.post("/api/v1/orders/{order_id}/cancel")
def cancel_order(
    order_id: uuid.UUID,
    body: CancelOrderBody,
    request: Request,
    actor: ActorDep,
    uow: UnitOfWorkDep,
) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = CancelOrder(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        actor=actor,
        order_id=order_id,
        reason=body.reason,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)


# Not for the public gateway. A customer access token is not permission.
# X-Internal-Token is compared with INTERNAL_SERVICE_TOKEN. Unset means 503, not open.
internal = APIRouter(prefix="/api/v1/internal/orders", tags=["internal"])


@internal.post("/{order_id}/processing")
def start_processing(
    order_id: uuid.UUID,
    request: Request,
    uow: UnitOfWorkDep,
    _: InternalDep,
) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = StartProcessing(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        order_id=order_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)


@internal.post("/{order_id}/shipped")
def ship_order(
    order_id: uuid.UUID,
    request: Request,
    uow: UnitOfWorkDep,
    _: InternalDep,
    body: ShipOrderBody | None = None,
) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = ShipOrder(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        order_id=order_id,
        tracking_reference=None if body is None else body.tracking_reference,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)


@internal.post("/{order_id}/delivered")
def deliver_order(order_id: uuid.UUID, request: Request, uow: UnitOfWorkDep, _: InternalDep) -> OrderResponse:
    correlation_id, causation_id = _trace(request)
    view = DeliverOrder(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        order_id=order_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return OrderResponse.from_view(view)

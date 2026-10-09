import uuid

from fastapi import APIRouter, Query, Request

from order_service.application.use_cases.catalog import (
    CreateProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
)
from order_service.presentation.dependencies import ActorDep, UnitOfWorkDep
from order_service.presentation.schemas import (
    ProductBody,
    ProductListResponse,
    ProductPatch,
    ProductResponse,
)

router = APIRouter(prefix="/api/v1/products", tags=["products"])


def _ids(request: Request) -> tuple[uuid.UUID, uuid.UUID]:
    return request.state.correlation_id, request.state.request_id


@router.post("", status_code=201)
def create_product(body: ProductBody, request: Request, actor: ActorDep, uow: UnitOfWorkDep) -> ProductResponse:
    correlation_id, causation_id = _ids(request)
    view = CreateProduct(request.app.state.clock, request.app.state.product_cache).execute(
        uow,
        sku=body.sku,
        name=body.name,
        amount_minor=body.unit_price.amount_minor,
        currency=body.unit_price.currency,
        actor=actor,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return ProductResponse.from_view(view)


@router.get("")
def list_products(
    request: Request,
    actor: ActorDep,
    uow: UnitOfWorkDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProductListResponse:
    views = ListProducts(request.app.state.product_cache).execute(uow, actor=actor, limit=limit, offset=offset)
    return ProductListResponse(
        items=[ProductResponse.from_view(view) for view in views],
        limit=limit,
        offset=offset,
    )


@router.get("/{product_id}")
def get_product(product_id: uuid.UUID, request: Request, actor: ActorDep, uow: UnitOfWorkDep) -> ProductResponse:
    view = GetProduct(request.app.state.product_cache).execute(uow, actor=actor, product_id=product_id)
    return ProductResponse.from_view(view)


@router.patch("/{product_id}")
def update_product(
    product_id: uuid.UUID,
    body: ProductPatch,
    request: Request,
    actor: ActorDep,
    uow: UnitOfWorkDep,
) -> ProductResponse:
    correlation_id, causation_id = _ids(request)
    price = body.unit_price
    view = UpdateProduct(request.app.state.clock, request.app.state.product_cache).execute(
        uow,
        product_id=product_id,
        name=body.name,
        amount_minor=None if price is None else price.amount_minor,
        currency=None if price is None else price.currency,
        active=body.active,
        actor=actor,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    return ProductResponse.from_view(view)

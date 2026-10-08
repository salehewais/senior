import uuid

from fastapi import APIRouter, Query, Request

from order_service.application.use_cases.catalog import GetCustomer, GetOwnCustomer, ListCustomers, RenameCustomer
from order_service.presentation.dependencies import ActorDep, UnitOfWorkDep
from order_service.presentation.schemas import CustomerListResponse, CustomerPatch, CustomerResponse

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.get("/me")
def get_me(actor: ActorDep, uow: UnitOfWorkDep) -> CustomerResponse:
    return CustomerResponse.from_view(GetOwnCustomer().execute(uow, actor=actor))


@router.patch("/me")
def rename_me(body: CustomerPatch, request: Request, actor: ActorDep, uow: UnitOfWorkDep) -> CustomerResponse:
    view = RenameCustomer(request.app.state.clock, request.app.state.event_publisher).execute(
        uow,
        actor=actor,
        display_name=body.display_name,
        correlation_id=request.state.correlation_id,
        causation_id=request.state.request_id,
    )
    return CustomerResponse.from_view(view)


@router.get("")
def list_customers(
    actor: ActorDep,
    uow: UnitOfWorkDep,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = None,
) -> CustomerListResponse:
    views, next_cursor = ListCustomers().execute(uow, actor=actor, limit=limit, cursor=cursor)
    return CustomerListResponse(
        items=[CustomerResponse.from_view(view) for view in views],
        next_cursor=next_cursor,
    )


@router.get("/{customer_id}")
def get_customer(customer_id: uuid.UUID, actor: ActorDep, uow: UnitOfWorkDep) -> CustomerResponse:
    return CustomerResponse.from_view(GetCustomer().execute(uow, actor=actor, customer_id=customer_id))

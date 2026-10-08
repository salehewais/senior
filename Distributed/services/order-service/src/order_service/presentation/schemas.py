import uuid

from pydantic import BaseModel, Field

from order_service.application.dto import CustomerView, OrderView, ProductView


class MoneyBody(BaseModel):
    amount_minor: int
    currency: str


class ProductBody(BaseModel):
    sku: str
    name: str
    unit_price: MoneyBody
    active: bool = True


class ProductPatch(BaseModel):
    name: str | None = None
    unit_price: MoneyBody | None = None
    active: bool | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    sku: str
    name: str
    unit_price: MoneyBody
    active: bool
    version: int

    @classmethod
    def from_view(cls, view: ProductView) -> "ProductResponse":
        return cls(
            id=view.id,
            sku=view.sku,
            name=view.name,
            unit_price=MoneyBody(amount_minor=view.unit_price.amount_minor, currency=view.unit_price.currency),
            active=view.active,
            version=view.version,
        )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    limit: int
    offset: int


class RegisterBody(BaseModel):
    email: str
    display_name: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


class RefreshTokenBody(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class CustomerPatch(BaseModel):
    display_name: str


class CustomerResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    version: int

    @classmethod
    def from_view(cls, view: CustomerView) -> "CustomerResponse":
        return cls(
            id=view.id,
            email=view.email,
            display_name=view.display_name,
            version=view.version,
        )


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    next_cursor: str | None


class OrderLineBody(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1)


class CreateOrderBody(BaseModel):
    items: list[OrderLineBody] = Field(min_length=1)


class CancelOrderBody(BaseModel):
    reason: str


class ShipOrderBody(BaseModel):
    tracking_reference: str | None = None


class OrderItemResponse(BaseModel):
    product_id: uuid.UUID
    sku: str
    quantity: int
    unit_price: MoneyBody


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    saga_status: str | None
    items: list[OrderItemResponse]
    total: MoneyBody
    version: int
    tracking_reference: str | None = None
    cancel_reason: str | None = None

    @classmethod
    def from_view(cls, view: OrderView) -> "OrderResponse":
        return cls(
            id=view.id,
            customer_id=view.customer_id,
            status=view.status,
            saga_status=view.saga_status,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    sku=item.sku,
                    quantity=item.quantity,
                    unit_price=MoneyBody(
                        amount_minor=item.unit_price.amount_minor,
                        currency=item.unit_price.currency,
                    ),
                )
                for item in view.items
            ],
            total=MoneyBody(amount_minor=view.total.amount_minor, currency=view.total.currency),
            version=view.version,
            tracking_reference=view.tracking_reference,
            cancel_reason=view.cancel_reason,
        )


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    next_cursor: str | None

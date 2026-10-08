"""Maps aggregates to rows. Optimistic updates use the version loaded with the row."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from order_service.domain.entities.account import Account
from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.entities.order_status import OrderStatus
from order_service.domain.entities.refresh_token import RefreshToken
from order_service.domain.exceptions import ConcurrentModificationError, NotFoundError
from order_service.domain.ids import AccountId, CustomerId, OrderId, ProductId, uuid7
from order_service.domain.repositories import (
    AccountRepository,
    CustomerRepository,
    OrderRepository,
    ProductRepository,
    RefreshTokenRepository,
)
from order_service.domain.roles import Role
from order_service.domain.value_objects import Money, Quantity
from order_service.infrastructure.database.models import (
    AccountRow,
    CustomerRow,
    OrderItemRow,
    OrderRow,
    ProductRow,
    RefreshTokenRow,
)


class SqlProductRepository(ProductRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, product_id: ProductId) -> Product | None:
        row = self._session.get(ProductRow, product_id.value)
        return None if row is None else _product(row)

    def get_by_sku(self, sku: str) -> Product | None:
        row = self._session.scalar(select(ProductRow).where(ProductRow.sku == sku))
        return None if row is None else _product(row)

    def add(self, product: Product) -> None:
        if product.loaded_version is None:
            self._session.add(
                ProductRow(
                    id=product.id.value,
                    sku=product.sku,
                    name=product.name,
                    amount_minor=product.unit_price.amount_minor,
                    currency=product.unit_price.currency,
                    active=product.active,
                    version=product.version,
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                )
            )
            self._session.flush()
            product.acknowledge_persisted()
            return
        row = self._session.get(ProductRow, product.id.value)
        if row is None or row.version != product.loaded_version:
            raise ConcurrentModificationError("The product was changed by another request.")
        row.name = product.name
        row.amount_minor = product.unit_price.amount_minor
        row.currency = product.unit_price.currency
        row.active = product.active
        row.version = product.version
        row.updated_at = product.updated_at
        self._session.flush()
        product.acknowledge_persisted()

    def list_page(self, *, limit: int, offset: int) -> list[Product]:
        rows = self._session.scalars(
            select(ProductRow).order_by(ProductRow.name, ProductRow.id).offset(offset).limit(limit)
        )
        return [_product(row) for row in rows]


class SqlCustomerRepository(CustomerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, customer_id: CustomerId) -> Customer | None:
        row = self._session.get(CustomerRow, customer_id.value)
        return None if row is None else _customer(row)

    def get_by_email(self, email: str) -> Customer | None:
        row = self._session.scalar(select(CustomerRow).where(CustomerRow.email == email))
        return None if row is None else _customer(row)

    def add(self, customer: Customer) -> None:
        if customer.loaded_version is None:
            self._session.add(
                CustomerRow(
                    id=customer.id.value,
                    email=customer.email,
                    display_name=customer.display_name,
                    version=customer.version,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at,
                )
            )
            self._session.flush()
            customer.acknowledge_persisted()
            return
        row = self._session.get(CustomerRow, customer.id.value)
        if row is None or row.version != customer.loaded_version:
            raise ConcurrentModificationError("The customer was changed by another request.")
        row.display_name = customer.display_name
        row.version = customer.version
        row.updated_at = customer.updated_at
        self._session.flush()
        customer.acknowledge_persisted()

    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
    ) -> list[Customer]:
        stmt = select(CustomerRow).order_by(CustomerRow.created_at.desc(), CustomerRow.id.desc())
        if created_before is not None and id_before is not None:
            stmt = stmt.where(tuple_(CustomerRow.created_at, CustomerRow.id) < (created_before, id_before))
        rows = self._session.scalars(stmt.limit(limit))
        return [_customer(row) for row in rows]


class SqlOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, order_id: OrderId) -> Order | None:
        row = self._session.get(OrderRow, order_id.value)
        return None if row is None else _order(row)

    def add(self, order: Order) -> None:
        if order.loaded_version is None:
            row = OrderRow(
                id=order.id.value,
                customer_id=order.customer_id.value,
                status=order.status.value,
                amount_minor=order.total.amount_minor,
                currency=order.total.currency,
                version=order.version,
                saga_status=order.saga_status,
                tracking_reference=order.tracking_reference,
                cancel_reason=order.cancel_reason,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    OrderItemRow(
                        id=uuid7(),
                        position=index,
                        product_id=item.product_id.value,
                        sku=item.sku,
                        quantity=item.quantity.value,
                        amount_minor=item.unit_price.amount_minor,
                        currency=item.unit_price.currency,
                    )
                    for index, item in enumerate(order.items)
                ],
            )
            self._session.add(row)
            self._session.flush()
            order.acknowledge_persisted()
            return
        row = self._session.get(OrderRow, order.id.value)
        if row is None or row.version != order.loaded_version:
            raise ConcurrentModificationError("The order was changed by another request.")
        row.status = order.status.value
        row.version = order.version
        row.saga_status = order.saga_status
        row.tracking_reference = order.tracking_reference
        row.cancel_reason = order.cancel_reason
        row.updated_at = order.updated_at
        self._session.flush()
        order.acknowledge_persisted()

    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
        customer_id: uuid.UUID | None = None,
    ) -> list[Order]:
        stmt = select(OrderRow).order_by(OrderRow.created_at.desc(), OrderRow.id.desc())
        if customer_id is not None:
            stmt = stmt.where(OrderRow.customer_id == customer_id)
        if created_before is not None and id_before is not None:
            stmt = stmt.where(tuple_(OrderRow.created_at, OrderRow.id) < (created_before, id_before))
        rows = self._session.scalars(stmt.limit(limit))
        return [_order(row) for row in rows]


class SqlAccountRepository(AccountRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, account_id: AccountId) -> Account | None:
        row = self._session.get(AccountRow, account_id.value)
        return None if row is None else _account(row)

    def get_by_email(self, email: str) -> Account | None:
        row = self._session.scalar(select(AccountRow).where(AccountRow.email == email))
        return None if row is None else _account(row)

    def add(self, account: Account) -> None:
        self._session.add(
            AccountRow(
                id=account.id.value,
                email=account.email,
                password_hash=account.password_hash,
                role=account.role.value,
                created_at=account.created_at,
            )
        )
        self._session.flush()


class SqlRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        row = self._session.scalar(select(RefreshTokenRow).where(RefreshTokenRow.token_hash == token_hash))
        return None if row is None else _refresh(row)

    def add(self, token: RefreshToken) -> None:
        self._session.add(
            RefreshTokenRow(
                id=token.id,
                account_id=token.account_id,
                token_hash=token.token_hash,
                expires_at=token.expires_at,
                revoked_at=token.revoked_at,
                parent_id=token.parent_id,
                created_at=token.created_at,
            )
        )
        self._session.flush()

    def save(self, token: RefreshToken) -> None:
        row = self._session.get(RefreshTokenRow, token.id)
        if row is None:
            raise NotFoundError("Refresh token not found.")
        row.revoked_at = token.revoked_at
        self._session.flush()


def _account(row: AccountRow) -> Account:
    return Account.reconstitute(
        account_id=AccountId(row.id),
        email=row.email,
        password_hash=row.password_hash,
        role=Role(row.role),
        created_at=row.created_at,
    )


def _refresh(row: RefreshTokenRow) -> RefreshToken:
    return RefreshToken(
        token_id=row.id,
        account_id=row.account_id,
        token_hash=row.token_hash,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
        parent_id=row.parent_id,
        created_at=row.created_at,
    )


def _product(row: ProductRow) -> Product:
    return Product.reconstitute(
        product_id=ProductId(row.id),
        sku=row.sku,
        name=row.name,
        unit_price=Money(row.amount_minor, row.currency),
        active=row.active,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _customer(row: CustomerRow) -> Customer:
    return Customer.reconstitute(
        customer_id=CustomerId(row.id),
        email=row.email,
        display_name=row.display_name,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _order(row: OrderRow) -> Order:
    items = tuple(
        OrderItem(
            product_id=ProductId(item.product_id),
            sku=item.sku,
            quantity=Quantity.of_line(item.quantity),
            unit_price=Money(item.amount_minor, item.currency),
        )
        for item in sorted(row.items, key=lambda item: item.position)
    )
    return Order.reconstitute(
        order_id=OrderId(row.id),
        customer_id=CustomerId(row.customer_id),
        status=OrderStatus(row.status),
        items=items,
        total=Money(row.amount_minor, row.currency),
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
        tracking_reference=row.tracking_reference,
        cancel_reason=row.cancel_reason,
        saga_status=row.saga_status,
    )

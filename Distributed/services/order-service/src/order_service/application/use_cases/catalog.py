"""Catalog and customer use cases. No HTTP types enter this module."""

from __future__ import annotations

import uuid

from order_service.application.actor import Actor
from order_service.application.authorization import require_role
from order_service.application.clock import Clock
from order_service.application.dto import CustomerView, ProductView, customer_view, product_view
from order_service.application.pagination import decode_cursor, encode_cursor
from order_service.application.product_cache import ProductCache
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.exceptions import ConflictError, NotFoundError
from order_service.domain.ids import CustomerId, ProductId
from order_service.domain.roles import Role
from order_service.domain.value_objects import Money

_ANY_ROLE = (Role.CUSTOMER, Role.ADMIN, Role.MANAGER)


class CreateProduct:
    def __init__(self, clock: Clock, cache: ProductCache | None = None) -> None:
        self._clock = clock
        self._cache = cache

    def execute(
        self,
        uow: UnitOfWork,
        *,
        sku: str,
        name: str,
        amount_minor: int,
        currency: str,
        actor: Actor,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> ProductView:
        require_role(actor, Role.ADMIN)
        if uow.products.get_by_sku(sku.strip()) is not None:
            raise ConflictError(f"SKU {sku.strip()} is already in the catalog.")
        product = Product.create(
            sku=sku,
            name=name,
            unit_price=Money(amount_minor, currency),
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.products.add(product)
        uow.stage_events(product)
        uow.commit()
        view = product_view(product)
        if self._cache is not None:
            self._cache.invalidate(view.id)
        return view


class UpdateProduct:
    def __init__(self, clock: Clock, cache: ProductCache | None = None) -> None:
        self._clock = clock
        self._cache = cache

    def execute(
        self,
        uow: UnitOfWork,
        *,
        product_id: uuid.UUID,
        name: str | None,
        amount_minor: int | None,
        currency: str | None,
        active: bool | None,
        actor: Actor,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> ProductView:
        require_role(actor, Role.ADMIN, Role.MANAGER)
        product = uow.products.get(ProductId(product_id))
        if product is None:
            raise NotFoundError("Product not found.")
        price = None
        if amount_minor is not None or currency is not None:
            price = Money(
                product.unit_price.amount_minor if amount_minor is None else amount_minor,
                product.unit_price.currency if currency is None else currency,
            )
        product.update(
            name=name,
            unit_price=price,
            active=active,
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.products.add(product)
        uow.stage_events(product)
        uow.commit()
        view = product_view(product)
        if self._cache is not None:
            self._cache.invalidate(view.id)
        return view


class GetProduct:
    def __init__(self, cache: ProductCache | None = None) -> None:
        self._cache = cache

    def execute(self, uow: UnitOfWork, *, actor: Actor, product_id: uuid.UUID) -> ProductView:
        require_role(actor, *_ANY_ROLE)
        if self._cache is not None:
            cached = self._cache.get_product(product_id)
            if cached is not None:
                return cached
        product = uow.products.get(ProductId(product_id))
        if product is None:
            raise NotFoundError("Product not found.")
        view = product_view(product)
        if self._cache is not None:
            self._cache.put_product(view)
        return view


class ListProducts:
    def __init__(self, cache: ProductCache | None = None) -> None:
        self._cache = cache

    def execute(self, uow: UnitOfWork, *, actor: Actor, limit: int, offset: int) -> list[ProductView]:
        require_role(actor, *_ANY_ROLE)
        if self._cache is not None:
            cached = self._cache.get_list(limit=limit, offset=offset)
            if cached is not None:
                return cached
        views = [product_view(product) for product in uow.products.list_page(limit=limit, offset=offset)]
        if self._cache is not None:
            self._cache.put_list(views, limit=limit, offset=offset)
        return views


class CreateCustomer:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        email: str,
        display_name: str,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> CustomerView:
        if uow.customers.get_by_email(email.strip().lower()) is not None:
            raise ConflictError("A customer with that email already exists.")
        customer = Customer.create(
            email=email,
            display_name=display_name,
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.customers.add(customer)
        uow.stage_events(customer)
        uow.commit()
        return customer_view(customer)


class RenameCustomer:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(
        self,
        uow: UnitOfWork,
        *,
        actor: Actor,
        display_name: str,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> CustomerView:
        require_role(actor, Role.CUSTOMER)
        customer = uow.customers.get(CustomerId(actor.account_id))
        if customer is None:
            raise NotFoundError("Customer not found.")
        customer.rename(
            display_name=display_name,
            now=self._clock.now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        uow.customers.add(customer)
        uow.stage_events(customer)
        uow.commit()
        return customer_view(customer)


class GetCustomer:
    def execute(self, uow: UnitOfWork, *, actor: Actor, customer_id: uuid.UUID) -> CustomerView:
        if actor.role == Role.CUSTOMER and actor.account_id != customer_id:
            raise NotFoundError("Customer not found.")
        require_role(actor, *_ANY_ROLE)
        customer = uow.customers.get(CustomerId(customer_id))
        if customer is None:
            raise NotFoundError("Customer not found.")
        return customer_view(customer)


class GetOwnCustomer:
    """`/customers/me` is only the customer role. Staff use the collection routes."""

    def execute(self, uow: UnitOfWork, *, actor: Actor) -> CustomerView:
        require_role(actor, Role.CUSTOMER)
        return GetCustomer().execute(uow, actor=actor, customer_id=actor.account_id)


class ListCustomers:
    def execute(
        self, uow: UnitOfWork, *, actor: Actor, limit: int, cursor: str | None
    ) -> tuple[list[CustomerView], str | None]:
        require_role(actor, Role.ADMIN, Role.MANAGER)
        created_before = None
        id_before = None
        if cursor is not None:
            created_before, id_before = decode_cursor(cursor)
        rows = uow.customers.list_page(
            limit=limit + 1,
            created_before=created_before,
            id_before=id_before,
        )
        page = rows[:limit]
        next_cursor = None
        if len(rows) > limit and page:
            last = page[-1]
            next_cursor = encode_cursor(last.created_at, last.id.value)
        return [customer_view(row) for row in page], next_cursor

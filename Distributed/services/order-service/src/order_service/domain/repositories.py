"""Repository ports. Infrastructure implements them. The domain does not import a database."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from order_service.domain.entities.account import Account
from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.order import Order
from order_service.domain.entities.refresh_token import RefreshToken
from order_service.domain.entities.saga import SagaInstance
from order_service.domain.ids import AccountId, CustomerId, OrderId, ProductId


class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id: ProductId) -> Product | None: ...

    @abstractmethod
    def get_by_sku(self, sku: str) -> Product | None: ...

    @abstractmethod
    def add(self, product: Product) -> None: ...

    @abstractmethod
    def list_page(self, *, limit: int, offset: int) -> list[Product]: ...


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: CustomerId) -> Customer | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Customer | None: ...

    @abstractmethod
    def add(self, customer: Customer) -> None: ...

    @abstractmethod
    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
    ) -> list[Customer]: ...


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: OrderId) -> Order | None: ...

    @abstractmethod
    def add(self, order: Order) -> None: ...

    @abstractmethod
    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
        customer_id: uuid.UUID | None = None,
    ) -> list[Order]: ...


class SagaRepository(ABC):
    @abstractmethod
    def get(self, saga_id: uuid.UUID) -> SagaInstance | None: ...

    @abstractmethod
    def get_by_order(self, order_id: uuid.UUID) -> SagaInstance | None: ...

    @abstractmethod
    def add(self, saga: SagaInstance) -> None: ...

    @abstractmethod
    def next_active(self) -> SagaInstance | None:
        """The oldest saga that is not terminal. None when every saga is finished."""


class AccountRepository(ABC):
    @abstractmethod
    def get(self, account_id: AccountId) -> Account | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Account | None: ...

    @abstractmethod
    def add(self, account: Account) -> None: ...


class RefreshTokenRepository(ABC):
    @abstractmethod
    def get_by_hash(self, token_hash: str) -> RefreshToken | None: ...

    @abstractmethod
    def add(self, token: RefreshToken) -> None: ...

    @abstractmethod
    def save(self, token: RefreshToken) -> None: ...

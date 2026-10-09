"""Single-process stand-in for order_db. Rollback restores the snapshot taken when the unit opened."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime

from order_service.application.outbox import OutboxRecord, stage_outbox_records
from order_service.application.publishing import RecordsEvents
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.entities.account import Account
from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.order import Order
from order_service.domain.entities.refresh_token import RefreshToken
from order_service.domain.entities.saga import SagaInstance
from order_service.domain.entities.saga_status import TERMINAL_SAGA_STATUSES
from order_service.domain.exceptions import ConcurrentModificationError, ConflictError, NotFoundError
from order_service.domain.ids import AccountId, CustomerId, OrderId, ProductId
from order_service.domain.repositories import (
    AccountRepository,
    CustomerRepository,
    OrderRepository,
    ProductRepository,
    RefreshTokenRepository,
    SagaRepository,
)


class MemoryStore:
    def __init__(self) -> None:
        self.products: dict[uuid.UUID, Product] = {}
        self.customers: dict[uuid.UUID, Customer] = {}
        self.orders: dict[uuid.UUID, Order] = {}
        self.accounts: dict[uuid.UUID, Account] = {}
        self.refresh_tokens: dict[uuid.UUID, RefreshToken] = {}
        self.outbox: dict[uuid.UUID, OutboxRecord] = {}
        self.sagas: dict[uuid.UUID, SagaInstance] = {}

    def snapshot(self) -> tuple[dict, dict, dict, dict, dict, dict, dict]:
        return (
            copy.deepcopy(self.products),
            copy.deepcopy(self.customers),
            copy.deepcopy(self.orders),
            copy.deepcopy(self.accounts),
            copy.deepcopy(self.refresh_tokens),
            copy.deepcopy(self.outbox),
            copy.deepcopy(self.sagas),
        )

    def restore(self, snapshot: tuple[dict, dict, dict, dict, dict, dict, dict]) -> None:
        products, customers, orders, accounts, refresh_tokens, outbox, sagas = snapshot
        self.products.clear()
        self.products.update(products)
        self.customers.clear()
        self.customers.update(customers)
        self.orders.clear()
        self.orders.update(orders)
        self.accounts.clear()
        self.accounts.update(accounts)
        self.refresh_tokens.clear()
        self.refresh_tokens.update(refresh_tokens)
        self.outbox.clear()
        self.outbox.update(outbox)
        self.sagas.clear()
        self.sagas.update(sagas)


def _working_copy(entity):
    """A reload is not a replay. Events are not rows, so a get() starts clean.

    The stored object still carries the events recorded when it was saved.
    SQL reconstitution does the same thing by building a new aggregate.
    """

    loaded = copy.deepcopy(entity)
    loaded.collect_events()
    return loaded


class InMemoryProductRepository(ProductRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get(self, product_id: ProductId) -> Product | None:
        row = self._store.products.get(product_id.value)
        return None if row is None else _working_copy(row)

    def get_by_sku(self, sku: str) -> Product | None:
        for product in self._store.products.values():
            if product.sku == sku:
                return copy.deepcopy(product)
        return None

    def add(self, product: Product) -> None:
        current = self._store.products.get(product.id.value)
        if product.loaded_version is None:
            if current is not None:
                raise ConflictError("Product already exists.")
            product.acknowledge_persisted()
            self._store.products[product.id.value] = copy.deepcopy(product)
            return
        if current is None or current.version != product.loaded_version:
            raise ConcurrentModificationError("The product was changed by another request.")
        product.acknowledge_persisted()
        self._store.products[product.id.value] = copy.deepcopy(product)

    def list_page(self, *, limit: int, offset: int) -> list[Product]:
        rows = sorted(self._store.products.values(), key=lambda product: (product.name, product.id.value))
        return [copy.deepcopy(product) for product in rows[offset : offset + limit]]


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get(self, customer_id: CustomerId) -> Customer | None:
        row = self._store.customers.get(customer_id.value)
        return None if row is None else _working_copy(row)

    def get_by_email(self, email: str) -> Customer | None:
        for customer in self._store.customers.values():
            if customer.email == email:
                return copy.deepcopy(customer)
        return None

    def add(self, customer: Customer) -> None:
        current = self._store.customers.get(customer.id.value)
        if customer.loaded_version is None:
            if current is not None:
                raise ConflictError("Customer already exists.")
            customer.acknowledge_persisted()
            self._store.customers[customer.id.value] = copy.deepcopy(customer)
            return
        if current is None or current.version != customer.loaded_version:
            raise ConcurrentModificationError("The customer was changed by another request.")
        customer.acknowledge_persisted()
        self._store.customers[customer.id.value] = copy.deepcopy(customer)

    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
    ) -> list[Customer]:
        rows = sorted(
            self._store.customers.values(),
            key=lambda customer: (customer.created_at, customer.id.value),
            reverse=True,
        )
        if created_before is not None and id_before is not None:
            rows = [
                customer
                for customer in rows
                if (customer.created_at, customer.id.value) < (created_before, id_before)
            ]
        return [copy.deepcopy(customer) for customer in rows[:limit]]


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get(self, order_id: OrderId) -> Order | None:
        row = self._store.orders.get(order_id.value)
        return None if row is None else _working_copy(row)

    def add(self, order: Order) -> None:
        current = self._store.orders.get(order.id.value)
        if order.loaded_version is None:
            if current is not None:
                raise ConflictError("Order already exists.")
            order.acknowledge_persisted()
            self._store.orders[order.id.value] = copy.deepcopy(order)
            return
        if current is None or current.version != order.loaded_version:
            raise ConcurrentModificationError("The order was changed by another request.")
        order.acknowledge_persisted()
        self._store.orders[order.id.value] = copy.deepcopy(order)

    def list_page(
        self,
        *,
        limit: int,
        created_before: datetime | None,
        id_before: uuid.UUID | None,
        customer_id: uuid.UUID | None = None,
    ) -> list[Order]:
        rows = sorted(
            self._store.orders.values(),
            key=lambda order: (order.created_at, order.id.value),
            reverse=True,
        )
        if customer_id is not None:
            rows = [order for order in rows if order.customer_id.value == customer_id]
        if created_before is not None and id_before is not None:
            rows = [
                order
                for order in rows
                if (order.created_at, order.id.value) < (created_before, id_before)
            ]
        return [copy.deepcopy(order) for order in rows[:limit]]


class InMemoryAccountRepository(AccountRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get(self, account_id: AccountId) -> Account | None:
        row = self._store.accounts.get(account_id.value)
        return None if row is None else copy.deepcopy(row)

    def get_by_email(self, email: str) -> Account | None:
        for account in self._store.accounts.values():
            if account.email == email:
                return copy.deepcopy(account)
        return None

    def add(self, account: Account) -> None:
        if account.id.value in self._store.accounts:
            raise ConflictError("Account already exists.")
        self._store.accounts[account.id.value] = copy.deepcopy(account)


class InMemoryRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        for token in self._store.refresh_tokens.values():
            if token.token_hash == token_hash:
                return copy.deepcopy(token)
        return None

    def add(self, token: RefreshToken) -> None:
        if token.id in self._store.refresh_tokens:
            raise ConflictError("Refresh token already exists.")
        self._store.refresh_tokens[token.id] = copy.deepcopy(token)

    def save(self, token: RefreshToken) -> None:
        if token.id not in self._store.refresh_tokens:
            raise NotFoundError("Refresh token not found.")
        self._store.refresh_tokens[token.id] = copy.deepcopy(token)


class InMemorySagaRepository(SagaRepository):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def get(self, saga_id: uuid.UUID) -> SagaInstance | None:
        row = self._store.sagas.get(saga_id)
        return None if row is None else copy.deepcopy(row)

    def get_by_order(self, order_id: uuid.UUID) -> SagaInstance | None:
        for saga in self._store.sagas.values():
            if saga.order_id == order_id:
                return copy.deepcopy(saga)
        return None

    def add(self, saga: SagaInstance) -> None:
        current = self._store.sagas.get(saga.id)
        if saga.loaded_version is None:
            if current is not None:
                raise ConflictError("Saga already exists.")
            saga.acknowledge_persisted()
            self._store.sagas[saga.id] = copy.deepcopy(saga)
            return
        if current is None or current.version != saga.loaded_version:
            raise ConcurrentModificationError("The saga was changed by another worker.")
        saga.acknowledge_persisted()
        self._store.sagas[saga.id] = copy.deepcopy(saga)

    def next_active(self) -> SagaInstance | None:
        rows = [
            saga
            for saga in self._store.sagas.values()
            if saga.status not in TERMINAL_SAGA_STATUSES
        ]
        if not rows:
            return None
        chosen = sorted(rows, key=lambda saga: (saga.updated_at, saga.id))[0]
        return copy.deepcopy(chosen)


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self, store: MemoryStore) -> None:
        self._store = store
        self._snapshot = store.snapshot()
        self._committed = False
        self.products = InMemoryProductRepository(store)
        self.customers = InMemoryCustomerRepository(store)
        self.orders = InMemoryOrderRepository(store)
        self.sagas = InMemorySagaRepository(store)
        self.accounts = InMemoryAccountRepository(store)
        self.refresh_tokens = InMemoryRefreshTokenRepository(store)

    def stage_events(self, *aggregates: RecordsEvents) -> None:
        for record in stage_outbox_records(*aggregates):
            if record.id in self._store.outbox:
                raise ConflictError("Outbox event already exists.")
            self._store.outbox[record.id] = record

    def stage_outbox(self, records: list[OutboxRecord]) -> None:
        for record in records:
            if record.id in self._store.outbox:
                raise ConflictError("Outbox event already exists.")
            self._store.outbox[record.id] = record

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        if not self._committed:
            self._store.restore(self._snapshot)

    def close(self) -> None:
        if not self._committed:
            self.rollback()

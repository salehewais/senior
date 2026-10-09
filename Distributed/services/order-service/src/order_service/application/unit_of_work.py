"""Transaction boundary. One unit of work touches order_db and nothing else.

Staging an outbox row is part of that transaction. The broker is not.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from order_service.application.outbox import OutboxRecord, stage_outbox_records
from order_service.application.publishing import RecordsEvents
from order_service.domain.repositories import (
    AccountRepository,
    CustomerRepository,
    OrderRepository,
    ProductRepository,
    RefreshTokenRepository,
    SagaRepository,
)


class UnitOfWork(ABC):
    products: ProductRepository
    customers: CustomerRepository
    orders: OrderRepository
    sagas: SagaRepository
    accounts: AccountRepository
    refresh_tokens: RefreshTokenRepository

    @abstractmethod
    def stage_events(self, *aggregates: RecordsEvents) -> None:
        """Insert one pending outbox row per domain event. Call this before commit."""

    @abstractmethod
    def stage_outbox(self, records: list[OutboxRecord]) -> None:
        """Insert command rows in this same transaction. Call this before commit."""

    @abstractmethod
    def commit(self) -> None:
        """Make every write in this unit visible, or raise and leave them invisible."""

    @abstractmethod
    def rollback(self) -> None:
        """Discard writes that have not been committed."""

    @abstractmethod
    def close(self) -> None:
        """Return the connection. Rolls back if commit was not called."""

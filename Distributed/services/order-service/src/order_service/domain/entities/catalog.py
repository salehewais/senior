"""Storefront catalog. The price copied onto an order line does not follow later edits."""

from __future__ import annotations

import uuid
from datetime import datetime

from order_service.domain.email import normalize_email
from order_service.domain.events import CustomerUpdated, ProductCreated, ProductUpdated
from order_service.domain.exceptions import DomainValidationError
from order_service.domain.ids import CustomerId, ProductId, uuid7
from order_service.domain.value_objects import Money


def _required_text(value: str, field: str, limit: int) -> str:
    if not isinstance(value, str):
        raise DomainValidationError(f"{field} must be text.")
    cleaned = value.strip()
    if not cleaned:
        raise DomainValidationError(f"{field} is required.")
    if len(cleaned) > limit:
        raise DomainValidationError(f"{field} cannot be longer than {limit} characters.")
    return cleaned


class Product:
    def __init__(
        self,
        *,
        product_id: ProductId,
        sku: str,
        name: str,
        unit_price: Money,
        active: bool,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        loaded_version: int | None = None,
    ) -> None:
        self.id = product_id
        self.sku = sku
        self.name = name
        self.unit_price = unit_price
        self.active = active
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self._loaded_version = loaded_version
        self._events: list[ProductCreated | ProductUpdated] = []

    @property
    def loaded_version(self) -> int | None:
        return self._loaded_version

    def acknowledge_persisted(self) -> None:
        self._loaded_version = self.version

    def collect_events(self) -> list[ProductCreated | ProductUpdated]:
        events = list(self._events)
        self._events.clear()
        return events

    def pending_events(self) -> tuple[ProductCreated | ProductUpdated, ...]:
        return tuple(self._events)

    @classmethod
    def create(
        cls,
        *,
        sku: str,
        name: str,
        unit_price: Money,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        active: bool = True,
        product_id: ProductId | None = None,
    ) -> Product:
        product = cls(
            product_id=product_id or ProductId.generate(),
            sku=_required_text(sku, "sku", 64),
            name=_required_text(name, "name", 200),
            unit_price=unit_price,
            active=active,
            version=1,
            created_at=now,
            updated_at=now,
        )
        product._events.append(
            ProductCreated(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=product.id.value,
                aggregate_version=1,
                correlation_id=correlation_id,
                causation_id=causation_id,
                sku=product.sku,
                name=product.name,
                unit_price=unit_price,
                active=active,
            )
        )
        return product

    @classmethod
    def reconstitute(
        cls,
        *,
        product_id: ProductId,
        sku: str,
        name: str,
        unit_price: Money,
        active: bool,
        version: int,
        created_at: datetime,
        updated_at: datetime,
    ) -> Product:
        return cls(
            product_id=product_id,
            sku=sku,
            name=name,
            unit_price=unit_price,
            active=active,
            version=version,
            created_at=created_at,
            updated_at=updated_at,
            loaded_version=version,
        )

    def update(
        self,
        *,
        name: str | None,
        unit_price: Money | None,
        active: bool | None,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        if name is None and unit_price is None and active is None:
            raise DomainValidationError("A product update needs at least one field.")
        if name is not None:
            self.name = _required_text(name, "name", 200)
        if unit_price is not None:
            self.unit_price = unit_price
        if active is not None:
            self.active = active
        self.version += 1
        self.updated_at = now
        self._events.append(
            ProductUpdated(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                sku=self.sku,
                name=self.name,
                unit_price=self.unit_price,
                active=self.active,
            )
        )


class Customer:
    def __init__(
        self,
        *,
        customer_id: CustomerId,
        email: str,
        display_name: str,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        loaded_version: int | None = None,
    ) -> None:
        self.id = customer_id
        self.email = email
        self.display_name = display_name
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self._loaded_version = loaded_version
        self._events: list[CustomerUpdated] = []

    @property
    def loaded_version(self) -> int | None:
        return self._loaded_version

    def acknowledge_persisted(self) -> None:
        self._loaded_version = self.version

    def collect_events(self) -> list[CustomerUpdated]:
        events = list(self._events)
        self._events.clear()
        return events

    def pending_events(self) -> tuple[CustomerUpdated, ...]:
        return tuple(self._events)

    @classmethod
    def create(
        cls,
        *,
        email: str,
        display_name: str,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        customer_id: CustomerId | None = None,
    ) -> Customer:
        customer = cls(
            customer_id=customer_id or CustomerId.generate(),
            email=_email(email),
            display_name=_required_text(display_name, "display_name", 120),
            version=1,
            created_at=now,
            updated_at=now,
        )
        customer._events.append(
            CustomerUpdated(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=customer.id.value,
                aggregate_version=1,
                correlation_id=correlation_id,
                causation_id=causation_id,
                email=customer.email,
                display_name=customer.display_name,
            )
        )
        return customer

    @classmethod
    def reconstitute(
        cls,
        *,
        customer_id: CustomerId,
        email: str,
        display_name: str,
        version: int,
        created_at: datetime,
        updated_at: datetime,
    ) -> Customer:
        return cls(
            customer_id=customer_id,
            email=email,
            display_name=display_name,
            version=version,
            created_at=created_at,
            updated_at=updated_at,
            loaded_version=version,
        )

    def rename(
        self,
        *,
        display_name: str,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        self.display_name = _required_text(display_name, "display_name", 120)
        self.version += 1
        self.updated_at = now
        self._events.append(
            CustomerUpdated(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                email=self.email,
                display_name=self.display_name,
            )
        )


def _email(value: str) -> str:
    return normalize_email(value)

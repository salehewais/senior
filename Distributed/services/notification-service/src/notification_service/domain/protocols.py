"""Store contract used by services. Implementations live in persistence."""

from __future__ import annotations

import uuid
from contextlib import AbstractContextManager
from typing import Protocol

from notification_service.domain.records import DeliveryRecord, DeviceToken, ListedDelivery


class Store(Protocol):
    def ping(self) -> bool: ...

    def transaction(self) -> AbstractContextManager[None]: ...

    def seen(self, event_id: uuid.UUID) -> bool: ...

    def mark(self, event_id: uuid.UUID, event_type: str) -> None: ...

    def remember_contact(self, order_id: uuid.UUID, account_id: uuid.UUID) -> None: ...

    def contact_for(self, order_id: uuid.UUID) -> uuid.UUID | None: ...

    def add_delivery(self, record: DeliveryRecord) -> None: ...

    def list_deliveries(self) -> list[ListedDelivery]: ...

    def register_token(self, account_id: uuid.UUID, token: object, platform: object) -> tuple[DeviceToken, bool]: ...

    def list_tokens(self, account_id: uuid.UUID) -> list[DeviceToken]: ...

    def delete_token(self, account_id: uuid.UUID, token_id: uuid.UUID) -> bool: ...


class NotificationEvent(Protocol):
    """Fields apply_notification reads. The messaging envelope satisfies this."""

    event_id: uuid.UUID
    event_type: str
    aggregate_id: uuid.UUID
    payload: dict[str, object]

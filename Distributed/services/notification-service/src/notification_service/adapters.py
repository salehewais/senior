"""Mock email and mock push. They record a row. They do not call a provider."""

from __future__ import annotations

import uuid

from notification_service.outcomes import TransientDeliveryError
from notification_service.store import DeliveryRecord, MemoryStore, SqlStore

Store = MemoryStore | SqlStore


class MockEmail:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.attempts = 0

    def deliver(self, store: Store, *, event_id: uuid.UUID, account_id: uuid.UUID, event_type: str) -> None:
        self.attempts += 1
        if self.fail:
            raise TransientDeliveryError("mock email failed")
        store.add_delivery(
            DeliveryRecord(
                event_id=event_id,
                channel="email",
                account_id=account_id,
                destination=f"account:{account_id}",
                summary=event_type,
            )
        )


class MockPush:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.attempts = 0

    def deliver(self, store: Store, *, event_id: uuid.UUID, account_id: uuid.UUID, event_type: str) -> None:
        self.attempts += 1
        if self.fail:
            raise TransientDeliveryError("mock push failed")
        tokens = store.list_tokens(account_id)
        if not tokens:
            store.add_delivery(
                DeliveryRecord(
                    event_id=event_id,
                    channel="push",
                    account_id=account_id,
                    destination="no-device",
                    summary=event_type,
                )
            )
            return
        for device in tokens:
            store.add_delivery(
                DeliveryRecord(
                    event_id=event_id,
                    channel="push",
                    account_id=account_id,
                    destination=device.token,
                    summary=event_type,
                )
            )

"""Register, list, and delete device tokens for one account."""

from __future__ import annotations

import uuid

from notification_service.domain.protocols import Store
from notification_service.domain.records import DeviceToken


def register_token(store: Store, account_id: uuid.UUID, token: object, platform: object) -> tuple[DeviceToken, bool]:
    with store.transaction():
        return store.register_token(account_id, token, platform)


def list_tokens(store: Store, account_id: uuid.UUID) -> list[DeviceToken]:
    with store.transaction():
        return store.list_tokens(account_id)


def delete_token(store: Store, account_id: uuid.UUID, token_id: uuid.UUID) -> bool:
    with store.transaction():
        return store.delete_token(account_id, token_id)

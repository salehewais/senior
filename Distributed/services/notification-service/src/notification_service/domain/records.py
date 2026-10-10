"""Device tokens and delivery rows. No database session lives here."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

PLATFORMS = frozenset({"android", "ios"})


@dataclass(frozen=True, slots=True)
class DeviceToken:
    id: uuid.UUID
    account_id: uuid.UUID
    token: str
    platform: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class DeliveryRecord:
    event_id: uuid.UUID
    channel: str
    account_id: uuid.UUID
    destination: str
    summary: str


@dataclass(frozen=True, slots=True)
class ListedDelivery:
    channel: str
    summary: str
    account_id: uuid.UUID
    destination: str
    created_at: datetime


def validate_token(token: object, platform: object) -> tuple[str, str]:
    if not isinstance(token, str) or not isinstance(platform, str):
        raise ValueError("invalid")
    cleaned = token.strip()
    if not cleaned or len(cleaned) > 4096 or any(char in cleaned for char in "\r\n"):
        raise ValueError("invalid")
    kind = platform.strip().lower()
    if kind not in PLATFORMS:
        raise ValueError("invalid")
    return cleaned, kind

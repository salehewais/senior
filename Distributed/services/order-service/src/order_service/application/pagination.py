"""Opaque cursors. Clients must not parse them. Invalid input is a validation error."""

from __future__ import annotations

import base64
import uuid
from datetime import datetime

from order_service.domain.exceptions import DomainValidationError


def encode_cursor(created_at: datetime, entity_id: uuid.UUID) -> str:
    raw = f"{created_at.isoformat()}|{entity_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        padded = cursor + ("=" * (-len(cursor) % 4))
        text = base64.urlsafe_b64decode(padded.encode()).decode()
        timestamp, entity_id = text.split("|", 1)
        created_at = datetime.fromisoformat(timestamp)
        parsed = uuid.UUID(entity_id)
    except (ValueError, UnicodeError, TypeError) as exc:
        raise DomainValidationError("cursor is invalid.") from exc
    if created_at.tzinfo is None:
        raise DomainValidationError("cursor is invalid.")
    return created_at, parsed

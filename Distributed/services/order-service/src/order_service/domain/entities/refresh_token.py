"""Server-side refresh session. Only the hash of the secret is kept."""

from __future__ import annotations

import uuid
from datetime import datetime


class RefreshToken:
    def __init__(
        self,
        *,
        token_id: uuid.UUID,
        account_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        revoked_at: datetime | None,
        parent_id: uuid.UUID | None,
        created_at: datetime,
    ) -> None:
        self.id = token_id
        self.account_id = account_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked_at = revoked_at
        self.parent_id = parent_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return (
            f"RefreshToken(id={self.id}, account_id={self.account_id}, "
            f"revoked={self.revoked_at is not None})"
        )

    def revoke(self, now: datetime) -> None:
        if self.revoked_at is None:
            self.revoked_at = now

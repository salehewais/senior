"""Login identity. The password hash is stored. The password is not."""

from __future__ import annotations

from datetime import datetime

from order_service.domain.email import normalize_email
from order_service.domain.exceptions import DomainValidationError
from order_service.domain.ids import AccountId
from order_service.domain.roles import Role


class Account:
    def __init__(
        self,
        *,
        account_id: AccountId,
        email: str,
        password_hash: str,
        role: Role,
        created_at: datetime,
    ) -> None:
        self.id = account_id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    def __repr__(self) -> str:
        # The hash must not show up in logs that print the account.
        return f"Account(id={self.id}, email={self.email}, role={self.role.value})"

    @classmethod
    def create(
        cls,
        *,
        email: str,
        password_hash: str,
        role: Role,
        now: datetime,
        account_id: AccountId | None = None,
    ) -> Account:
        if not isinstance(password_hash, str) or not password_hash.strip():
            raise DomainValidationError("password hash is missing.")
        if not isinstance(role, Role):
            raise DomainValidationError("role is not valid.")
        return cls(
            account_id=account_id or AccountId.generate(),
            email=normalize_email(email),
            password_hash=password_hash,
            role=role,
            created_at=now,
        )

    @classmethod
    def reconstitute(
        cls,
        *,
        account_id: AccountId,
        email: str,
        password_hash: str,
        role: Role,
        created_at: datetime,
    ) -> Account:
        return cls(
            account_id=account_id,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=created_at,
        )

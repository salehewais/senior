"""Register, login, refresh, and logout. Role always comes from the account row."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from order_service.application.auth_policy import ACCESS_TOKEN_TTL_SECONDS, REFRESH_TOKEN_TTL
from order_service.application.clock import Clock
from order_service.application.ports import AccessTokenIssuer, PasswordHasher, RefreshTokenCodec
from order_service.application.publishing import EventPublisher, publish_after_commit
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.email import normalize_email
from order_service.domain.entities.account import Account
from order_service.domain.entities.catalog import Customer
from order_service.domain.entities.refresh_token import RefreshToken
from order_service.domain.exceptions import (
    ConflictError,
    DependencyUnavailableError,
    DomainValidationError,
    UnauthenticatedError,
)
from order_service.domain.ids import AccountId, CustomerId, uuid7
from order_service.domain.roles import Role

_LOGIN_FAILURE = "Email or password is incorrect."
_AUTH_REQUIRED = "Authentication is required."


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
    account_id: uuid.UUID
    role: str


class RegisterAccount:
    """Public registration always creates a customer. A role in the request is not a parameter."""

    def __init__(
        self,
        clock: Clock,
        passwords: PasswordHasher,
        tokens: AccessTokenIssuer | None,
        refresh_tokens: RefreshTokenCodec,
        publisher: EventPublisher | None = None,
        *,
        refresh_ttl: timedelta = REFRESH_TOKEN_TTL,
    ) -> None:
        self._clock = clock
        self._passwords = passwords
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens
        self._publisher = publisher
        self._refresh_ttl = refresh_ttl

    def execute(
        self,
        uow: UnitOfWork,
        *,
        email: str,
        display_name: str,
        password: str,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> TokenPair:
        self._require_keys()
        normalized = normalize_email(email)
        checked = _checked_password(password)
        if uow.accounts.get_by_email(normalized) is not None or uow.customers.get_by_email(normalized) is not None:
            raise ConflictError("A customer with that email already exists.")
        now = self._clock.now()
        account = Account.create(
            email=normalized,
            password_hash=self._passwords.hash_password(checked),
            role=Role.CUSTOMER,
            now=now,
        )
        # The profile and the login row share an id so the access token subject is the customer id.
        customer = Customer.create(
            email=account.email,
            display_name=display_name,
            now=now,
            correlation_id=correlation_id,
            causation_id=causation_id,
            customer_id=CustomerId(account.id.value),
        )
        uow.accounts.add(account)
        uow.customers.add(customer)
        raw_refresh = _store_refresh(
            uow,
            codec=self._refresh_tokens,
            account_id=account.id.value,
            parent_id=None,
            now=now,
            ttl=self._refresh_ttl,
        )
        access = self._issue(account, now)
        uow.commit()
        publish_after_commit(self._publisher, customer)
        return _pair(access, raw_refresh, account)

    def _require_keys(self) -> None:
        if self._tokens is None:
            raise DependencyUnavailableError("Token signing keys are not configured.")

    def _issue(self, account: Account, now: datetime) -> str:
        assert self._tokens is not None
        return self._tokens.issue(account_id=account.id.value, role=account.role.value, now=now)


class LoginAccount:
    def __init__(
        self,
        clock: Clock,
        passwords: PasswordHasher,
        tokens: AccessTokenIssuer | None,
        refresh_tokens: RefreshTokenCodec,
        *,
        refresh_ttl: timedelta = REFRESH_TOKEN_TTL,
    ) -> None:
        self._clock = clock
        self._passwords = passwords
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens
        self._refresh_ttl = refresh_ttl

    def execute(self, uow: UnitOfWork, *, email: str, password: str) -> TokenPair:
        if self._tokens is None:
            raise DependencyUnavailableError("Token signing keys are not configured.")
        account = _account_for_login(uow, email)
        if account is None:
            # Unknown email and a wrong password must cost a hash check and return the same error.
            self._passwords.verify_dummy(password)
            raise UnauthenticatedError(_LOGIN_FAILURE)
        if not self._passwords.verify_password(password, account.password_hash):
            raise UnauthenticatedError(_LOGIN_FAILURE)
        now = self._clock.now()
        raw_refresh = _store_refresh(
            uow,
            codec=self._refresh_tokens,
            account_id=account.id.value,
            parent_id=None,
            now=now,
            ttl=self._refresh_ttl,
        )
        access = self._tokens.issue(account_id=account.id.value, role=account.role.value, now=now)
        uow.commit()
        return _pair(access, raw_refresh, account)


class RefreshSession:
    """Rotate the refresh token in the same transaction that revokes the one just presented."""

    def __init__(
        self,
        clock: Clock,
        tokens: AccessTokenIssuer | None,
        refresh_tokens: RefreshTokenCodec,
        *,
        refresh_ttl: timedelta = REFRESH_TOKEN_TTL,
    ) -> None:
        self._clock = clock
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens
        self._refresh_ttl = refresh_ttl

    def execute(self, uow: UnitOfWork, *, refresh_token: str) -> TokenPair:
        if self._tokens is None:
            raise DependencyUnavailableError("Token signing keys are not configured.")
        now = self._clock.now()
        record = _presented(uow, self._refresh_tokens, refresh_token)
        if record is None or record.revoked_at is not None or record.expires_at <= now:
            raise UnauthenticatedError(_AUTH_REQUIRED)
        account = uow.accounts.get(AccountId(record.account_id))
        if account is None:
            raise UnauthenticatedError(_AUTH_REQUIRED)
        record.revoke(now)
        uow.refresh_tokens.save(record)
        raw_refresh = _store_refresh(
            uow,
            codec=self._refresh_tokens,
            account_id=account.id.value,
            parent_id=record.id,
            now=now,
            ttl=self._refresh_ttl,
        )
        access = self._tokens.issue(account_id=account.id.value, role=account.role.value, now=now)
        uow.commit()
        return _pair(access, raw_refresh, account)


class LogoutSession:
    def __init__(self, clock: Clock, refresh_tokens: RefreshTokenCodec) -> None:
        self._clock = clock
        self._refresh_tokens = refresh_tokens

    def execute(self, uow: UnitOfWork, *, refresh_token: str) -> None:
        record = _presented(uow, self._refresh_tokens, refresh_token)
        if record is None:
            raise UnauthenticatedError(_AUTH_REQUIRED)
        if record.revoked_at is None:
            record.revoke(self._clock.now())
            uow.refresh_tokens.save(record)
        uow.commit()


class CreateStaffAccount:
    """Not exposed over HTTP. Public register cannot create admin or manager."""

    def __init__(self, clock: Clock, passwords: PasswordHasher) -> None:
        self._clock = clock
        self._passwords = passwords

    def execute(self, uow: UnitOfWork, *, email: str, password: str, role: Role) -> uuid.UUID:
        if role not in (Role.ADMIN, Role.MANAGER):
            raise DomainValidationError("Staff accounts must be admin or manager.")
        normalized = normalize_email(email)
        checked = _checked_password(password)
        if uow.accounts.get_by_email(normalized) is not None:
            raise ConflictError("An account with that email already exists.")
        account = Account.create(
            email=normalized,
            password_hash=self._passwords.hash_password(checked),
            role=role,
            now=self._clock.now(),
        )
        uow.accounts.add(account)
        uow.commit()
        return account.id.value


def _checked_password(password: str) -> str:
    if not isinstance(password, str) or len(password) < 8 or len(password) > 128:
        raise DomainValidationError("password must be between 8 and 128 characters.")
    return password


def _account_for_login(uow: UnitOfWork, email: str) -> Account | None:
    try:
        normalized = normalize_email(email)
    except DomainValidationError:
        return None
    return uow.accounts.get_by_email(normalized)


def _presented(uow: UnitOfWork, codec: RefreshTokenCodec, raw: str) -> RefreshToken | None:
    if not isinstance(raw, str) or not raw:
        return None
    return uow.refresh_tokens.get_by_hash(codec.hash_secret(raw))


def _store_refresh(
    uow: UnitOfWork,
    *,
    codec: RefreshTokenCodec,
    account_id: uuid.UUID,
    parent_id: uuid.UUID | None,
    now: datetime,
    ttl: timedelta,
) -> str:
    raw = codec.new_secret()
    uow.refresh_tokens.add(
        RefreshToken(
            token_id=uuid7(),
            account_id=account_id,
            token_hash=codec.hash_secret(raw),
            expires_at=now + ttl,
            revoked_at=None,
            parent_id=parent_id,
            created_at=now,
        )
    )
    return raw


def _pair(access: str, refresh: str, account: Account) -> TokenPair:
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TOKEN_TTL_SECONDS,
        account_id=account.id.value,
        role=account.role.value,
    )

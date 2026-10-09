"""Persistence for notification_db. MemoryStore is the test double."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from notification_service.models import (
    DeviceTokenRow,
    NotificationDeliveryRow,
    OrderContactRow,
    ProcessedEventRow,
)
from notification_service.settings import db_connect_timeout_seconds, notification_database_url

PLATFORMS = frozenset({"android", "ios"})
_session: ContextVar[Session | None] = ContextVar("notification_session", default=None)


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


class MemoryStore:
    def __init__(self) -> None:
        self.processed: dict[uuid.UUID, str] = {}
        self.deliveries: list[DeliveryRecord] = []
        self.tokens: list[DeviceToken] = []
        self.contacts: dict[uuid.UUID, uuid.UUID] = {}
        self.reachable = True

    def ping(self) -> bool:
        return self.reachable

    @contextmanager
    def transaction(self) -> Iterator[None]:
        snapshot = (
            dict(self.processed),
            list(self.deliveries),
            list(self.tokens),
            dict(self.contacts),
        )
        try:
            yield
        except Exception:
            self.processed, self.deliveries, self.tokens, self.contacts = snapshot
            raise

    def seen(self, event_id: uuid.UUID) -> bool:
        return event_id in self.processed

    def mark(self, event_id: uuid.UUID, event_type: str) -> None:
        self.processed[event_id] = event_type

    def remember_contact(self, order_id: uuid.UUID, account_id: uuid.UUID) -> None:
        self.contacts[order_id] = account_id

    def contact_for(self, order_id: uuid.UUID) -> uuid.UUID | None:
        return self.contacts.get(order_id)

    def add_delivery(self, record: DeliveryRecord) -> None:
        self.deliveries.append(record)

    def register_token(self, account_id: uuid.UUID, token: object, platform: object) -> tuple[DeviceToken, bool]:
        cleaned, kind = validate_token(token, platform)
        for existing in self.tokens:
            if existing.account_id == account_id and existing.token == cleaned:
                return existing, False
        row = DeviceToken(
            id=uuid.uuid4(),
            account_id=account_id,
            token=cleaned,
            platform=kind,
            created_at=datetime.now(UTC),
        )
        self.tokens.append(row)
        return row, True

    def list_tokens(self, account_id: uuid.UUID) -> list[DeviceToken]:
        return [row for row in self.tokens if row.account_id == account_id]

    def delete_token(self, account_id: uuid.UUID, token_id: uuid.UUID) -> bool:
        kept: list[DeviceToken] = []
        removed = False
        for row in self.tokens:
            if row.id == token_id and row.account_id == account_id:
                removed = True
                continue
            kept.append(row)
        self.tokens = kept
        return removed


class SqlStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._factory = sessionmaker(bind=engine, expire_on_commit=False)

    @classmethod
    def from_settings(cls) -> SqlStore:
        url = notification_database_url()
        engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": db_connect_timeout_seconds()},
        )
        return cls(engine)

    def ping(self) -> bool:
        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @contextmanager
    def transaction(self) -> Iterator[None]:
        session = self._factory()
        token = _session.set(session)
        try:
            yield
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            _session.reset(token)
            session.close()

    def _current(self) -> Session:
        session = _session.get()
        if session is None:
            raise RuntimeError("notification store method called outside a transaction")
        return session

    def seen(self, event_id: uuid.UUID) -> bool:
        return self._current().get(ProcessedEventRow, event_id) is not None

    def mark(self, event_id: uuid.UUID, event_type: str) -> None:
        self._current().add(
            ProcessedEventRow(event_id=event_id, event_type=event_type, processed_at=datetime.now(UTC))
        )

    def remember_contact(self, order_id: uuid.UUID, account_id: uuid.UUID) -> None:
        session = self._current()
        row = session.get(OrderContactRow, order_id)
        if row is None:
            session.add(OrderContactRow(order_id=order_id, account_id=account_id))
        else:
            row.account_id = account_id

    def contact_for(self, order_id: uuid.UUID) -> uuid.UUID | None:
        row = self._current().get(OrderContactRow, order_id)
        if row is None:
            return None
        return row.account_id

    def add_delivery(self, record: DeliveryRecord) -> None:
        self._current().add(
            NotificationDeliveryRow(
                id=uuid.uuid4(),
                event_id=record.event_id,
                channel=record.channel,
                account_id=record.account_id,
                destination=record.destination,
                summary=record.summary,
                created_at=datetime.now(UTC),
            )
        )

    def register_token(self, account_id: uuid.UUID, token: object, platform: object) -> tuple[DeviceToken, bool]:
        cleaned, kind = validate_token(token, platform)
        session = self._current()
        existing = session.scalar(
            select(DeviceTokenRow).where(DeviceTokenRow.account_id == account_id, DeviceTokenRow.token == cleaned)
        )
        if existing is not None:
            return _token(existing), False
        row = DeviceTokenRow(
            id=uuid.uuid4(),
            account_id=account_id,
            token=cleaned,
            platform=kind,
            created_at=datetime.now(UTC),
        )
        session.add(row)
        return _token(row), True

    def list_tokens(self, account_id: uuid.UUID) -> list[DeviceToken]:
        rows = self._current().scalars(select(DeviceTokenRow).where(DeviceTokenRow.account_id == account_id))
        return [_token(row) for row in rows]

    def delete_token(self, account_id: uuid.UUID, token_id: uuid.UUID) -> bool:
        session = self._current()
        row = session.get(DeviceTokenRow, token_id)
        if row is None or row.account_id != account_id:
            return False
        session.delete(row)
        return True

    def deliveries_for(self, event_id: uuid.UUID) -> list[DeliveryRecord]:
        rows = self._current().scalars(
            select(NotificationDeliveryRow).where(NotificationDeliveryRow.event_id == event_id)
        )
        return [
            DeliveryRecord(
                event_id=row.event_id,
                channel=row.channel,
                account_id=row.account_id,
                destination=row.destination,
                summary=row.summary,
            )
            for row in rows
        ]


def _token(row: DeviceTokenRow) -> DeviceToken:
    return DeviceToken(
        id=row.id,
        account_id=row.account_id,
        token=row.token,
        platform=row.platform,
        created_at=row.created_at,
    )

from sqlalchemy.orm import Session

from order_service.application.outbox import OutboxRecord, stage_outbox_records
from order_service.application.publishing import RecordsEvents
from order_service.application.unit_of_work import UnitOfWork
from order_service.infrastructure.database.models import OutboxRow
from order_service.infrastructure.database.repositories import (
    SqlAccountRepository,
    SqlCustomerRepository,
    SqlOrderRepository,
    SqlProductRepository,
    SqlRefreshTokenRepository,
)
from order_service.observability.metrics import record_outbox_created


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        self._session = session
        self._committed = False
        self._outbox_types: list[str] = []
        self.products = SqlProductRepository(session)
        self.customers = SqlCustomerRepository(session)
        self.orders = SqlOrderRepository(session)
        self.accounts = SqlAccountRepository(session)
        self.refresh_tokens = SqlRefreshTokenRepository(session)

    def stage_events(self, *aggregates: RecordsEvents) -> None:
        for record in stage_outbox_records(*aggregates):
            self._session.add(_outbox_row(record))
            self._outbox_types.append(record.event_type)

    def commit(self) -> None:
        self._session.commit()
        self._committed = True
        for event_type in self._outbox_types:
            record_outbox_created(event_type)
        self._outbox_types.clear()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        if not self._committed:
            self._session.rollback()
        self._session.close()


def _outbox_row(record: OutboxRecord) -> OutboxRow:
    return OutboxRow(
        id=record.id,
        event_type=record.event_type,
        aggregate_type=record.aggregate_type,
        aggregate_id=record.aggregate_id,
        payload=record.payload,
        created_at=record.created_at,
        published_at=record.published_at,
        retry_count=record.retry_count,
        status=record.status,
    )

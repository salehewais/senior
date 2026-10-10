import logging

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from order_service.application.outbox import OutboxRecord, stage_outbox_records
from order_service.application.publishing import RecordsEvents
from order_service.application.unit_of_work import UnitOfWork
from order_service.domain.exceptions import ConflictError, DependencyUnavailableError
from order_service.infrastructure.database.models import OutboxRow
from order_service.infrastructure.database.repositories import (
    SqlAccountRepository,
    SqlCustomerRepository,
    SqlOrderRepository,
    SqlProductRepository,
    SqlRefreshTokenRepository,
)
from order_service.infrastructure.database.saga_repository import SqlSagaRepository
from order_service.observability.metrics import record_outbox_created
from order_service.observability.tracing import current_trace_carrier

logger = logging.getLogger("order_service")

_CONFLICT = "The request conflicts with data already stored."
_UNAVAILABLE = "The order database is unavailable."
_GUARDED = ("flush", "commit", "get", "scalar", "scalars", "execute")


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        _translate_integrity_errors(session)
        self._session = session
        self._committed = False
        self._outbox_types: list[str] = []
        self.products = SqlProductRepository(session)
        self.customers = SqlCustomerRepository(session)
        self.orders = SqlOrderRepository(session)
        self.sagas = SqlSagaRepository(session)
        self.accounts = SqlAccountRepository(session)
        self.refresh_tokens = SqlRefreshTokenRepository(session)

    def stage_events(self, *aggregates: RecordsEvents) -> None:
        carrier = current_trace_carrier()
        for record in stage_outbox_records(*aggregates, trace_carrier=carrier):
            self._session.add(_outbox_row(record))
            self._outbox_types.append(record.event_type)

    def stage_outbox(self, records: list[OutboxRecord]) -> None:
        for record in records:
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


def _translate_integrity_errors(session: Session) -> None:
    """Database failures become domain errors before they leave this unit of work.

    A unique or foreign-key violation is a conflict. A connection or query failure
    is a dependency outage. HTTP maps those codes and does not import SQLAlchemy.
    """

    for name in _GUARDED:
        method = getattr(session, name, None)
        if method is None:
            continue
        setattr(session, name, _guard(method))


def _guard(method):
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except IntegrityError as exc:
            raise ConflictError(_CONFLICT) from exc
        except OperationalError as exc:
            logger.exception("database unavailable")
            raise DependencyUnavailableError(_UNAVAILABLE) from exc

    return wrapped


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

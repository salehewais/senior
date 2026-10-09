"""saga_instances in the same session as the order and the outbox."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from order_service.domain.entities.saga import SagaInstance
from order_service.domain.entities.saga_status import TERMINAL_SAGA_STATUSES, SagaStatus
from order_service.domain.exceptions import ConcurrentModificationError, ConflictError
from order_service.domain.repositories import SagaRepository
from order_service.infrastructure.database.models import SagaInstanceRow


class SqlSagaRepository(SagaRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, saga_id: uuid.UUID) -> SagaInstance | None:
        row = self._session.get(SagaInstanceRow, saga_id)
        return None if row is None else _saga(row)

    def get_by_order(self, order_id: uuid.UUID) -> SagaInstance | None:
        row = self._session.scalar(select(SagaInstanceRow).where(SagaInstanceRow.order_id == order_id))
        return None if row is None else _saga(row)

    def add(self, saga: SagaInstance) -> None:
        if saga.loaded_version is None:
            if self._session.get(SagaInstanceRow, saga.id) is not None:
                raise ConflictError("Saga already exists.")
            self._session.add(_row(saga))
            self._session.flush()
            saga.acknowledge_persisted()
            return
        row = self._session.get(SagaInstanceRow, saga.id)
        if row is None or row.version != saga.loaded_version:
            raise ConcurrentModificationError("The saga was changed by another worker.")
        row.status = saga.status.value
        row.version = saga.version
        row.completed_steps = list(saga.completed_steps)
        row.reservation_id = saga.reservation_id
        row.payment_reference = saga.payment_reference
        row.failure_reason = saga.failure_reason
        row.pending_step = saga.pending_step
        row.pending_outcome = saga.pending_outcome
        row.updated_at = saga.updated_at
        self._session.flush()
        saga.acknowledge_persisted()

    def next_active(self) -> SagaInstance | None:
        terminal = [status.value for status in TERMINAL_SAGA_STATUSES]
        stmt = (
            select(SagaInstanceRow)
            .where(SagaInstanceRow.status.notin_(terminal))
            .order_by(SagaInstanceRow.updated_at, SagaInstanceRow.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        row = self._session.scalar(stmt)
        return None if row is None else _saga(row)


def _row(saga: SagaInstance) -> SagaInstanceRow:
    return SagaInstanceRow(
        id=saga.id,
        order_id=saga.order_id,
        status=saga.status.value,
        correlation_id=saga.correlation_id,
        causation_id=saga.causation_id,
        version=saga.version,
        completed_steps=list(saga.completed_steps),
        reservation_id=saga.reservation_id,
        payment_reference=saga.payment_reference,
        failure_reason=saga.failure_reason,
        pending_step=saga.pending_step,
        pending_outcome=saga.pending_outcome,
        created_at=saga.created_at,
        updated_at=saga.updated_at,
    )


def _saga(row: SagaInstanceRow) -> SagaInstance:
    steps = row.completed_steps if isinstance(row.completed_steps, list) else []
    return SagaInstance.reconstitute(
        saga_id=row.id,
        order_id=row.order_id,
        status=SagaStatus(row.status),
        correlation_id=row.correlation_id,
        causation_id=row.causation_id,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
        completed_steps=tuple(str(step) for step in steps),
        reservation_id=row.reservation_id,
        payment_reference=row.payment_reference,
        failure_reason=row.failure_reason,
        pending_step=row.pending_step,
        pending_outcome=row.pending_outcome,
    )

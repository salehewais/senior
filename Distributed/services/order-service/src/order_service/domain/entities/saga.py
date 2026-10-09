"""One saga row. Process memory is not the record; this object is."""

from __future__ import annotations

import uuid
from datetime import datetime

from order_service.domain.entities.saga_status import (
    TERMINAL_SAGA_STATUSES,
    SagaStatus,
    require_saga_transition,
)

STEP_RESERVE = "reserve"
STEP_PAYMENT = "payment"
STEP_CREATE_ERP = "create_erp"
STEP_RELEASE = "release"
STEP_REFUND = "refund"
STEP_CANCEL_ERP = "cancel_erp"


class SagaInstance:
    def __init__(
        self,
        *,
        saga_id: uuid.UUID,
        order_id: uuid.UUID,
        status: SagaStatus,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        completed_steps: tuple[str, ...] = (),
        reservation_id: str | None = None,
        payment_reference: str | None = None,
        failure_reason: str | None = None,
        pending_step: str | None = None,
        pending_outcome: str | None = None,
        loaded_version: int | None = None,
    ) -> None:
        self.id = saga_id
        self.order_id = order_id
        self.status = status
        self.correlation_id = correlation_id
        self.causation_id = causation_id
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self.completed_steps = completed_steps
        self.reservation_id = reservation_id
        self.payment_reference = payment_reference
        self.failure_reason = failure_reason
        self.pending_step = pending_step
        self.pending_outcome = pending_outcome
        self._loaded_version = loaded_version

    @property
    def loaded_version(self) -> int | None:
        return self._loaded_version

    def acknowledge_persisted(self) -> None:
        self._loaded_version = self.version

    def is_terminal(self) -> bool:
        return self.status in TERMINAL_SAGA_STATUSES

    def has_step(self, name: str) -> bool:
        return name in self.completed_steps

    @classmethod
    def start(
        cls,
        *,
        order_id: uuid.UUID,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        saga_id: uuid.UUID | None = None,
    ) -> SagaInstance:
        return cls(
            saga_id=saga_id or uuid.uuid4(),
            order_id=order_id,
            status=SagaStatus.STARTED,
            correlation_id=correlation_id,
            causation_id=causation_id,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def reconstitute(
        cls,
        *,
        saga_id: uuid.UUID,
        order_id: uuid.UUID,
        status: SagaStatus,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        completed_steps: tuple[str, ...],
        reservation_id: str | None,
        payment_reference: str | None,
        failure_reason: str | None,
        pending_step: str | None,
        pending_outcome: str | None,
    ) -> SagaInstance:
        return cls(
            saga_id=saga_id,
            order_id=order_id,
            status=status,
            correlation_id=correlation_id,
            causation_id=causation_id,
            version=version,
            created_at=created_at,
            updated_at=updated_at,
            completed_steps=completed_steps,
            reservation_id=reservation_id,
            payment_reference=payment_reference,
            failure_reason=failure_reason,
            pending_step=pending_step,
            pending_outcome=pending_outcome,
            loaded_version=version,
        )

    def awaiting(self, step: str) -> bool:
        return self.pending_step == step and self.pending_outcome == "unknown"

    def note_unknown(self, step: str, now: datetime) -> None:
        if self.awaiting(step):
            return
        self.pending_step = step
        self.pending_outcome = "unknown"
        self._touch(now)

    def clear_pending(self, now: datetime) -> None:
        if self.pending_step is None and self.pending_outcome is None:
            return
        self.pending_step = None
        self.pending_outcome = None
        self._touch(now)

    def reserve_succeeded(self, reservation_id: str, now: datetime) -> None:
        self._transition(SagaStatus.INVENTORY_RESERVED, now)
        self._complete_step(STEP_RESERVE)
        self.reservation_id = reservation_id

    def reserve_failed(self, reason: str, now: datetime) -> None:
        self._transition(SagaStatus.FAILED, now)
        self.failure_reason = reason

    def payment_succeeded(self, payment_reference: str, now: datetime) -> None:
        self._transition(SagaStatus.PAYMENT_CONFIRMED, now)
        self._complete_step(STEP_PAYMENT)
        self.payment_reference = payment_reference

    def payment_failed(self, reason: str, now: datetime) -> None:
        self._transition(SagaStatus.COMPENSATING, now)
        self.failure_reason = reason

    def erp_succeeded(self, now: datetime) -> None:
        self._transition(SagaStatus.ODOO_ORDER_CREATED, now)
        self._complete_step(STEP_CREATE_ERP)

    def erp_failed(self, reason: str, now: datetime) -> None:
        self._transition(SagaStatus.COMPENSATING, now)
        self.failure_reason = reason

    def complete(self, now: datetime) -> None:
        self._transition(SagaStatus.COMPLETED, now)

    def compensation_succeeded(self, step: str, now: datetime) -> None:
        if self.status is not SagaStatus.COMPENSATING:
            require_saga_transition(self.status, SagaStatus.COMPENSATING)
        self._complete_step(step)
        self.pending_step = None
        self.pending_outcome = None
        self._touch(now)

    def compensation_finished(self, now: datetime) -> None:
        self._transition(SagaStatus.COMPENSATED, now)

    def compensation_failed(self, reason: str, now: datetime) -> None:
        self._transition(SagaStatus.MANUAL_INTERVENTION_REQUIRED, now)
        self.failure_reason = reason

    def _transition(self, target: SagaStatus, now: datetime) -> None:
        require_saga_transition(self.status, target)
        self.status = target
        self.pending_step = None
        self.pending_outcome = None
        self._touch(now)

    def _complete_step(self, name: str) -> None:
        if name not in self.completed_steps:
            self.completed_steps = (*self.completed_steps, name)

    def _touch(self, now: datetime) -> None:
        self.version += 1
        self.updated_at = now

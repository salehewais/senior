"""Saga states for Extension Phase 1.

These are not order statuses. COMPLETED means reserve, simulated payment, and
ERP create finished. It does not mean the parcel was delivered.
"""

from __future__ import annotations

from enum import StrEnum

from order_service.domain.exceptions import InvalidStateTransition


class SagaStatus(StrEnum):
    STARTED = "STARTED"
    INVENTORY_RESERVED = "INVENTORY_RESERVED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    ODOO_ORDER_CREATED = "ODOO_ORDER_CREATED"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"


TERMINAL_SAGA_STATUSES: frozenset[SagaStatus] = frozenset(
    {
        SagaStatus.COMPLETED,
        SagaStatus.COMPENSATED,
        SagaStatus.FAILED,
        SagaStatus.MANUAL_INTERVENTION_REQUIRED,
    }
)

ALLOWED_SAGA_TRANSITIONS: frozenset[tuple[SagaStatus, SagaStatus]] = frozenset(
    {
        (SagaStatus.STARTED, SagaStatus.INVENTORY_RESERVED),
        (SagaStatus.STARTED, SagaStatus.FAILED),
        (SagaStatus.INVENTORY_RESERVED, SagaStatus.PAYMENT_CONFIRMED),
        (SagaStatus.INVENTORY_RESERVED, SagaStatus.COMPENSATING),
        (SagaStatus.PAYMENT_CONFIRMED, SagaStatus.ODOO_ORDER_CREATED),
        (SagaStatus.PAYMENT_CONFIRMED, SagaStatus.COMPENSATING),
        (SagaStatus.ODOO_ORDER_CREATED, SagaStatus.COMPLETED),
        (SagaStatus.COMPENSATING, SagaStatus.COMPENSATED),
        (SagaStatus.COMPENSATING, SagaStatus.MANUAL_INTERVENTION_REQUIRED),
    }
)


def require_saga_transition(current: SagaStatus, target: SagaStatus) -> None:
    if (current, target) not in ALLOWED_SAGA_TRANSITIONS:
        raise InvalidStateTransition(
            f"A saga in {current.value} cannot move to {target.value}."
        )

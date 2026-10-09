"""Advance non-terminal sagas. Run next to the API, not inside the confirm request.

    python -m order_service.infrastructure.saga.worker

Confirm commits the saga row at STARTED. This process loads that row and
applies one step. Inventory and ERP calls here return unknown until a later
lookup says the command landed. Simulated payment is local. It is not a
provider, and a refund it records is not guaranteed.

Odoo applies the same command bodies from commerce.commands. This process
does not open odoo_db.
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

from order_service.application.saga.orchestrator import advance
from order_service.application.saga.payment import SimulatedPayment
from order_service.application.saga.results import StepResult, unknown
from order_service.domain.ids import OrderId
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.settings import get_settings
from order_service.observability.metrics import set_payment_circuit_state

logger = logging.getLogger("order_service.saga")


class WaitingInventory:
    """The command is in the outbox. The outcome stays unknown until lookup says otherwise."""

    def lookup_reservation(self, order_id: str) -> StepResult:
        del order_id
        return unknown("odoo-unavailable")

    def reserve(self, command: dict[str, object]) -> StepResult:
        del command
        return unknown("odoo-unavailable")

    def release(self, command: dict[str, object]) -> StepResult:
        del command
        return unknown("odoo-unavailable")


class WaitingErp:
    def lookup_sales_order(self, order_id: str) -> StepResult:
        del order_id
        return unknown("odoo-unavailable")

    def create_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        return unknown("odoo-unavailable")

    def cancel_sales_order(self, command: dict[str, object]) -> StepResult:
        del command
        return unknown("odoo-unavailable")


def advance_one(uow: SqlUnitOfWork, payment: SimulatedPayment, now: datetime) -> bool:
    saga = uow.sagas.next_active()
    if saga is None:
        return False
    order = uow.orders.get(OrderId(saga.order_id))
    if order is None:
        logger.error("saga row has no order saga_id=%s", saga.id)
        return False
    records = advance(
        saga,
        order,
        inventory=WaitingInventory(),
        payment=payment,
        erp=WaitingErp(),
        now=now,
    )
    uow.sagas.add(saga)
    uow.orders.add(order)
    uow.stage_events(order)
    uow.stage_outbox(records)
    set_payment_circuit_state(payment.circuit_gauge)
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = get_settings()
    engine = make_engine(settings)
    sessions = make_session_factory(engine)
    payment = SimulatedPayment()
    pause = getattr(settings, "outbox_poll_interval_seconds", 1.0)
    logger.info("saga worker started")
    while True:
        uow = SqlUnitOfWork(sessions())
        try:
            moved = advance_one(uow, payment, datetime.now(UTC))
            if moved:
                uow.commit()
            else:
                uow.rollback()
        except Exception:
            uow.rollback()
            logger.exception("saga step failed")
        finally:
            uow.close()
        time.sleep(pause)


if __name__ == "__main__":
    main()

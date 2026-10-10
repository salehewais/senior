"""One saga step per call. The caller commits the saga, the order, and the outbox together."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from order_service.application.outbox import PENDING, OutboxRecord
from order_service.application.publishing import command_message
from order_service.application.saga.contract import (
    CANCEL_ERP_ORDER,
    CREATE_ERP_ORDER,
    RELEASE_INVENTORY,
    RESERVE_INVENTORY,
    step_idempotency_key,
)
from order_service.application.saga.ports import ErpPort, InventoryPort, PaymentPort
from order_service.application.saga.results import StepOutcome, StepResult
from order_service.domain.entities.order import Order
from order_service.domain.entities.saga import (
    STEP_CANCEL_ERP,
    STEP_CREATE_ERP,
    STEP_PAYMENT,
    STEP_REFUND,
    STEP_RELEASE,
    STEP_RESERVE,
    SagaInstance,
)
from order_service.domain.entities.saga_status import SagaStatus
from order_service.domain.ids import uuid7


def advance(
    saga: SagaInstance,
    order: Order,
    *,
    inventory: InventoryPort,
    payment: PaymentPort,
    erp: ErpPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    """Move the saga by at most one remote call. Terminal sagas stay where they are."""

    if saga.is_terminal():
        return []
    if saga.status is SagaStatus.STARTED:
        records = _reserve(saga, order, inventory, now, trace_carrier)
    elif saga.status is SagaStatus.INVENTORY_RESERVED:
        records = _pay(saga, order, payment, now)
    elif saga.status is SagaStatus.PAYMENT_CONFIRMED:
        records = _create_erp(saga, order, erp, now, trace_carrier)
    elif saga.status is SagaStatus.ODOO_ORDER_CREATED:
        saga.complete(now)
        records = []
    elif saga.status is SagaStatus.COMPENSATING:
        records = _compensate(saga, order, inventory, payment, erp, now, trace_carrier)
    else:
        records = []
    order.set_saga_status(saga.status.value)
    return records


def _reserve(
    saga: SagaInstance,
    order: Order,
    inventory: InventoryPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    if saga.awaiting(STEP_RESERVE):
        looked = inventory.lookup_reservation(str(order.id.value))
        if looked.outcome is StepOutcome.UNKNOWN:
            return []
        if looked.outcome is StepOutcome.SUCCEEDED:
            saga.reserve_succeeded(looked.reference or str(order.id.value), now)
            return []
        if looked.outcome is StepOutcome.FAILED:
            saga.reserve_failed(looked.reason or "reserve_failed", now)
            return []
        saga.clear_pending(now)
    command = _command(saga, order, RESERVE_INVENTORY, _reserve_payload(order, saga), now, trace_carrier)
    payload = _payload(command)
    result = inventory.reserve(payload)
    _apply_forward(
        saga,
        result,
        now,
        on_success=saga.reserve_succeeded,
        on_failure=saga.reserve_failed,
        step=STEP_RESERVE,
    )
    return [command]


def _pay(
    saga: SagaInstance,
    order: Order,
    payment: PaymentPort,
    now: datetime,
) -> list[OutboxRecord]:
    result = payment.charge(
        order_id=str(order.id.value),
        amount_minor=order.total.amount_minor,
        currency=order.total.currency,
        idempotency_key=step_idempotency_key(str(saga.id), STEP_PAYMENT),
    )
    if result.outcome is StepOutcome.UNKNOWN:
        saga.note_unknown(STEP_PAYMENT, now)
        return []
    if result.outcome is StepOutcome.SUCCEEDED and result.reference:
        order.record_payment_confirmed(
            payment_reference=result.reference,
            now=now,
            correlation_id=saga.correlation_id,
            causation_id=saga.id,
        )
        saga.payment_succeeded(result.reference, now)
        return []
    reason = result.reason or "declined"
    order.record_payment_failed(
        reason_code=_payment_reason(reason),
        now=now,
        correlation_id=saga.correlation_id,
        causation_id=saga.id,
    )
    saga.payment_failed(reason, now)
    return []


def _create_erp(
    saga: SagaInstance,
    order: Order,
    erp: ErpPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    if saga.awaiting(STEP_CREATE_ERP):
        looked = erp.lookup_sales_order(str(order.id.value))
        if looked.outcome is StepOutcome.UNKNOWN:
            return []
        if looked.outcome is StepOutcome.SUCCEEDED:
            saga.erp_succeeded(now)
            return []
        if looked.outcome is StepOutcome.FAILED:
            saga.erp_failed(looked.reason or "erp_create_failed", now)
            return []
        saga.clear_pending(now)
    command = _command(saga, order, CREATE_ERP_ORDER, _erp_payload(order, saga), now, trace_carrier)
    result = erp.create_sales_order(_payload(command))
    _apply_forward(
        saga,
        result,
        now,
        on_success=lambda _reference, moment: saga.erp_succeeded(moment),
        on_failure=saga.erp_failed,
        step=STEP_CREATE_ERP,
    )
    return [command]


def _compensate(
    saga: SagaInstance,
    order: Order,
    inventory: InventoryPort,
    payment: PaymentPort,
    erp: ErpPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    if saga.has_step(STEP_CREATE_ERP) and not saga.has_step(STEP_CANCEL_ERP):
        return _cancel_erp(saga, order, erp, now, trace_carrier)
    if saga.has_step(STEP_PAYMENT) and not saga.has_step(STEP_REFUND):
        return _refund(saga, order, payment, now)
    if saga.has_step(STEP_RESERVE) and not saga.has_step(STEP_RELEASE):
        return _release(saga, order, inventory, now, trace_carrier)
    saga.compensation_finished(now)
    return []


def _release(
    saga: SagaInstance,
    order: Order,
    inventory: InventoryPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    if saga.awaiting(STEP_RELEASE):
        looked = inventory.lookup_reservation(str(order.id.value))
        if looked.outcome is StepOutcome.UNKNOWN:
            return []
        if looked.outcome is StepOutcome.ABSENT:
            saga.compensation_succeeded(STEP_RELEASE, now)
            return []
        if looked.outcome is StepOutcome.FAILED:
            saga.compensation_failed(looked.reason or "release_failed", now)
            return []
        saga.clear_pending(now)
    command = _command(
        saga,
        order,
        RELEASE_INVENTORY,
        {
            "order_id": str(order.id.value),
            "reservation_id": saga.reservation_id,
            "idempotency_key": step_idempotency_key(str(saga.id), STEP_RELEASE),
        },
        now,
        trace_carrier,
    )
    result = inventory.release(_payload(command))
    _apply_compensation(saga, result, STEP_RELEASE, "release_failed", now)
    return [command]


def _refund(
    saga: SagaInstance,
    order: Order,
    payment: PaymentPort,
    now: datetime,
) -> list[OutboxRecord]:
    result = payment.refund(
        order_id=str(order.id.value),
        payment_reference=saga.payment_reference or "",
        idempotency_key=step_idempotency_key(str(saga.id), STEP_REFUND),
    )
    if result.outcome is StepOutcome.UNKNOWN:
        saga.note_unknown(STEP_REFUND, now)
        return []
    if result.outcome is StepOutcome.SUCCEEDED:
        saga.compensation_succeeded(STEP_REFUND, now)
        return []
    saga.compensation_failed(result.reason or "refund_failed", now)
    return []


def _cancel_erp(
    saga: SagaInstance,
    order: Order,
    erp: ErpPort,
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    if saga.awaiting(STEP_CANCEL_ERP):
        looked = erp.lookup_sales_order(str(order.id.value))
        if looked.outcome is StepOutcome.UNKNOWN:
            return []
        if looked.outcome is StepOutcome.ABSENT:
            saga.compensation_succeeded(STEP_CANCEL_ERP, now)
            return []
        if looked.outcome is StepOutcome.FAILED:
            saga.compensation_failed(looked.reason or "cancel_erp_failed", now)
            return []
        saga.clear_pending(now)
    command = _command(
        saga,
        order,
        CANCEL_ERP_ORDER,
        {
            "order_id": str(order.id.value),
            "idempotency_key": step_idempotency_key(str(saga.id), STEP_CANCEL_ERP),
        },
        now,
        trace_carrier,
    )
    result = erp.cancel_sales_order(_payload(command))
    _apply_compensation(saga, result, STEP_CANCEL_ERP, "cancel_erp_failed", now)
    return [command]


def _apply_forward(
    saga: SagaInstance,
    result: StepResult,
    now: datetime,
    *,
    on_success,
    on_failure,
    step: str,
) -> None:
    if result.outcome is StepOutcome.SUCCEEDED:
        on_success(result.reference or str(saga.order_id), now)
        return
    if result.outcome is StepOutcome.FAILED:
        on_failure(result.reason or f"{step}_failed", now)
        return
    saga.note_unknown(step, now)


def _apply_compensation(
    saga: SagaInstance,
    result: StepResult,
    step: str,
    default_reason: str,
    now: datetime,
) -> None:
    if result.outcome is StepOutcome.SUCCEEDED:
        saga.compensation_succeeded(step, now)
        return
    if result.outcome is StepOutcome.FAILED:
        saga.compensation_failed(result.reason or default_reason, now)
        return
    saga.note_unknown(step, now)


def _payment_reason(reason: str) -> str:
    if reason in {"declined", "timeout", "circuit_open", "provider_error"}:
        return reason
    return "provider_error"


def _reserve_payload(order: Order, saga: SagaInstance) -> dict[str, object]:
    return {
        "order_id": str(order.id.value),
        "idempotency_key": step_idempotency_key(str(saga.id), STEP_RESERVE),
        "lines": [
            {
                "product_id": str(item.product_id.value),
                "sku": item.sku,
                "quantity": item.quantity.value,
            }
            for item in order.items
        ],
    }


def _erp_payload(order: Order, saga: SagaInstance) -> dict[str, object]:
    return {
        "order_id": str(order.id.value),
        "customer_id": str(order.customer_id.value),
        "idempotency_key": step_idempotency_key(str(saga.id), STEP_CREATE_ERP),
        "items": [
            {
                "product_id": str(item.product_id.value),
                "sku": item.sku,
                "quantity": item.quantity.value,
                "unit_price": item.unit_price.as_dict(),
            }
            for item in order.items
        ],
        "total": order.total.as_dict(),
    }


def _payload(record: OutboxRecord) -> dict[str, object]:
    body = record.payload.get("payload")
    if not isinstance(body, dict):
        raise TypeError("command envelope has no payload object")
    return body


def _command(
    saga: SagaInstance,
    order: Order,
    event_type: str,
    payload: dict[str, object],
    now: datetime,
    trace_carrier: Mapping[str, str] | None = None,
) -> OutboxRecord:
    message = command_message(
        event_id=uuid7(),
        event_type=event_type,
        occurred_at=now,
        aggregate_id=order.id.value,
        correlation_id=saga.correlation_id,
        causation_id=saga.id,
        payload=payload,
        trace_carrier=trace_carrier,
    )
    return OutboxRecord(
        id=message.event_id,
        event_type=message.event_type,
        aggregate_type="order",
        aggregate_id=order.id.value,
        payload=message.body,
        created_at=now,
        published_at=None,
        retry_count=0,
        status=PENDING,
    )

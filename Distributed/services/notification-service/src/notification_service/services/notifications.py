"""Turn one accepted event into mock email and mock push rows."""

from __future__ import annotations

import uuid

from notification_service.domain.outcomes import (
    REASON_DUPLICATE,
    REASON_HANDLER_FAILED,
    REASON_INVALID_PAYLOAD,
    REASON_RECIPIENT_UNKNOWN,
    ApplyResult,
    Outcome,
    PermanentFailure,
    TransientDeliveryError,
)
from notification_service.domain.protocols import NotificationEvent, Store
from notification_service.domain.records import ListedDelivery
from notification_service.services.channels import MockEmail, MockPush


def list_deliveries(store: Store) -> list[ListedDelivery]:
    with store.transaction():
        return store.list_deliveries()


def apply_notification(
    inspected: NotificationEvent,
    store: Store,
    email: MockEmail,
    push: MockPush,
) -> ApplyResult:
    try:
        with store.transaction():
            if store.seen(inspected.event_id):
                return ApplyResult(Outcome.SUCCESS, REASON_DUPLICATE)
            account_id = _recipient(store, inspected)
            if account_id is None:
                return ApplyResult(Outcome.RETRY, REASON_RECIPIENT_UNKNOWN)
            email.deliver(
                store,
                event_id=inspected.event_id,
                account_id=account_id,
                event_type=inspected.event_type,
            )
            push.deliver(
                store,
                event_id=inspected.event_id,
                account_id=account_id,
                event_type=inspected.event_type,
            )
            store.mark(inspected.event_id, inspected.event_type)
        return ApplyResult(Outcome.SUCCESS)
    except TransientDeliveryError:
        return ApplyResult(Outcome.RETRY, REASON_HANDLER_FAILED)
    except PermanentFailure as exc:
        return ApplyResult(Outcome.PERMANENT, exc.reason)


def _recipient(store: Store, inspected: NotificationEvent) -> uuid.UUID | None:
    payload = inspected.payload
    order_id = _required_uuid(payload.get("order_id"))
    if order_id != inspected.aggregate_id:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    customer = _optional_uuid(payload.get("customer_id"))
    if customer is not None:
        store.remember_contact(order_id, customer)
        return customer
    return store.contact_for(order_id)


def _required_uuid(value: object) -> uuid.UUID:
    parsed = _optional_uuid(value)
    if parsed is None:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    return parsed


def _optional_uuid(value: object) -> uuid.UUID | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise PermanentFailure(REASON_INVALID_PAYLOAD)
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise PermanentFailure(REASON_INVALID_PAYLOAD) from exc

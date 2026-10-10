"""Stage outbox rows from domain events. No broker and no SQLAlchemy.

The unit of work inserts the returned records before it commits. If that
transaction rolls back, the caller rolls these rows back with the business write.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from order_service.application.publishing import RecordsEvents, aggregate_type_for, to_outbound

logger = logging.getLogger("order_service.outbox")

PENDING = "pending"
PUBLISHED = "published"
FAILED = "failed"


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    """One outbox row. ``id`` is the envelope ``event_id``. ``payload`` is the full envelope."""

    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    payload: dict[str, object]
    created_at: datetime
    published_at: datetime | None
    retry_count: int
    status: str


def stage_outbox_records(
    *aggregates: RecordsEvents,
    now: datetime | None = None,
    trace_carrier: Mapping[str, str] | None = None,
) -> list[OutboxRecord]:
    """One pending row per domain event still recorded on these aggregates.

    Clears the aggregates' pending events so a second call does not insert them again.
    ``created_at`` is the insert time inside the business transaction.
    """

    created_at = now or datetime.now(UTC)
    records: list[OutboxRecord] = []
    for aggregate in aggregates:
        for event in aggregate.pending_events():
            envelope = to_outbound(event, trace_carrier).body
            records.append(
                OutboxRecord(
                    id=event.event_id,
                    event_type=event.event_type,
                    aggregate_type=aggregate_type_for(event),
                    aggregate_id=event.aggregate_id,
                    payload=envelope,
                    created_at=created_at,
                    published_at=None,
                    retry_count=0,
                    status=PENDING,
                )
            )
            logger.info(
                "outbox row staged event_id=%s event_type=%s correlation_id=%s status=pending",
                event.event_id,
                event.event_type,
                event.correlation_id,
            )
        aggregate.collect_events()
    return records

"""How one delivery ends. The broker module does not import this decision."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

MAX_AUTOMATIC_RETRIES = 5

HEADER_RETRY_COUNT = "x-retry-count"
HEADER_ORIGINAL_ROUTING_KEY = "x-original-routing-key"
HEADER_FAILURE_REASON = "x-failure-reason"

REASON_MALFORMED = "malformed-envelope"
REASON_UNKNOWN_TYPE = "unknown-event-type"
REASON_UNKNOWN_VERSION = "unknown-schema-version"
REASON_RETRIES_EXHAUSTED = "retries-exhausted"
REASON_DUPLICATE = "duplicate"
REASON_STALE_SNAPSHOT = "stale-snapshot"
REASON_VERSION_GAP = "version-gap"
REASON_HANDLER_FAILED = "handler-failed"
REASON_INVALID_PAYLOAD = "invalid-payload"
REASON_STALE_ORDER_VERSION = "stale-order-version"


class Outcome(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    PERMANENT = "permanent"


@dataclass(frozen=True, slots=True)
class ApplyResult:
    outcome: Outcome
    reason: str = ""


class PermanentFailure(Exception):
    """The body can never be applied. Retrying it would waste the budget."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class VersionGap(Exception):
    """N+1 arrived before N. The caller retries and does not mark the event processed."""

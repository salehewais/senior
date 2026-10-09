"""How one delivery ends. Same header names as the other commerce consumers."""

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
REASON_HANDLER_FAILED = "handler-failed"
REASON_INVALID_PAYLOAD = "invalid-payload"
REASON_RECIPIENT_UNKNOWN = "recipient-unknown"


class Outcome(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    PERMANENT = "permanent"


@dataclass(frozen=True, slots=True)
class ApplyResult:
    outcome: Outcome
    reason: str = ""


class PermanentFailure(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class TransientDeliveryError(Exception):
    """A mock adapter failed in a way that can be retried. Nothing was committed."""

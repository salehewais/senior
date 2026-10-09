"""Outcomes a saga step can observe. Unknown is not failure."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StepOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"
    ABSENT = "absent"


@dataclass(frozen=True, slots=True)
class StepResult:
    outcome: StepOutcome
    reference: str | None = None
    reason: str = ""


def succeeded(reference: str | None = None) -> StepResult:
    return StepResult(StepOutcome.SUCCEEDED, reference=reference)


def failed(reason: str) -> StepResult:
    return StepResult(StepOutcome.FAILED, reason=reason)


def unknown(reason: str = "timeout") -> StepResult:
    return StepResult(StepOutcome.UNKNOWN, reason=reason)


def absent() -> StepResult:
    return StepResult(StepOutcome.ABSENT)

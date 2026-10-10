"""Simulated payment inside the order service.

This is not a payment provider and not a separate service. A refund that
returns succeeded is recorded locally. It is not a guaranteed refund.
The port it implements lives in application.saga.ports.
"""

from __future__ import annotations

from order_service.application.saga.results import StepResult, failed, succeeded, unknown

CHARGE_SUCCEED = "succeed"
CHARGE_DECLINE = "decline"
CHARGE_TIMEOUT = "timeout"
CHARGE_CIRCUIT = "circuit_open"
REFUND_SUCCEED = "succeed"
REFUND_FAIL = "fail"

CLOSED = "closed"
HALF_OPEN = "half_open"
OPEN = "open"


class SimulatedPayment:
    def __init__(
        self,
        *,
        charge: str = CHARGE_SUCCEED,
        refund: str = REFUND_SUCCEED,
        failure_threshold: int = 3,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure threshold must be at least 1")
        self._charge = charge
        self._refund = refund
        self._threshold = failure_threshold
        self._results: dict[str, StepResult] = {}
        self._consecutive_failures = 0
        self.state = CLOSED
        self.charge_calls = 0
        self.refund_calls = 0

    @property
    def circuit_gauge(self) -> float:
        if self.state == OPEN:
            return 2.0
        if self.state == HALF_OPEN:
            return 1.0
        return 0.0

    def charge(
        self,
        *,
        order_id: str,
        amount_minor: int,
        currency: str,
        idempotency_key: str,
    ) -> StepResult:
        del order_id, amount_minor, currency
        self.charge_calls += 1
        stored = self._results.get(idempotency_key)
        if stored is not None:
            return stored
        if self.state == OPEN:
            result = failed("circuit_open")
            self._results[idempotency_key] = result
            return result
        result = self._charge_once()
        self._results[idempotency_key] = result
        return result

    def refund(
        self,
        *,
        order_id: str,
        payment_reference: str,
        idempotency_key: str,
    ) -> StepResult:
        del order_id, payment_reference
        self.refund_calls += 1
        stored = self._results.get(idempotency_key)
        if stored is not None:
            return stored
        if self._refund == REFUND_FAIL:
            result = failed("refund_failed")
        else:
            result = succeeded(f"refund-{idempotency_key}")
        self._results[idempotency_key] = result
        return result

    def _charge_once(self) -> StepResult:
        if self._charge == CHARGE_TIMEOUT:
            return unknown("timeout")
        if self._charge == CHARGE_DECLINE:
            self._record_failure()
            return failed("declined")
        if self._charge == CHARGE_CIRCUIT:
            self._record_failure()
            return failed("circuit_open")
        self._consecutive_failures = 0
        self.state = CLOSED
        return succeeded(f"sim-{self.charge_calls}")

    def _record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._threshold:
            self.state = OPEN

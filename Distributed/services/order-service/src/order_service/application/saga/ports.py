"""Ports the orchestrator calls. Infrastructure and tests supply the adapters."""

from __future__ import annotations

from typing import Protocol

from order_service.application.saga.results import StepResult


class InventoryPort(Protocol):
    def lookup_reservation(self, order_id: str) -> StepResult:
        """Read the reservation. A timeout is unknown, not absent."""

    def reserve(self, command: dict[str, object]) -> StepResult: ...

    def release(self, command: dict[str, object]) -> StepResult: ...


class PaymentPort(Protocol):
    def charge(
        self,
        *,
        order_id: str,
        amount_minor: int,
        currency: str,
        idempotency_key: str,
    ) -> StepResult: ...

    def refund(
        self,
        *,
        order_id: str,
        payment_reference: str,
        idempotency_key: str,
    ) -> StepResult:
        """A succeeded refund is simulated. It is not a guaranteed movement of money."""


class ErpPort(Protocol):
    def lookup_sales_order(self, order_id: str) -> StepResult: ...

    def create_sales_order(self, command: dict[str, object]) -> StepResult: ...

    def cancel_sales_order(self, command: dict[str, object]) -> StepResult: ...

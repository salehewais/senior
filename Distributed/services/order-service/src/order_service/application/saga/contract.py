"""Command contract shared with the Odoo consumer.

Routing keys match docs/rabbitmq.md. The Odoo parser accepts these event
types and payload fields. Reporting does not bind to this exchange.
"""

from __future__ import annotations

EXCHANGE_COMMERCE_COMMANDS = "commerce.commands"

RESERVE_INVENTORY = "ReserveInventory"
RELEASE_INVENTORY = "ReleaseInventory"
CREATE_ERP_ORDER = "CreateErpOrder"
CANCEL_ERP_ORDER = "CancelErpOrder"

COMMAND_ROUTING_KEYS: dict[str, str] = {
    RESERVE_INVENTORY: "inventory.reserve",
    RELEASE_INVENTORY: "inventory.release",
    CREATE_ERP_ORDER: "erp.create-sales-order",
    CANCEL_ERP_ORDER: "erp.cancel-sales-order",
}

COMMAND_EVENT_TYPES: frozenset[str] = frozenset(COMMAND_ROUTING_KEYS)


def step_idempotency_key(saga_id: str, step: str) -> str:
    """Stable key for one saga step. Retries reuse it. A new saga does not."""

    return f"{saga_id}:{step}"

"""Reservations and saga commands. Same odoo_db transaction as the caller."""

from odoo import fields

from commerce_erp.domain import commands as _commands

from .order_store import _OdooStore


class _OdooCommandStore:
    """Reservations and sales orders for saga commands. Same odoo_db transaction as the caller."""

    def __init__(self, env):
        self.env = env
        self._orders = _OdooStore(env)

    def has_event(self, event_id: str) -> bool:
        return bool(self.env["commerce.processed.event"].search_count([("event_id", "=", event_id)]))

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None:
        self.env["commerce.processed.event"].create(
            {
                "event_id": event_id,
                "event_type": event_type,
                "aggregate_id": aggregate_id,
                "processed_at": fields.Datetime.now(),
                "consumer_name": "odoo-commands",
            }
        )

    def result_for_key(self, idempotency_key: str):
        row = self.env["commerce.reservation"].search([("idempotency_key", "=", idempotency_key)], limit=1)
        if not row:
            sale = self.env["sale.order"].search([("commerce_idempotency_key", "=", idempotency_key)], limit=1)
            if not sale:
                return None
            return _commands.CommandResult("succeeded", "idempotency_key", sale.commerce_order_id or "")
        return _commands.CommandResult("succeeded", "idempotency_key", row.reservation_id or "")

    def remember_key(self, idempotency_key: str, result) -> None:
        if not result.reference:
            return
        reservation = self.env["commerce.reservation"].search([("reservation_id", "=", result.reference)], limit=1)
        if reservation and not reservation.idempotency_key:
            reservation.idempotency_key = idempotency_key
        sale = self.env["sale.order"].search([("commerce_order_id", "=", result.reference)], limit=1)
        if sale and not sale.commerce_idempotency_key:
            sale.commerce_idempotency_key = idempotency_key

    def find_reservation(self, order_id: str):
        row = self.env["commerce.reservation"].search([("order_id", "=", order_id)], limit=1)
        if not row:
            return None
        return row.reservation_id, row.state == "released"

    def save_reservation(self, order_id: str, reservation_id: str, *, released: bool) -> None:
        row = self.env["commerce.reservation"].search([("order_id", "=", order_id)], limit=1)
        values = {
            "order_id": order_id,
            "reservation_id": reservation_id,
            "state": "released" if released else "reserved",
        }
        if row:
            row.write(values)
            return
        self.env["commerce.reservation"].create(values)

    def has_order(self, order_id: str) -> bool:
        return self._orders.has_order(order_id)

    def create_sales_order(self, order) -> None:
        self._orders.create_sales_order(order)

    def cancel_sales_order(self, order_id: str) -> bool:
        sale = self.env["sale.order"].search([("commerce_order_id", "=", order_id)], limit=1)
        if not sale or sale.state == "cancel":
            return False
        sale.with_context(tracking_disable=True, mail_notrack=True).action_cancel()
        return True

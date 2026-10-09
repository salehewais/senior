"""Apply OrderConfirmed inside one odoo_db transaction.

The worker calls this method over XML-RPC. The processed-event row and the
sales order commit together when the RPC returns. The worker acks after that.
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError

from .bootstrap import import_commerce_erp

_logger = logging.getLogger(__name__)
_erp = import_commerce_erp()


class _OdooStore:
    def __init__(self, env):
        self.env = env

    def has_event(self, event_id: str) -> bool:
        return bool(self.env["commerce.processed.event"].search_count([("event_id", "=", event_id)]))

    def has_order(self, order_id: str) -> bool:
        return bool(self.env["sale.order"].search_count([("commerce_order_id", "=", order_id)]))

    def remember_event(self, event_id: str, event_type: str, aggregate_id: str) -> None:
        self.env["commerce.processed.event"].create(
            {
                "event_id": event_id,
                "event_type": event_type,
                "aggregate_id": aggregate_id,
                "processed_at": fields.Datetime.now(),
                "consumer_name": "odoo-order-confirmed",
            }
        )

    def create_sales_order(self, order) -> None:
        partner = self._partner(order.customer_id)
        commands = []
        for line in order.lines:
            product = self._product(line)
            commands.append(
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "name": line.sku,
                        "product_uom_qty": line.quantity,
                        "product_uom": product.uom_id.id,
                        "price_unit": line.amount_minor / 100.0,
                        "commerce_unit_amount_minor": line.amount_minor,
                        "commerce_currency": line.currency,
                    },
                )
            )
        sale = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "commerce_order_id": order.order_id,
                "client_order_ref": order.order_id,
                "order_line": commands,
            }
        )
        sale.with_context(
            commerce_correlation_id=order.correlation_id,
            commerce_causation_id=order.event_id,
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_notrack=True,
        ).action_confirm()

    def _partner(self, customer_id: str):
        Partner = self.env["res.partner"]
        partner = Partner.search([("commerce_customer_id", "=", customer_id)], limit=1)
        if partner:
            return partner
        partner = Partner.create(_erp.confirmed.partner_values(customer_id))
        self._xmlid(partner, _erp.confirmed.xmlid_for_customer(customer_id))
        return partner

    def _product(self, line):
        Product = self.env["product.product"]
        product = Product.search([("default_code", "=", line.sku)], limit=1)
        if not product:
            product = Product.search([("commerce_product_id", "=", line.product_id)], limit=1)
        if product:
            if not product.commerce_product_id:
                product.commerce_product_id = line.product_id
            elif product.commerce_product_id != line.product_id:
                _logger.warning(
                    "sku already mapped; keeping the first commerce product id sku=%s",
                    line.sku,
                )
            return product
        product = Product.create(_erp.confirmed.product_values(line))
        self._xmlid(product, _erp.confirmed.xmlid_for_sku(line.sku))
        return product

    def _xmlid(self, record, name: str) -> None:
        external = self.env["ir.model.data"].search(
            [("module", "=", "commerce_connector"), ("name", "=", name)],
            limit=1,
        )
        if external:
            return
        self.env["ir.model.data"].create(
            {
                "module": "commerce_connector",
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "noupdate": True,
            }
        )


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
            return _erp.commands.CommandResult("succeeded", "idempotency_key", sale.commerce_order_id or "")
        return _erp.commands.CommandResult("succeeded", "idempotency_key", row.reservation_id or "")

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


class CommerceConnector(models.Model):
    _name = "commerce.connector"
    _description = "Apply OrderConfirmed through the Odoo ORM"

    name = fields.Char()

    @api.model
    def apply_order_confirmed(self, envelope):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError("Only the ERP service user can apply OrderConfirmed.")
        result = _erp.confirmed.apply_confirmed_order(_OdooStore(self.env), envelope)
        event_id = envelope.get("event_id") if isinstance(envelope, dict) else None
        _logger.info(
            "apply_order_confirmed outcome=%s reason=%s event_id=%s",
            result.outcome,
            result.reason,
            event_id,
        )
        return result.as_dict()

    @api.model
    def apply_command(self, envelope):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError("Only the ERP service user can apply a saga command.")
        result = _erp.commands.apply_command(_OdooCommandStore(self.env), envelope)
        event_id = envelope.get("event_id") if isinstance(envelope, dict) else None
        _logger.info(
            "apply_command outcome=%s reason=%s event_id=%s",
            result.outcome,
            result.reason,
            event_id,
        )
        return result.as_dict()

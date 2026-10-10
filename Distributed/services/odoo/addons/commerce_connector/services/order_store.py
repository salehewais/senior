"""Apply a confirmed order inside the Odoo ORM. This store does not open RabbitMQ."""

import logging

from odoo import fields

from commerce_erp.domain import confirmed as _confirmed

_logger = logging.getLogger(__name__)


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
        partner = Partner.create(_confirmed.partner_values(customer_id))
        self._xmlid(partner, _confirmed.xmlid_for_customer(customer_id))
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
        product = Product.create(_confirmed.product_values(line))
        self._xmlid(product, _confirmed.xmlid_for_sku(line.sku))
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

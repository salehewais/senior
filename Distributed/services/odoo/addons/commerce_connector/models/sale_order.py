"""Fulfillment buttons. Each click is one HTTP call to the order service.

A 409 is shown to the user. The button does not try the next milestone and
does not publish an order-status event. The order service publishes the fact
after its domain accepts the transition.
"""

import os

from odoo import fields, models
from odoo.exceptions import UserError

from .bootstrap import import_commerce_erp

_erp = import_commerce_erp()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commerce_order_id = fields.Char(
        string="Commerce order id",
        copy=False,
        index=True,
        readonly=True,
    )
    commerce_idempotency_key = fields.Char(string="Saga idempotency key", copy=False, index=True)
    commerce_tracking_reference = fields.Char(string="Tracking reference")

    _sql_constraints = [
        (
            "commerce_order_id_unique",
            "unique(commerce_order_id)",
            "This commerce order already has a sales order.",
        ),
    ]

    def action_commerce_processing(self):
        self._commerce_milestone("processing")

    def action_commerce_shipped(self):
        self._commerce_milestone("shipped")

    def action_commerce_delivered(self):
        self._commerce_milestone("delivered")

    def _commerce_milestone(self, milestone: str) -> None:
        token = os.environ.get("INTERNAL_SERVICE_TOKEN", "")
        base_url = os.environ.get("ORDER_SERVICE_URL", "http://127.0.0.1:8000")
        timeout = float(os.environ.get("ORDER_SERVICE_TIMEOUT_SECONDS", "5"))
        for order in self:
            if not order.commerce_order_id:
                raise UserError("This sales order has no commerce order id.")
            try:
                result = _erp.fulfillment.post_milestone(
                    order_service_url=base_url,
                    token=token,
                    order_id=order.commerce_order_id,
                    milestone=milestone,
                    tracking_reference=order.commerce_tracking_reference or None,
                    timeout=timeout,
                )
            except _erp.fulfillment.MissingToken as exc:
                raise UserError(
                    "INTERNAL_SERVICE_TOKEN is unset. The order service was not called."
                ) from exc
            if result.result is _erp.fulfillment.MilestoneResult.ACCEPTED:
                continue
            if result.result is _erp.fulfillment.MilestoneResult.NOT_READY:
                raise UserError(
                    "The previous milestone is not applied yet. Retry this button later. "
                    "The order service did not skip a step."
                )
            raise UserError(
                "The order service did not accept the milestone "
                f"(HTTP {result.http_status}). It was not retried."
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commerce_unit_amount_minor = fields.Integer(
        string="Unit price minor units",
        readonly=True,
        help="Integer minor units from OrderConfirmed. price_unit is that amount divided by 100 for the Odoo UI.",
    )
    commerce_currency = fields.Char(string="Commerce currency", readonly=True)

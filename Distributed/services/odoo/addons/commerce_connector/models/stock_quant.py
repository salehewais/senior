"""Schedule one inventory snapshot per product when stock changes.

The schedule is a set of product ids on the cursor. The precommit hook reads
the quants after Odoo has flushed them and inserts the outbox row before
COMMIT. A second sales order is not involved. This does not publish.
"""

from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def write(self, vals):
        result = super().write(vals)
        if {"quantity", "reserved_quantity", "inventory_quantity"} & set(vals):
            self._commerce_schedule(self.product_id)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._commerce_schedule(records.product_id)
        return records

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity=False,
        reserved_quantity=False,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        result = super()._update_available_quantity(
            product_id,
            location_id,
            quantity=quantity,
            reserved_quantity=reserved_quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
        )
        self._commerce_schedule(product_id)
        return result

    @api.model
    def _update_reserved_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        result = super()._update_reserved_quantity(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        self._commerce_schedule(product_id)
        return result

    def _commerce_schedule(self, products):
        if not products:
            return
        product_ids = set(products.ids)
        if not product_ids:
            return
        cursor = self.env.cr
        pending = getattr(cursor, "commerce_snapshot_product_ids", None)
        if pending is None:
            pending = set()
            cursor.commerce_snapshot_product_ids = pending
            cursor.commerce_snapshot_context = {
                "correlation_id": self.env.context.get("commerce_correlation_id"),
                "causation_id": self.env.context.get("commerce_causation_id"),
            }

            def _flush():
                scheduled = set(cursor.commerce_snapshot_product_ids or ())
                cursor.commerce_snapshot_product_ids = set()
                context = cursor.commerce_snapshot_context or {}
                if not scheduled:
                    return
                self.env["commerce.inventory.state"].enqueue_products(
                    self.env["product.product"].browse(list(scheduled)),
                    correlation_id=context.get("correlation_id"),
                    causation_id=context.get("causation_id"),
                )

            cursor.precommit.add(_flush)
        pending.update(product_ids)

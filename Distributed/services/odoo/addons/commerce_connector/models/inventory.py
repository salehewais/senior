"""Latest stock snapshot and the inventory outbox row, one transaction.

enqueue_products runs from the cursor precommit hook. Odoo flushes the quant
writes, then runs that hook, then commits. The outbox insert is in that same
transaction. Nothing publishes to RabbitMQ here.
"""

import logging
from datetime import UTC, datetime

from odoo import api, fields, models
from psycopg2.extras import Json

from .bootstrap import import_commerce_erp

_logger = logging.getLogger(__name__)
_erp = import_commerce_erp()


class CommerceInventoryState(models.Model):
    _name = "commerce.inventory.state"
    _description = "Latest commerce stock snapshot"
    _rec_name = "sku"
    _order = "sku, id"

    product_id = fields.Many2one("product.product", required=True, ondelete="cascade", index=True)
    commerce_product_id = fields.Char(required=True, index=True)
    sku = fields.Char(required=True)
    warehouse_code = fields.Char(required=True)
    on_hand = fields.Integer(required=True)
    reserved = fields.Integer(required=True)
    version = fields.Integer(required=True)

    _sql_constraints = [
        ("product_unique", "unique(product_id)", "One snapshot row per product."),
        (
            "commerce_product_unique",
            "unique(commerce_product_id)",
            "One snapshot row per commerce product.",
        ),
    ]

    def init(self):
        for statement in _erp.inventory.OUTBOX_STATEMENTS:
            self.env.cr.execute(statement)

    @api.model
    def enqueue_products(self, products, correlation_id=None, causation_id=None):
        warehouse = self.env["stock.warehouse"].search([], limit=1, order="id")
        warehouse_code = warehouse.code if warehouse and warehouse.code else "WH"
        for product in products:
            commerce_product_id = product.commerce_product_id
            sku = product.default_code
            if not commerce_product_id or not sku:
                continue
            product.invalidate_recordset(["qty_available", "free_qty"])
            on_hand = _erp.inventory.quantity_for_catalog(product.qty_available)
            free = _erp.inventory.quantity_for_catalog(product.free_qty)
            reserved = on_hand - free if on_hand > free else 0
            state = self.search([("product_id", "=", product.id)], limit=1)
            version = 1 if not state else state.version + 1
            values = {
                "product_id": product.id,
                "commerce_product_id": commerce_product_id,
                "sku": sku,
                "warehouse_code": warehouse_code,
                "on_hand": on_hand,
                "reserved": reserved,
                "version": version,
            }
            if state:
                state.write(values)
            else:
                self.create(values)
            envelope = _erp.inventory.build_inventory_updated(
                product_id=commerce_product_id,
                sku=sku,
                on_hand=on_hand,
                reserved=reserved,
                warehouse_code=warehouse_code,
                aggregate_version=version,
                correlation_id=correlation_id,
                causation_id=causation_id,
            )
            self.env.cr.execute(
                """
                INSERT INTO commerce_event_outbox
                    (id, event_type, aggregate_type, aggregate_id, payload,
                     created_at, published_at, retry_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, NULL, 0, 'pending')
                """,
                (
                    envelope["event_id"],
                    envelope["event_type"],
                    _erp.inventory.AGGREGATE_TYPE,
                    envelope["aggregate_id"],
                    Json(envelope),
                    datetime.now(UTC),
                ),
            )
            _logger.info(
                "inventory outbox staged event_id=%s aggregate_id=%s aggregate_version=%s",
                envelope["event_id"],
                envelope["aggregate_id"],
                version,
            )

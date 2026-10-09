from odoo import fields, models


class CommerceProcessedEvent(models.Model):
    _name = "commerce.processed.event"
    _description = "OrderConfirmed deliveries already applied"
    _rec_name = "event_id"
    _order = "processed_at desc, id desc"

    event_id = fields.Char(required=True, index=True)
    event_type = fields.Char(required=True)
    aggregate_id = fields.Char(required=True, index=True)
    processed_at = fields.Datetime(required=True)
    consumer_name = fields.Char(required=True, default="odoo-order-confirmed")

    _sql_constraints = [
        (
            "event_id_unique",
            "unique(event_id)",
            "This event_id was already applied.",
        ),
    ]

"""One reservation row per commerce order. Odoo is the stock authority for this hold."""

from odoo import fields, models


class CommerceReservation(models.Model):
    _name = "commerce.reservation"
    _description = "Idempotent inventory reservation for one commerce order"

    order_id = fields.Char(required=True, index=True)
    reservation_id = fields.Char(required=True)
    idempotency_key = fields.Char(index=True)
    state = fields.Selection(
        [("reserved", "Reserved"), ("released", "Released")],
        required=True,
        default="reserved",
    )

    _sql_constraints = [
        (
            "order_id_unique",
            "unique(order_id)",
            "This commerce order already has a reservation row.",
        ),
    ]

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commerce_customer_id = fields.Char(
        string="Commerce customer id",
        copy=False,
        index=True,
        help="Stable external id from OrderConfirmed. Password hashes are not stored.",
    )

    _sql_constraints = [
        (
            "commerce_customer_id_unique",
            "unique(commerce_customer_id)",
            "This commerce customer already has a partner.",
        ),
    ]

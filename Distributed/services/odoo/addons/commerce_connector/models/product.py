from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    commerce_product_id = fields.Char(
        string="Commerce product id",
        copy=False,
        index=True,
        help="Catalog product id from the first OrderConfirmed line for this SKU.",
    )

    _sql_constraints = [
        (
            "commerce_product_id_unique",
            "unique(commerce_product_id)",
            "This commerce product already exists.",
        ),
    ]

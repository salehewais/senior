from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    athir_financial_tolerance = fields.Float(
        related='company_id.athir_financial_tolerance',
        readonly=False,
    )
    athir_allow_company_fallback = fields.Boolean(
        related='company_id.athir_allow_company_fallback',
        readonly=False,
    )
    athir_store_raw_payload = fields.Boolean(
        related='company_id.athir_store_raw_payload',
        readonly=False,
    )
    athir_auto_post = fields.Boolean(
        related='company_id.athir_auto_post',
        readonly=False,
    )
    athir_register_payments = fields.Boolean(
        related='company_id.athir_register_payments',
        readonly=False,
    )

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    athir_financial_tolerance = fields.Float(
        string='Athir Financial Tolerance',
        default=0.01,
        help='Absolute amount tolerance when comparing Athir totals to Odoo computed totals.',
    )
    athir_allow_company_fallback = fields.Boolean(
        string='Athir Allow Default Company Fallback',
        default=False,
        help='When enabled and organization mapping is missing, use the credential/company '
             'context company. Disabled by default — unresolved organization is rejected.',
    )
    athir_store_raw_payload = fields.Boolean(
        string='Store Athir Raw Payloads',
        default=False,
        help='Off by default. Raw payloads may contain patient data.',
    )
    # Future hooks — unused in v1 code paths.
    athir_auto_post = fields.Boolean(
        string='Athir Auto-Post Invoices',
        default=False,
        help='Reserved for future use. v1 always creates draft invoices.',
    )
    athir_register_payments = fields.Boolean(
        string='Athir Register Payments',
        default=False,
        help='Reserved for future use. v1 only stores payment traces.',
    )

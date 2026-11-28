from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    athir_mrn = fields.Char(
        string='Athir MRN',
        index=True,
        copy=False,
        help='Medical Record Number used to resolve B2C Athir customers.',
    )
    athir_insurance_company_id = fields.Char(
        string='Athir Insurance Company ID',
        index=True,
        copy=False,
        help='External insurance company id for B2B Athir customers.',
    )

    _athir_mrn_uniq = models.Constraint(
        'UNIQUE(athir_mrn)',
        'Athir MRN must be unique.',
    )
    _athir_insurance_uniq = models.Constraint(
        'UNIQUE(athir_insurance_company_id)',
        'Athir insurance company id must be unique.',
    )

from odoo import api, fields, models
from odoo.exceptions import ValidationError


ENTITY_TYPES = [
    ('customer', 'Customer'),
    ('product', 'Product'),
    ('tax', 'Tax'),
    ('payment_method', 'Payment Method'),
    ('company', 'Company'),
    ('branch', 'Branch'),
    ('clinic', 'Clinic'),
    ('doctor', 'Doctor'),
    ('cashier', 'Cashier'),
    ('service_group', 'Service Group'),
]


class AthirExternalMapping(models.Model):
    _name = 'athir.external.mapping'
    _description = 'Athir External Mapping'
    _order = 'entity_type, external_id'

    name = fields.Char(compute='_compute_name', store=True)
    source_system = fields.Char(required=True, default='athir', index=True)
    entity_type = fields.Selection(ENTITY_TYPES, required=True, index=True)
    external_id = fields.Char(required=True, index=True)
    external_name = fields.Char()
    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    company_id = fields.Many2one('res.company', index=True, ondelete='cascade')
    active = fields.Boolean(default=True)
    note = fields.Text()

    _mapping_uniq = models.Constraint(
        'UNIQUE(source_system, entity_type, external_id, company_id)',
        'External mapping must be unique per system, entity, id, and company.',
    )

    @api.depends('entity_type', 'external_id', 'external_name')
    def _compute_name(self):
        for rec in self:
            label = rec.external_name or rec.external_id or ''
            rec.name = '%s: %s' % (rec.entity_type or '?', label)

    @api.constrains('res_model', 'res_id')
    def _check_target_exists(self):
        for rec in self:
            if not rec.res_model or not rec.res_id:
                raise ValidationError('Mapped record model and id are required.')
            if rec.res_model not in self.env:
                raise ValidationError('Unknown model: %s' % rec.res_model)
            target = self.env[rec.res_model].browse(rec.res_id).exists()
            if not target:
                raise ValidationError(
                    'Mapped record %s,%s does not exist.' % (rec.res_model, rec.res_id)
                )

    def get_record(self):
        self.ensure_one()
        return self.env[self.res_model].browse(self.res_id).exists()

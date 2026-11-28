from odoo import fields, models


class AthirIntegrationLog(models.Model):
    _name = 'athir.integration.log'
    _description = 'Athir Integration Log'
    _order = 'create_date desc'

    name = fields.Char(required=True, default='/')
    operation = fields.Selection(
        [('invoice', 'Invoice'), ('refund', 'Refund')],
        required=True,
    )
    status = fields.Selection(
        [
            ('received', 'Received'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('duplicate', 'Duplicate'),
            ('rejected', 'Rejected'),
        ],
        required=True,
        default='received',
        index=True,
    )
    external_id = fields.Char(index=True)
    correlation_id = fields.Char(index=True)
    payload_hash = fields.Char()
    error_code = fields.Char()
    error_message = fields.Text()
    company_id = fields.Many2one('res.company', ondelete='set null')
    move_id = fields.Many2one('account.move', ondelete='set null')
    credential_id = fields.Many2one('athir.api.credential', ondelete='set null')
    raw_payload = fields.Text(
        groups='bh_athir_integration.group_athir_manager',
        help='Stored only when company setting store_raw_payload is enabled.',
    )

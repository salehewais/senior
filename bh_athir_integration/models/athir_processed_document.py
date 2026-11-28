from odoo import api, fields, models


class AthirProcessedDocument(models.Model):
    _name = 'athir.processed.document'
    _description = 'Athir Processed Document (Idempotency)'
    _order = 'create_date desc'

    source_system = fields.Char(required=True, default='athir', index=True)
    operation = fields.Selection(
        [('invoice', 'Invoice'), ('refund', 'Refund')],
        required=True,
        index=True,
    )
    external_id = fields.Char(required=True, index=True)
    payload_hash = fields.Char(required=True)
    status = fields.Selection(
        [('succeeded', 'Succeeded'), ('failed', 'Failed')],
        required=True,
        index=True,
    )
    odoo_move_id = fields.Many2one('account.move', ondelete='set null')
    error_code = fields.Char()
    error_message = fields.Text()
    company_id = fields.Many2one('res.company', ondelete='set null')

    _external_operation_uniq = models.Constraint(
        'UNIQUE(source_system, operation, external_id)',
        'This Athir document was already processed.',
    )

    @api.model
    def _advisory_lock(self, source_system, operation, external_id):
        token = 'athir.processed:%s:%s:%s' % (source_system, operation, external_id)
        self.env.cr.execute(
            'SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))',
            (token,),
        )

    @api.model
    def begin_or_replay(self, source_system, operation, external_id, payload_hash):
        """Lock and inspect prior processing.

        Returns dict:
          - action: 'proceed' | 'replay' | 'conflict'
          - document: existing record or empty
          - move: account.move when replaying
        """
        self._advisory_lock(source_system, operation, external_id)
        existing = self.sudo().search([
            ('source_system', '=', source_system),
            ('operation', '=', operation),
            ('external_id', '=', external_id),
        ], limit=1)
        if not existing:
            return {'action': 'proceed', 'document': existing, 'move': False}
        if existing.status == 'succeeded':
            if existing.payload_hash == payload_hash:
                return {
                    'action': 'replay',
                    'document': existing,
                    'move': existing.odoo_move_id,
                }
            return {'action': 'conflict', 'document': existing, 'move': False}
        # Previous failure: allow retry.
        return {'action': 'proceed', 'document': existing, 'move': False}

    @api.model
    def mark_result(
        self,
        source_system,
        operation,
        external_id,
        payload_hash,
        status,
        move=None,
        error_code=None,
        error_message=None,
        company=None,
        existing=None,
    ):
        vals = {
            'source_system': source_system,
            'operation': operation,
            'external_id': external_id,
            'payload_hash': payload_hash,
            'status': status,
            'odoo_move_id': move.id if move else False,
            'error_code': error_code or False,
            'error_message': error_message or False,
            'company_id': company.id if company else False,
        }
        if existing:
            existing.sudo().write(vals)
            return existing
        return self.sudo().create(vals)

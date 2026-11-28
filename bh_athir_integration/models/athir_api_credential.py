import hashlib
import hmac
import secrets

from odoo import api, fields, models


class AthirApiCredential(models.Model):
    _name = 'athir.api.credential'
    _description = 'Athir API Credential'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company Scope',
        help='Optional. When set, writes run in this company context.',
    )
    token_hash = fields.Char(
        copy=False,
        groups='bh_athir_integration.group_athir_manager',
    )
    has_token = fields.Boolean(compute='_compute_has_token')
    revoked = fields.Boolean(default=False)
    last_used_at = fields.Datetime(readonly=True)
    note = fields.Text()

    @api.depends('token_hash')
    def _compute_has_token(self):
        for rec in self:
            rec.has_token = bool(rec.token_hash)

    @api.model
    def _hash_token(self, token):
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def action_generate_token(self):
        self.ensure_one()
        token = secrets.token_urlsafe(32)
        self.sudo().write({
            'token_hash': self._hash_token(token),
            'revoked': False,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Athir API Token Generated',
                'message': (
                    'Copy this token now; it will not be shown again:\n%s' % token
                ),
                'type': 'warning',
                'sticky': True,
            },
        }

    def action_revoke(self):
        self.write({'revoked': True})

    @api.model
    def authenticate_token(self, token):
        """Validate token via constant-time hash compare. Returns 0..1 credential."""
        if not token:
            return self.browse()
        token_hash = self._hash_token(token)
        candidates = self.sudo().search([
            ('active', '=', True),
            ('revoked', '=', False),
            ('token_hash', '!=', False),
        ])
        for cred in candidates:
            if hmac.compare_digest(cred.token_hash or '', token_hash):
                cred.sudo().write({'last_used_at': fields.Datetime.now()})
                return cred
        return self.browse()

    @api.model
    def extract_token_from_headers(self, headers):
        auth = headers.get('Authorization') or headers.get('authorization') or ''
        if auth.lower().startswith('bearer '):
            return auth[7:].strip()
        api_key = headers.get('X-API-Key') or headers.get('x-api-key')
        if api_key:
            return api_key.strip()
        return None

    def get_env_for_writes(self, base_env):
        """Return a superuser env, optionally company-scoped (Odoo 19: no env.sudo())."""
        self.ensure_one()
        env = base_env(su=True)
        if self.company_id:
            env = env['res.company'].with_company(self.company_id).env
        return env

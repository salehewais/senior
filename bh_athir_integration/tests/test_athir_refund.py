import json

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.bh_athir_integration.application.integration_facade import (
    IntegrationFacade,
)
from odoo.addons.bh_athir_integration.domain.exceptions import UnsupportedContractError
from odoo.addons.bh_athir_integration.tests.common import AthirIntegrationCommon


@tagged('post_install', '-at_install')
class TestAthirRefund(AthirIntegrationCommon):

    def test_refund_strategy_unsupported(self):
        with self.assertRaises(UnsupportedContractError) as ctx:
            IntegrationFacade(self.env(su=True)).process(
                'refund',
                {'invoice_id': 'ATH-INV-1001'},
                credential=self.credential,
            )
        self.assertEqual(ctx.exception.code, 'UNSUPPORTED_CONTRACT')
        self.assertFalse(self.env['account.move'].search([
            ('move_type', '=', 'out_refund'),
            ('ref', '=', 'ATH-INV-1001'),
        ]))


@tagged('post_install', '-at_install')
class TestAthirRefundHttp(HttpCase):

    def test_refund_endpoint_returns_unsupported(self):
        company = self.env.company
        credential = self.env['athir.api.credential'].sudo().create({
            'name': 'HTTP Refund Cred',
            'company_id': company.id,
        })
        token = 'refund-test-token-value'
        credential.sudo().write({
            'token_hash': self.env['athir.api.credential']._hash_token(token),
        })
        response = self.url_open(
            '/api/athir/v1/refunds',
            data=json.dumps({'invoice_id': 'X'}),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % token,
            },
            method='POST',
        )
        self.assertEqual(response.status_code, 501)
        body = response.json()
        self.assertEqual(body['error']['code'], 'UNSUPPORTED_CONTRACT')
        self.assertFalse(self.env['athir.processed.document'].sudo().search([
            ('operation', '=', 'refund'),
            ('status', '=', 'succeeded'),
        ]))

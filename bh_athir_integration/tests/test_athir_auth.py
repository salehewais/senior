import json

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.bh_athir_integration.tests.common import AthirIntegrationCommon


@tagged('post_install', '-at_install')
class TestAthirAuth(AthirIntegrationCommon):

    def test_authenticate_valid_token(self):
        cred = self.env['athir.api.credential'].authenticate_token(self.api_token)
        self.assertEqual(cred, self.credential)

    def test_authenticate_missing_token(self):
        cred = self.env['athir.api.credential'].authenticate_token(None)
        self.assertFalse(cred)

    def test_authenticate_invalid_token(self):
        cred = self.env['athir.api.credential'].authenticate_token('wrong-token')
        self.assertFalse(cred)

    def test_authenticate_revoked_token(self):
        self.credential.action_revoke()
        cred = self.env['athir.api.credential'].authenticate_token(self.api_token)
        self.assertFalse(cred)

    def test_extract_bearer_and_api_key(self):
        Credential = self.env['athir.api.credential']
        self.assertEqual(
            Credential.extract_token_from_headers({'Authorization': 'Bearer abc'}),
            'abc',
        )
        self.assertEqual(
            Credential.extract_token_from_headers({'X-API-Key': 'xyz'}),
            'xyz',
        )
        self.assertIsNone(Credential.extract_token_from_headers({}))


@tagged('post_install', '-at_install')
class TestAthirAuthHttp(HttpCase):

    def test_invoice_endpoint_requires_auth(self):
        response = self.url_open(
            '/api/athir/v1/invoices',
            data=json.dumps({}),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        self.assertEqual(response.status_code, 401)
        body = response.json()
        self.assertFalse(body.get('success'))
        self.assertEqual(body['error']['code'], 'UNAUTHORIZED')

from odoo.tests import tagged

from odoo.addons.bh_athir_integration.application.integration_facade import (
    IntegrationFacade,
)
from odoo.addons.bh_athir_integration.domain.exceptions import (
    IdempotencyConflictError,
    UnresolvedMappingError,
)
from odoo.addons.bh_athir_integration.tests.common import (
    AthirIntegrationCommon,
    sample_b2c_payload,
)


@tagged('post_install', '-at_install')
class TestAthirIdempotency(AthirIntegrationCommon):

    def setUp(self):
        super().setUp()
        self.facade = IntegrationFacade(self.env(su=True))

    def test_first_create_then_replay_same_hash(self):
        payload = sample_b2c_payload(invoice_id='ATH-INV-IDEM-1')
        first = self.facade.process('invoice', payload, credential=self.credential)
        self.assertEqual(first['status'], 'created')
        move_id = first['odoo_move_id']

        second = self.facade.process('invoice', payload, credential=self.credential)
        self.assertEqual(second['status'], 'already_processed')
        self.assertEqual(second['odoo_move_id'], move_id)
        self.assertEqual(
            self.env['account.move'].search_count([
                ('athir_invoice_id', '=', 'ATH-INV-IDEM-1'),
            ]),
            1,
        )

    def test_conflict_different_hash(self):
        payload = sample_b2c_payload(invoice_id='ATH-INV-IDEM-2')
        self.facade.process('invoice', payload, credential=self.credential)

        conflict = sample_b2c_payload(
            invoice_id='ATH-INV-IDEM-2',
            total_amount=115.0,
            branch_id='BR-OTHER',
            branch_name='Other',
        )
        with self.assertRaises(IdempotencyConflictError):
            self.facade.process('invoice', conflict, credential=self.credential)

    def test_failed_then_retry(self):
        # Seed a prior failed processed-document (idempotency store).
        self.env['athir.processed.document'].sudo().create({
            'source_system': 'athir',
            'operation': 'invoice',
            'external_id': 'ATH-INV-IDEM-3',
            'payload_hash': 'prior-failed-hash',
            'status': 'failed',
            'error_code': 'UNRESOLVED_PRODUCT',
        })

        # A fresh reject still raises (mapping miss) without blocking the store.
        bad = sample_b2c_payload(invoice_id='ATH-INV-IDEM-3')
        bad['services'][0]['service_id'] = 'SVC-MISSING'
        bad['services'][0]['service_name'] = 'Nope'
        with self.assertRaises(UnresolvedMappingError):
            self.facade.process('invoice', bad, credential=self.credential)

        good = sample_b2c_payload(invoice_id='ATH-INV-IDEM-3')
        result = self.facade.process('invoice', good, credential=self.credential)
        self.assertEqual(result['status'], 'created')
        doc = self.env['athir.processed.document'].sudo().search([
            ('external_id', '=', 'ATH-INV-IDEM-3'),
            ('operation', '=', 'invoice'),
        ])
        self.assertEqual(doc.status, 'succeeded')
        self.assertTrue(doc.odoo_move_id)

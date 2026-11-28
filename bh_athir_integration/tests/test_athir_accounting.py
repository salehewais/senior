from odoo.tests import tagged

from odoo.addons.bh_athir_integration.application.integration_facade import (
    IntegrationFacade,
)
from odoo.addons.bh_athir_integration.domain.exceptions import (
    FinancialDiscrepancyError,
    UnresolvedMappingError,
)
from odoo.addons.bh_athir_integration.tests.common import (
    AthirIntegrationCommon,
    sample_b2b_payload,
    sample_b2c_payload,
)


@tagged('post_install', '-at_install')
class TestAthirAccounting(AthirIntegrationCommon):

    def setUp(self):
        super().setUp()
        self.facade = IntegrationFacade(self.env(su=True))

    def test_create_draft_b2c_invoice(self):
        result = self.facade.process(
            'invoice',
            sample_b2c_payload(invoice_id='ATH-INV-TEST-B2C'),
            credential=self.credential,
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'created')
        move = self.env['account.move'].browse(result['odoo_move_id'])
        self.assertEqual(move.state, 'draft')
        self.assertEqual(move.move_type, 'out_invoice')
        self.assertEqual(move.partner_id, self.partner_b2c)
        self.assertEqual(move.athir_invoice_id, 'ATH-INV-TEST-B2C')
        self.assertAlmostEqual(move.amount_total, 115.0, places=2)

        line = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product')
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_id, self.product)
        self.assertIn(self.tax, line.tax_ids)
        self.assertAlmostEqual(line.discount, 0.0, places=2)
        self.assertEqual(line.athir_service_external_id, 'SVC-1')
        self.assertEqual(line.athir_cash_vat_amount, 15.0)

        traces = move.athir_payment_trace_ids
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces.pay_method_external_id, 'CASH')
        self.assertAlmostEqual(traces.amount, 115.0, places=2)

    def test_create_draft_b2b_invoice(self):
        result = self.facade.process(
            'invoice',
            sample_b2b_payload(invoice_id='ATH-INV-TEST-B2B'),
            credential=self.credential,
        )
        move = self.env['account.move'].browse(result['odoo_move_id'])
        self.assertEqual(move.partner_id, self.partner_b2b)
        self.assertEqual(move.athir_bill_type, 'B2B')
        self.assertEqual(move.state, 'draft')

    def test_discount_percent_conversion(self):
        payload = sample_b2c_payload(
            invoice_id='ATH-INV-DISC',
            total_amount=103.5,  # 90 net + 15% = 103.5
            services=[{
                **sample_b2c_payload()['services'][0],
                'price': 100.0,
                'discount_amount': 10.0,
                'net_price': 90.0,
                'cash_net_without_vat': 90.0,
                'cash_vat_amount': 13.5,
            }],
            pay_methods=[{'pay_method_id': 'CASH', 'amount': 103.5}],
        )
        result = self.facade.process('invoice', payload, credential=self.credential)
        move = self.env['account.move'].browse(result['odoo_move_id'])
        line = move.invoice_line_ids.filtered(lambda l: l.display_type == 'product')
        self.assertAlmostEqual(line.discount, 10.0, places=2)
        self.assertEqual(move.state, 'draft')

    def test_financial_discrepancy_rolls_back(self):
        payload = sample_b2c_payload(
            invoice_id='ATH-INV-BAD-TOTAL',
            total_amount=999.0,
        )
        with self.assertRaises(FinancialDiscrepancyError):
            self.facade.process('invoice', payload, credential=self.credential)
        self.assertFalse(self.env['account.move'].search([
            ('athir_invoice_id', '=', 'ATH-INV-BAD-TOTAL'),
        ]))

    def test_unresolved_product_rejects(self):
        payload = sample_b2c_payload(invoice_id='ATH-INV-NOPROD')
        payload['services'][0]['service_id'] = 'SVC-MISSING'
        payload['services'][0]['service_name'] = 'Nope'
        with self.assertRaises(UnresolvedMappingError):
            self.facade.process('invoice', payload, credential=self.credential)

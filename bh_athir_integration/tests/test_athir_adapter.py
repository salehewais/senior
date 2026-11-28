from odoo.tests import TransactionCase, tagged

from odoo.addons.bh_athir_integration.adapters.athir_invoice_adapter import (
    AthirInvoiceAdapter,
)
from odoo.addons.bh_athir_integration.domain.exceptions import (
    FinancialDiscrepancyError,
    ValidationError,
)
from odoo.addons.bh_athir_integration.domain.validators import validate_canonical_invoice
from odoo.addons.bh_athir_integration.tests.common import (
    sample_b2b_payload,
    sample_b2c_payload,
)


@tagged('post_install', '-at_install')
class TestAthirInvoiceAdapter(TransactionCase):

    def setUp(self):
        super().setUp()
        self.adapter = AthirInvoiceAdapter()

    def test_adapt_valid_b2c(self):
        invoice = self.adapter.adapt(sample_b2c_payload())
        self.assertEqual(invoice.external_invoice_id, 'ATH-INV-1001')
        self.assertEqual(invoice.bill_type, 'B2C')
        self.assertEqual(invoice.mrn, 'MRN-100')
        self.assertEqual(invoice.organization, 'ORG-1')
        self.assertEqual(invoice.branch_id, 'BR-1')
        self.assertEqual(invoice.lines[0].service_id, 'SVC-1')
        self.assertEqual(len(invoice.lines), 1)
        self.assertEqual(len(invoice.payments), 1)
        self.assertEqual(invoice.payments[0].pay_method_id, 'CASH')
        self.assertEqual(invoice.invoice_date.isoformat(), '2026-01-15')

    def test_adapt_valid_b2b(self):
        invoice = self.adapter.adapt(sample_b2b_payload())
        self.assertEqual(invoice.bill_type, 'B2B')
        self.assertEqual(invoice.insurance_company_id, 'INS-1')
        self.assertEqual(invoice.insurance_company_name, 'Bupa')
        self.assertIsNone(invoice.mrn)

    def test_adapt_date_only_transaction_created_at(self):
        payload = sample_b2c_payload()
        payload['services'][0]['transaction_created_at'] = '2026-01-15'
        invoice = self.adapter.adapt(payload)
        self.assertEqual(invoice.invoice_date.isoformat(), '2026-01-15')

    def test_adapt_int_pay_method_id(self):
        payload = sample_b2c_payload(
            pay_methods=[{'pay_method_id': 12, 'amount': 115.0}],
        )
        invoice = self.adapter.adapt(payload)
        self.assertEqual(invoice.payments[0].pay_method_id, '12')

    def test_missing_invoice_id(self):
        with self.assertRaises(ValidationError) as ctx:
            self.adapter.adapt(sample_b2c_payload(invoice_id=None))
        self.assertEqual(ctx.exception.code, 'MISSING_INVOICE_ID')

    def test_missing_bill_type(self):
        with self.assertRaises(ValidationError):
            self.adapter.adapt(sample_b2c_payload(bill_type='X'))

    def test_missing_services(self):
        with self.assertRaises(ValidationError) as ctx:
            self.adapter.adapt(sample_b2c_payload(services=[]))
        self.assertEqual(ctx.exception.code, 'MISSING_SERVICES')

    def test_bad_datetime(self):
        payload = sample_b2c_payload()
        payload['services'][0]['transaction_created_at'] = 'not-a-date'
        with self.assertRaises(ValidationError) as ctx:
            self.adapter.adapt(payload)
        self.assertEqual(ctx.exception.code, 'INVALID_DATE')

    def test_multi_line_multi_pay(self):
        payload = sample_b2c_payload(
            total_amount=230.0,
            services=[
                sample_b2c_payload()['services'][0],
                {
                    **sample_b2c_payload()['services'][0],
                    'service_id': 'SVC-2',
                    'service_name': 'Xray',
                    'transaction_created_at': '2026-01-15T11:00:00',
                },
            ],
            pay_methods=[
                {'pay_method_id': 'CASH', 'amount': 100.0},
                {'pay_method_id': 'CARD', 'amount': 130.0},
            ],
        )
        invoice = self.adapter.adapt(payload)
        self.assertEqual(len(invoice.lines), 2)
        self.assertEqual(len(invoice.payments), 2)

    def test_inconsistent_line_dates(self):
        payload = sample_b2c_payload(
            services=[
                sample_b2c_payload()['services'][0],
                {
                    **sample_b2c_payload()['services'][0],
                    'service_id': 'SVC-2',
                    'service_name': 'Xray',
                    'transaction_created_at': '2026-01-16T11:00:00',
                },
            ],
        )
        invoice = self.adapter.adapt(payload)
        with self.assertRaises(ValidationError) as ctx:
            validate_canonical_invoice(invoice)
        self.assertEqual(ctx.exception.code, 'INCONSISTENT_LINE_DATES')

    def test_financial_inconsistency_net_price(self):
        payload = sample_b2c_payload()
        payload['services'][0]['net_price'] = 50.0
        invoice = self.adapter.adapt(payload)
        with self.assertRaises(FinancialDiscrepancyError):
            validate_canonical_invoice(invoice)

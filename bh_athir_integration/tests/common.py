from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


def sample_b2c_payload(**overrides):
    payload = {
        'invoice_id': 'ATH-INV-1001',
        'bill_type': 'B2C',
        'organization': 'ORG-1',
        'branch_id': 'BR-1',
        'branch_name': 'Main Branch',
        'clinic_id': 'CL-1',
        'clinic_name': 'Dental',
        'cashier_id': 'CA-1',
        'cashier_name': 'Cashier One',
        'mrn': 'MRN-100',
        'total_amount': 115.0,
        'services': [
            {
                'service_id': 'SVC-1',
                'service_name': 'Consultation',
                'service_group_id': 'SG-1',
                'service_group_name': 'OPD',
                'doctor_id': 'DOC-1',
                'doctor_name': 'Dr Smith',
                'price': 100.0,
                'discount_amount': 0.0,
                'net_price': 100.0,
                'tax_code_id': 'TAX-15',
                'insurance_net_without_vat': 0.0,
                'insurance_vat_amount': 0.0,
                'cash_net_without_vat': 100.0,
                'cash_vat_amount': 15.0,
                'transaction_created_at': '2026-01-15T10:00:00',
            },
        ],
        'pay_methods': [
            {'pay_method_id': 'CASH', 'amount': 115.0},
        ],
    }
    payload.update(overrides)
    return payload


def sample_b2b_payload(**overrides):
    payload = sample_b2c_payload(
        bill_type='B2B',
        mrn=None,
        insurance_company_id='INS-1',
        insurance_company_name='Bupa',
        invoice_id='ATH-INV-2001',
    )
    # sample_b2c_payload leaves mrn unless explicitly cleared via update above;
    # ensure B2B payloads do not carry a leftover mrn key with None if unwanted.
    if payload.get('mrn') is None:
        payload.pop('mrn', None)
    payload.update(overrides)
    return payload


@tagged('post_install', '-at_install')
class AthirIntegrationCommon(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.athir_financial_tolerance = 0.01
        cls.company.athir_allow_company_fallback = False
        cls.company.athir_store_raw_payload = False

        cls.partner_b2c = cls.env['res.partner'].search(
            [('athir_mrn', '=', 'MRN-100')], limit=1,
        )
        if not cls.partner_b2c:
            cls.partner_b2c = cls.env['res.partner'].create({
                'name': 'Patient MRN-100',
                'athir_mrn': 'MRN-100',
            })
        cls.partner_b2b = cls.env['res.partner'].search(
            [('athir_insurance_company_id', '=', 'INS-1')], limit=1,
        )
        if not cls.partner_b2b:
            cls.partner_b2b = cls.env['res.partner'].create({
                'name': 'Insurance Bupa',
                'athir_insurance_company_id': 'INS-1',
                'company_type': 'company',
            })

        cls.product = cls.product_a
        cls.tax = cls.env['account.tax'].create({
            'name': 'Athir VAT 15%',
            'amount': 15.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': cls.company.id,
        })

        Mapping = cls.env['athir.external.mapping'].sudo()

        def ensure_mapping(entity_type, external_id, res_model, res_id, company_id=False, name=False):
            domain = [
                ('source_system', '=', 'athir'),
                ('entity_type', '=', entity_type),
                ('external_id', '=', external_id),
                ('company_id', '=', company_id or False),
            ]
            rec = Mapping.search(domain, limit=1)
            vals = {
                'source_system': 'athir',
                'entity_type': entity_type,
                'external_id': external_id,
                'external_name': name or external_id,
                'res_model': res_model,
                'res_id': res_id,
                'company_id': company_id or False,
                'active': True,
            }
            if rec:
                rec.write(vals)
            else:
                Mapping.create(vals)

        ensure_mapping(
            'company', 'ORG-1', 'res.company', cls.company.id, name='Athir Org',
        )
        ensure_mapping(
            'product', 'SVC-1', 'product.product', cls.product.id,
            company_id=cls.company.id, name='Consultation',
        )
        ensure_mapping(
            'tax', 'TAX-15', 'account.tax', cls.tax.id,
            company_id=cls.company.id, name='15%',
        )

        cls.credential = cls.env['athir.api.credential'].sudo().create({
            'name': 'Test Athir Credential',
            'company_id': cls.company.id,
        })
        cls.api_token = 'test-athir-token-secret-value'
        cls.credential.sudo().write({
            'token_hash': cls.env['athir.api.credential']._hash_token(cls.api_token),
            'revoked': False,
        })

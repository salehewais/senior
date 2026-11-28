from odoo.tests import tagged

from odoo.addons.bh_athir_integration.domain.canonical import CanonicalInvoice
from odoo.addons.bh_athir_integration.domain.exceptions import (
    AmbiguousMappingError,
    UnresolvedMappingError,
)
from odoo.addons.bh_athir_integration.mappers.customer_mapper import CustomerMapper
from odoo.addons.bh_athir_integration.mappers.organization_mapper import OrganizationMapper
from odoo.addons.bh_athir_integration.mappers.tax_mapper import TaxMapper
from odoo.addons.bh_athir_integration.tests.common import AthirIntegrationCommon


def _customer_stub(**kwargs):
    """Minimal CanonicalInvoice for CustomerMapper unit tests."""
    defaults = {
        'external_invoice_id': 'stub',
        'organization': 'ORG-1',
        'invoice_date': None,
        'branch_id': 'BR-1',
        'clinic_id': 'CL-1',
        'lines': [],
        'payments': [],
        'source_payload_hash': 'stub',
    }
    defaults.update(kwargs)
    # invoice_date is required; use a sentinel date when unused by mapper.
    if defaults['invoice_date'] is None:
        from datetime import date
        defaults['invoice_date'] = date(2026, 1, 15)
    return CanonicalInvoice(**defaults)


@tagged('post_install', '-at_install')
class TestAthirMapping(AthirIntegrationCommon):

    def test_company_mapping_hit(self):
        company = OrganizationMapper(self.env).resolve('ORG-1')
        self.assertEqual(company, self.company)

    def test_company_mapping_miss(self):
        with self.assertRaises(UnresolvedMappingError) as ctx:
            OrganizationMapper(self.env).resolve('ORG-MISSING')
        self.assertEqual(ctx.exception.code, 'UNRESOLVED_COMPANY')

    def test_b2c_customer_by_mrn(self):
        canonical = _customer_stub(bill_type='B2C', mrn='MRN-100')
        partner = CustomerMapper(self.env).resolve(canonical, company=self.company)
        self.assertEqual(partner, self.partner_b2c)

    def test_b2b_customer_by_insurance_field(self):
        canonical = _customer_stub(
            bill_type='B2B',
            insurance_company_id='INS-1',
            insurance_company_name='Bupa',
        )
        partner = CustomerMapper(self.env).resolve(canonical, company=self.company)
        self.assertEqual(partner, self.partner_b2b)

    def test_customer_miss(self):
        canonical = _customer_stub(bill_type='B2C', mrn='MRN-UNKNOWN')
        with self.assertRaises(UnresolvedMappingError) as ctx:
            CustomerMapper(self.env).resolve(canonical, company=self.company)
        self.assertEqual(ctx.exception.code, 'UNRESOLVED_CUSTOMER')

    def test_tax_unresolved(self):
        with self.assertRaises(UnresolvedMappingError) as ctx:
            TaxMapper(self.env).resolve('UNKNOWN-TAX', company=self.company)
        self.assertEqual(ctx.exception.code, 'UNRESOLVED_TAX')

    def test_ambiguous_mapping(self):
        other_company = self.env['res.company'].create({'name': 'Other Co'})
        Mapping = self.env['athir.external.mapping'].sudo()
        Mapping.create({
            'entity_type': 'tax',
            'external_id': 'TAX-15',
            'res_model': 'account.tax',
            'res_id': self.tax.id,
            'company_id': other_company.id,
        })
        # Two global mappings for the same external id → ambiguous.
        Mapping.create({
            'entity_type': 'product',
            'external_id': 'SVC-AMB',
            'res_model': 'product.product',
            'res_id': self.product.id,
            'company_id': False,
        })
        Mapping.create({
            'entity_type': 'product',
            'external_id': 'SVC-AMB',
            'res_model': 'product.product',
            'res_id': self.product_b.id,
            'company_id': False,
        })
        from odoo.addons.bh_athir_integration.mappers.product_mapper import ProductMapper
        with self.assertRaises(AmbiguousMappingError):
            ProductMapper(self.env).resolve('SVC-AMB', company=self.company)

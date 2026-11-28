#!/usr/bin/env python3
"""Seed sample mappings/partners for scripts/test_invoice.py.

Run inside Odoo shell:
  ./odoo-bin shell -d athir_test ... < scripts/setup_sample_data.py

Or from an open shell:
  >>> exec(open('.../scripts/setup_sample_data.py').read())
"""

company = env.company

tax = env['account.tax'].search([
    ('amount', '=', 15.0),
    ('type_tax_use', '=', 'sale'),
    ('company_id', '=', company.id),
], limit=1)
if not tax:
    tax = env['account.tax'].create({
        'name': 'Athir VAT 15%',
        'amount': 15.0,
        'amount_type': 'percent',
        'type_tax_use': 'sale',
        'company_id': company.id,
    })

product = env['product.product'].search([('default_code', '=', 'SVC-1')], limit=1)
if not product:
    product = env['product.product'].create({
        'name': 'Consultation',
        'default_code': 'SVC-1',
        'list_price': 100.0,
        'type': 'service',
        'taxes_id': [(6, 0, tax.ids)],
    })

partner = env['res.partner'].search([('athir_mrn', '=', 'MRN-100')], limit=1)
if not partner:
    partner = env['res.partner'].create({
        'name': 'Patient MRN-100',
        'athir_mrn': 'MRN-100',
    })

insurance = env['res.partner'].search([('athir_insurance_company_id', '=', 'INS-1')], limit=1)
if not insurance:
    insurance = env['res.partner'].create({
        'name': 'Insurance Bupa',
        'company_type': 'company',
        'athir_insurance_company_id': 'INS-1',
    })

Mapping = env['athir.external.mapping'].sudo()


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


ensure_mapping('company', 'ORG-1', 'res.company', company.id, name='Athir Org')
ensure_mapping(
    'product', 'SVC-1', 'product.product', product.id,
    company_id=company.id, name='Consultation',
)
ensure_mapping(
    'tax', 'TAX-15', 'account.tax', tax.id,
    company_id=company.id, name='15%',
)

env.cr.commit()
print('Sample Athir data ready:')
print('  company mapping ORG-1 ->', company.name)
print('  product mapping SVC-1 ->', product.display_name)
print('  tax mapping TAX-15 ->', tax.display_name)
print('  B2C partner MRN-100 ->', partner.display_name)
print('  B2B partner INS-1 ->', insurance.display_name)

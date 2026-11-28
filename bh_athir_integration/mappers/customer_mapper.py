from odoo.addons.bh_athir_integration.domain.exceptions import (
    AmbiguousMappingError,
    UnresolvedMappingError,
)
from .mapping_service import MappingService


class CustomerMapper:
    def __init__(self, env):
        self.env = env
        self.mapping = MappingService(env)
        self.Partner = env['res.partner'].sudo()

    def resolve(self, canonical, company=None):
        if canonical.bill_type == 'B2C':
            return self._resolve_b2c(canonical.mrn, company)
        return self._resolve_b2b(canonical.insurance_company_id, company)

    def _resolve_b2c(self, mrn, company):
        mapped = self.mapping.resolve(
            'customer', mrn, company=company, required=False, code_prefix='CUSTOMER',
        )
        if mapped:
            return mapped

        partners = self.Partner.search([('athir_mrn', '=', mrn)])
        if len(partners) > 1:
            raise AmbiguousMappingError(
                'Multiple partners with Athir MRN %s' % mrn,
                details={'mrn': mrn},
            )
        if not partners:
            raise UnresolvedMappingError(
                'No customer for MRN %s' % mrn,
                code='UNRESOLVED_CUSTOMER',
                details={'mrn': mrn},
            )
        return partners

    def _resolve_b2b(self, insurance_company_id, company):
        mapped = self.mapping.resolve(
            'customer',
            insurance_company_id,
            company=company,
            required=False,
            code_prefix='CUSTOMER',
        )
        if mapped:
            return mapped

        partners = self.Partner.search([
            ('athir_insurance_company_id', '=', insurance_company_id),
        ])
        if len(partners) > 1:
            raise AmbiguousMappingError(
                'Multiple partners with Athir insurance id %s' % insurance_company_id,
                details={'insurance_id': insurance_company_id},
            )
        if not partners:
            raise UnresolvedMappingError(
                'No customer for insurance id %s' % insurance_company_id,
                code='UNRESOLVED_CUSTOMER',
                details={'insurance_id': insurance_company_id},
            )
        return partners

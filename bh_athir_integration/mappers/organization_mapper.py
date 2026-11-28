from odoo.addons.bh_athir_integration.domain.exceptions import UnresolvedMappingError
from .mapping_service import MappingService


class OrganizationMapper:
    def __init__(self, env):
        self.env = env
        self.mapping = MappingService(env)

    def resolve(self, organization, fallback_company=None):
        company = self.mapping.resolve(
            'company',
            organization,
            company=None,
            required=False,
            code_prefix='COMPANY',
        )
        if company:
            return company

        if fallback_company and fallback_company.athir_allow_company_fallback:
            return fallback_company

        raise UnresolvedMappingError(
            'organization could not be mapped to an Odoo company',
            code='UNRESOLVED_COMPANY',
            details={'organization': organization},
        )

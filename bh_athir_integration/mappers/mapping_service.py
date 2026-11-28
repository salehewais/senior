from odoo.addons.bh_athir_integration.domain.exceptions import (
    AmbiguousMappingError,
    UnresolvedMappingError,
)


class MappingService:
    SOURCE_SYSTEM = 'athir'

    def __init__(self, env):
        self.env = env
        self.Mapping = env['athir.external.mapping'].sudo()

    def resolve(
        self,
        entity_type,
        external_id,
        company=None,
        *,
        required=True,
        code_prefix=None,
    ):
        if not external_id:
            if required:
                raise UnresolvedMappingError(
                    'Missing external id for %s' % entity_type,
                    code='UNRESOLVED_%s' % (code_prefix or entity_type.upper()),
                )
            return self.env['athir.external.mapping'].browse()

        domain = [
            ('source_system', '=', self.SOURCE_SYSTEM),
            ('entity_type', '=', entity_type),
            ('external_id', '=', str(external_id)),
            ('active', '=', True),
        ]
        if company:
            domain.append(('company_id', 'in', [False, company.id]))

        matches = self.Mapping.search(domain)
        if company and len(matches) > 1:
            company_specific = matches.filtered(lambda m: m.company_id.id == company.id)
            if company_specific:
                matches = company_specific

        if not matches:
            if required:
                raise UnresolvedMappingError(
                    'No mapping for %s/%s' % (entity_type, external_id),
                    code='UNRESOLVED_%s' % (code_prefix or entity_type.upper()),
                    details={'entity_type': entity_type, 'external_id': str(external_id)},
                )
            return self.env['athir.external.mapping'].browse()

        if len(matches) > 1:
            raise AmbiguousMappingError(
                'Ambiguous mapping for %s/%s' % (entity_type, external_id),
                details={
                    'entity_type': entity_type,
                    'external_id': str(external_id),
                    'count': len(matches),
                },
            )

        mapping = matches[0]
        record = mapping.get_record()
        if not record:
            raise UnresolvedMappingError(
                'Mapped record missing for %s/%s' % (entity_type, external_id),
                code='UNRESOLVED_%s' % (code_prefix or entity_type.upper()),
                details={'entity_type': entity_type, 'external_id': str(external_id)},
            )
        return record

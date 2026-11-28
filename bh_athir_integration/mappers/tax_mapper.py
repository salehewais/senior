from .mapping_service import MappingService


class TaxMapper:
    def __init__(self, env):
        self.mapping = MappingService(env)

    def resolve(self, tax_code_external_id, company=None):
        # Mapping only — never fuzzy-match labels like "15%".
        return self.mapping.resolve(
            'tax',
            tax_code_external_id,
            company=company,
            required=True,
            code_prefix='TAX',
        )

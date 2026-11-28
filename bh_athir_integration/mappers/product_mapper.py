from .mapping_service import MappingService


class ProductMapper:
    def __init__(self, env):
        self.mapping = MappingService(env)

    def resolve(self, service_external_id, company=None):
        return self.mapping.resolve(
            'product',
            service_external_id,
            company=company,
            required=True,
            code_prefix='PRODUCT',
        )

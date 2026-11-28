from .mapping_service import MappingService


class PaymentMapper:
    def __init__(self, env):
        self.mapping = MappingService(env)

    def resolve(self, pay_method_external_id, company=None, required=False):
        return self.mapping.resolve(
            'payment_method',
            pay_method_external_id,
            company=company,
            required=required,
            code_prefix='PAYMENT_METHOD',
        )

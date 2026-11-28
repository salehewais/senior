from odoo.addons.bh_athir_integration.application.strategies.invoice_strategy import (
    InvoiceProcessingStrategy,
)
from odoo.addons.bh_athir_integration.application.strategies.refund_strategy import (
    RefundProcessingStrategy,
)
from odoo.addons.bh_athir_integration.domain.exceptions import ValidationError


class ProcessorFactory:
    def __init__(self, env):
        self.env = env
        self._registry = {
            'invoice': InvoiceProcessingStrategy,
            'refund': RefundProcessingStrategy,
        }

    def get(self, operation):
        strategy_cls = self._registry.get(operation)
        if not strategy_cls:
            raise ValidationError(
                'Unknown operation: %s' % operation,
                code='UNKNOWN_OPERATION',
            )
        return strategy_cls(self.env)

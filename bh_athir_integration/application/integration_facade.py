from odoo.addons.bh_athir_integration.application.processor_factory import (
    ProcessorFactory,
)


class IntegrationFacade:
    """Single application entry after authentication."""

    def __init__(self, env):
        self.env = env
        self.factory = ProcessorFactory(env)

    def process(self, operation, payload, credential=None, correlation_id=None):
        strategy = self.factory.get(operation)
        return strategy.process(
            payload,
            credential=credential,
            correlation_id=correlation_id,
        )

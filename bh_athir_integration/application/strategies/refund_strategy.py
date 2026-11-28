import json
import uuid

from odoo.addons.bh_athir_integration.adapters.athir_refund_adapter import (
    AthirRefundAdapter,
)
from odoo.addons.bh_athir_integration.domain.exceptions import UnsupportedContractError


class RefundProcessingStrategy:
    OPERATION = 'refund'

    def __init__(self, env):
        self.env = env
        self.adapter = AthirRefundAdapter()
        self.Log = env['athir.integration.log']

    def process(self, payload, credential=None, correlation_id=None):
        correlation_id = correlation_id or str(uuid.uuid4())
        vals = {
            'name': correlation_id,
            'operation': self.OPERATION,
            'status': 'rejected',
            'correlation_id': correlation_id,
            'credential_id': credential.id if credential else False,
            'error_code': 'UNSUPPORTED_CONTRACT',
            'error_message': 'Athir refund payload contract is not supported yet',
        }
        company = (
            credential.company_id
            if credential and credential.company_id
            else self.env.company
        )
        if company.athir_store_raw_payload and isinstance(payload, dict):
            vals['raw_payload'] = json.dumps(payload, default=str)
        self.Log.sudo().create(vals)

        # Adapter raises the same domain error (extension point).
        raise UnsupportedContractError(
            'Athir refund payload contract is not supported yet',
        )

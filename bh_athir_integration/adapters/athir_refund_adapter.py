from odoo.addons.bh_athir_integration.domain.exceptions import UnsupportedContractError


class AthirRefundAdapter:
    """Extension point. Refund contract is not approved yet."""

    def adapt(self, payload):
        raise UnsupportedContractError(
            'Athir refund payload contract is not supported yet',
        )

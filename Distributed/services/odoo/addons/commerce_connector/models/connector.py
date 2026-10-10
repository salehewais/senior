"""Apply OrderConfirmed inside one odoo_db transaction.

The worker calls this method over XML-RPC. The processed-event row and the
sales order commit together when the RPC returns. The worker acks after that.
"""

import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError

from commerce_erp.domain import commands as _commands
from commerce_erp.domain import confirmed as _confirmed

from ..services.command_store import _OdooCommandStore
from ..services.order_store import _OdooStore

_logger = logging.getLogger(__name__)


class CommerceConnector(models.Model):
    _name = "commerce.connector"
    _description = "Apply OrderConfirmed through the Odoo ORM"

    name = fields.Char()

    @api.model
    def apply_order_confirmed(self, envelope):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError("Only the ERP service user can apply OrderConfirmed.")
        result = _confirmed.apply_confirmed_order(_OdooStore(self.env), envelope)
        event_id = envelope.get("event_id") if isinstance(envelope, dict) else None
        _logger.info(
            "apply_order_confirmed outcome=%s reason=%s event_id=%s",
            result.outcome,
            result.reason,
            event_id,
        )
        return result.as_dict()

    @api.model
    def apply_command(self, envelope):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError("Only the ERP service user can apply a saga command.")
        result = _commands.apply_command(_OdooCommandStore(self.env), envelope)
        event_id = envelope.get("event_id") if isinstance(envelope, dict) else None
        _logger.info(
            "apply_command outcome=%s reason=%s event_id=%s",
            result.outcome,
            result.reason,
            event_id,
        )
        return result.as_dict()

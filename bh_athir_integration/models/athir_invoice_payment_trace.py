from odoo import fields, models


class AthirInvoicePaymentTrace(models.Model):
    _name = 'athir.invoice.payment.trace'
    _description = 'Athir Invoice Payment Trace'
    _order = 'id'

    move_id = fields.Many2one(
        'account.move',
        required=True,
        ondelete='cascade',
        index=True,
    )
    log_id = fields.Many2one('athir.integration.log', ondelete='set null')
    pay_method_external_id = fields.Char(required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        related='move_id.currency_id',
        store=True,
    )
    payment_method_id = fields.Many2one(
        'account.payment.method',
        string='Resolved Payment Method',
        help='Optional linked Odoo payment method when mapping exists. '
             'No payment is registered in v1.',
    )
    note = fields.Char()

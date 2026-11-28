from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    athir_source_system = fields.Char(index=True, copy=False)
    athir_invoice_id = fields.Char(index=True, copy=False)
    athir_bill_type = fields.Selection(
        [('B2B', 'B2B'), ('B2C', 'B2C')],
        copy=False,
    )
    athir_organization_external_id = fields.Char(copy=False)
    athir_organization_name = fields.Char(copy=False)
    athir_branch_external_id = fields.Char(copy=False)
    athir_branch_name = fields.Char(copy=False)
    athir_clinic_external_id = fields.Char(copy=False)
    athir_clinic_name = fields.Char(copy=False)
    athir_cashier_external_id = fields.Char(copy=False)
    athir_cashier_name = fields.Char(copy=False)
    athir_customer_external_id = fields.Char(copy=False)
    athir_customer_mrn = fields.Char(copy=False)
    athir_payload_hash = fields.Char(copy=False)
    athir_payment_trace_ids = fields.One2many(
        'athir.invoice.payment.trace',
        'move_id',
        string='Athir Payment Traces',
    )

    _athir_invoice_uniq = models.Constraint(
        'UNIQUE(athir_source_system, athir_invoice_id, company_id)',
        'This Athir invoice was already imported for this company.',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    athir_service_external_id = fields.Char(copy=False)
    athir_service_name = fields.Char(copy=False)
    athir_service_group_external_id = fields.Char(copy=False)
    athir_service_group_name = fields.Char(copy=False)
    athir_doctor_external_id = fields.Char(copy=False)
    athir_doctor_name = fields.Char(copy=False)
    athir_tax_code_external_id = fields.Char(copy=False)
    athir_discount_amount = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_net_price = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_insurance_net_without_vat = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_insurance_vat_amount = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_cash_net_without_vat = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_cash_vat_amount = fields.Monetary(
        currency_field='currency_id',
        copy=False,
    )
    athir_transaction_created_at = fields.Datetime(copy=False)

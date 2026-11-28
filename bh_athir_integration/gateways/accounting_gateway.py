from decimal import Decimal

from odoo.addons.bh_athir_integration.domain.exceptions import (
    FinancialDiscrepancyError,
    ValidationError,
)


class AccountingGateway:
    """Create draft customer invoices from resolved Athir data. Never posts or pays."""

    def __init__(self, env):
        self.env = env
        self.Move = env['account.move'].sudo()

    def create_draft_customer_invoice(self, canonical, resolved):
        company = resolved['company']
        partner = resolved['partner']
        tolerance = Decimal(str(company.athir_financial_tolerance or 0.01))

        line_commands = []
        for line, line_resolved in zip(canonical.lines, resolved['lines']):
            product = line_resolved['product']
            tax = line_resolved['tax']
            discount_pct = self._discount_percent(line.price, line.discount_amount)
            line_commands.append((0, 0, {
                'product_id': product.id,
                'name': line.service_name or product.display_name,
                'quantity': 1.0,
                'price_unit': float(line.price),
                'discount': float(discount_pct),
                'tax_ids': [(6, 0, tax.ids)],
                'athir_service_external_id': line.service_id,
                'athir_service_name': line.service_name or False,
                'athir_service_group_external_id': line.service_group_id or False,
                'athir_service_group_name': line.service_group_name or False,
                'athir_doctor_external_id': line.doctor_id or False,
                'athir_doctor_name': line.doctor_name or False,
                'athir_tax_code_external_id': line.tax_code_id,
                'athir_discount_amount': float(line.discount_amount),
                'athir_net_price': float(line.net_price),
                'athir_insurance_net_without_vat': float(line.insurance_net_without_vat),
                'athir_insurance_vat_amount': float(line.insurance_vat_amount),
                'athir_cash_net_without_vat': float(line.cash_net_without_vat),
                'athir_cash_vat_amount': float(line.cash_vat_amount),
                'athir_transaction_created_at': line.transaction_created_at.replace(
                    tzinfo=None,
                ),
            }))

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': canonical.invoice_date,
            'company_id': company.id,
            'ref': canonical.external_invoice_id,
            'invoice_line_ids': line_commands,
            'athir_source_system': 'athir',
            'athir_invoice_id': canonical.external_invoice_id,
            'athir_bill_type': canonical.bill_type,
            'athir_organization_external_id': canonical.organization,
            'athir_organization_name': False,
            'athir_branch_external_id': canonical.branch_id,
            'athir_branch_name': canonical.branch_name or False,
            'athir_clinic_external_id': canonical.clinic_id,
            'athir_clinic_name': canonical.clinic_name or False,
            'athir_cashier_external_id': canonical.cashier_id or False,
            'athir_cashier_name': canonical.cashier_name or False,
            'athir_customer_external_id': (
                canonical.insurance_company_id
                if canonical.bill_type == 'B2B'
                else False
            ),
            'athir_customer_mrn': (
                canonical.mrn if canonical.bill_type == 'B2C' else False
            ),
            'athir_payload_hash': canonical.source_payload_hash,
        }

        move = self.Move.with_company(company).create(move_vals)
        if move.state != 'draft':
            raise ValidationError(
                'Invoice was not left in draft state',
                code='UNEXPECTED_STATE',
            )

        self._assert_financials(move, canonical, tolerance)
        return move

    def _discount_percent(self, price, discount_amount):
        price = Decimal(price)
        discount_amount = Decimal(discount_amount)
        if price == 0:
            if discount_amount != 0:
                raise ValidationError(
                    'discount_amount provided with zero price',
                    code='INVALID_DISCOUNT',
                )
            return Decimal('0')
        return (discount_amount / price) * Decimal('100')

    def _assert_financials(self, move, canonical, tolerance):
        if canonical.total_amount is None:
            return
        odoo_total = Decimal(str(move.amount_total))
        expected = Decimal(canonical.total_amount)
        if abs(odoo_total - expected) > tolerance:
            # Roll back by raising — caller runs inside a transaction/savepoint.
            raise FinancialDiscrepancyError(
                'Odoo invoice total does not match Athir total_amount',
                details={
                    'odoo_total': str(odoo_total),
                    'athir_total': str(expected),
                    'tolerance': str(tolerance),
                },
            )

    def create_payment_traces(self, move, payments, resolved_methods, log=None):
        Trace = self.env['athir.invoice.payment.trace'].sudo()
        for payment, method in zip(payments, resolved_methods):
            method_id = False
            if method and method._name == 'account.payment.method':
                method_id = method.id
            Trace.create({
                'move_id': move.id,
                'log_id': log.id if log else False,
                'pay_method_external_id': payment.pay_method_id,
                'amount': float(payment.amount),
                'payment_method_id': method_id,
            })

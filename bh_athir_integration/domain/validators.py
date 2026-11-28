from decimal import Decimal

from .exceptions import FinancialDiscrepancyError, ValidationError
from .canonical import CanonicalInvoice


def validate_canonical_invoice(invoice: CanonicalInvoice, tolerance: Decimal = Decimal('0.01')):
    if not invoice.external_invoice_id:
        raise ValidationError('invoice_id is required', code='MISSING_INVOICE_ID')
    if invoice.bill_type not in ('B2B', 'B2C'):
        raise ValidationError('bill_type must be B2B or B2C', code='INVALID_BILL_TYPE')
    if not invoice.organization:
        raise ValidationError('organization is required', code='MISSING_ORGANIZATION')
    if not invoice.lines:
        raise ValidationError('services must not be empty', code='MISSING_SERVICES')
    if not invoice.branch_id:
        raise ValidationError('branch_id is required', code='MISSING_BRANCH')
    if not invoice.clinic_id:
        raise ValidationError('clinic_id is required', code='MISSING_CLINIC')

    if invoice.bill_type == 'B2C':
        if not invoice.mrn:
            raise ValidationError('mrn is required for B2C', code='MISSING_MRN')
    else:
        if not invoice.insurance_company_id:
            raise ValidationError(
                'insurance_company_id is required for B2B',
                code='MISSING_INSURANCE',
            )

    dates = {line.transaction_created_at.date() for line in invoice.lines}
    if len(dates) > 1:
        raise ValidationError(
            'transaction_created_at dates are inconsistent across services',
            code='INCONSISTENT_LINE_DATES',
        )

    for idx, line in enumerate(invoice.lines):
        if line.price < 0:
            raise ValidationError(
                'service price cannot be negative',
                code='INVALID_PRICE',
                details={'line_index': idx},
            )
        if line.discount_amount < 0:
            raise ValidationError(
                'discount_amount cannot be negative',
                code='INVALID_DISCOUNT',
                details={'line_index': idx},
            )
        expected_net = line.price - line.discount_amount
        if abs(expected_net - line.net_price) > tolerance:
            raise FinancialDiscrepancyError(
                'net_price does not match price - discount_amount',
                details={
                    'line_index': idx,
                    'expected_net': str(expected_net),
                    'net_price': str(line.net_price),
                },
            )
        if not line.tax_code_id:
            raise ValidationError(
                'tax_code_id is required on each service',
                code='MISSING_TAX_CODE',
                details={'line_index': idx},
            )
        if not line.service_id:
            raise ValidationError(
                'service_id is required',
                code='MISSING_SERVICE',
                details={'line_index': idx},
            )

    if invoice.payments:
        for idx, payment in enumerate(invoice.payments):
            if not payment.pay_method_id:
                raise ValidationError(
                    'pay_method_id is required',
                    code='MISSING_PAY_METHOD',
                    details={'payment_index': idx},
                )

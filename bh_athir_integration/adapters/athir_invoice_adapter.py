from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from odoo.addons.bh_athir_integration.domain.canonical import (
    CanonicalInvoice,
    CanonicalPayment,
    CanonicalServiceLine,
)
from odoo.addons.bh_athir_integration.domain.exceptions import ValidationError


def _as_dict(value: Any, field_name: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(
            '%s must be an object' % field_name,
            code='INVALID_TYPE',
            details={'field': field_name},
        )
    return value


def _as_list(value: Any, field_name: str) -> list:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValidationError(
            '%s must be an array' % field_name,
            code='INVALID_TYPE',
            details={'field': field_name},
        )
    return value


def _decimal(value: Any, field_name: str, default: Decimal | None = None) -> Decimal:
    if value is None:
        if default is not None:
            return default
        raise ValidationError(
            '%s is required' % field_name,
            code='MISSING_FIELD',
            details={'field': field_name},
        )
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(
            '%s must be numeric' % field_name,
            code='INVALID_TYPE',
            details={'field': field_name},
        ) from exc


def _optional_str(value: Any) -> str | None:
    if value is None or value == '':
        return None
    return str(value)


def _required_str(value: Any, field_name: str) -> str:
    text = _optional_str(value)
    if not text:
        raise ValidationError(
            '%s is required' % field_name,
            code='MISSING_FIELD',
            details={'field': field_name},
        )
    return text


def _parse_datetime(value: Any, field_name: str) -> datetime:
    if not value or not isinstance(value, str):
        raise ValidationError(
            '%s must be an ISO date or datetime string' % field_name,
            code='INVALID_DATE',
            details={'field': field_name},
        )
    text = value.strip().replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass
    try:
        parsed_date = date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(
            '%s is not a valid date or datetime' % field_name,
            code='INVALID_DATE',
            details={'field': field_name, 'value': value},
        ) from exc
    return datetime(parsed_date.year, parsed_date.month, parsed_date.day)


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class AthirInvoiceAdapter:
    """Athir flat JSON → CanonicalInvoice. No ORM access."""

    SOURCE_SYSTEM = 'athir'

    def adapt(self, payload: Any) -> CanonicalInvoice:
        if not isinstance(payload, dict):
            raise ValidationError('Payload must be a JSON object', code='INVALID_PAYLOAD')

        invoice_id = payload.get('invoice_id')
        if not invoice_id:
            raise ValidationError('invoice_id is required', code='MISSING_INVOICE_ID')

        bill_type = payload.get('bill_type')
        if bill_type not in ('B2B', 'B2C'):
            raise ValidationError(
                'bill_type must be B2B or B2C',
                code='INVALID_BILL_TYPE',
            )

        organization = payload.get('organization')
        if organization is None or organization == '':
            raise ValidationError('organization is required', code='MISSING_ORGANIZATION')
        if isinstance(organization, dict):
            raise ValidationError(
                'organization must be a string (flat contract)',
                code='INVALID_TYPE',
                details={'field': 'organization'},
            )
        organization = str(organization)

        branch_id = _required_str(payload.get('branch_id'), 'branch_id')
        clinic_id = _required_str(payload.get('clinic_id'), 'clinic_id')

        mrn = None
        insurance_company_id = None
        insurance_company_name = None
        if bill_type == 'B2C':
            mrn = _optional_str(payload.get('mrn'))
            if not mrn:
                raise ValidationError('mrn is required for B2C', code='MISSING_MRN')
        else:
            insurance_company_id = _optional_str(payload.get('insurance_company_id'))
            if not insurance_company_id:
                raise ValidationError(
                    'insurance_company_id is required for B2B',
                    code='MISSING_INSURANCE',
                )
            insurance_company_name = _optional_str(payload.get('insurance_company_name'))

        lines = self._adapt_services(_as_list(payload.get('services'), 'services'))
        if not lines:
            raise ValidationError('services must not be empty', code='MISSING_SERVICES')

        payments = self._adapt_payments(_as_list(payload.get('pay_methods'), 'pay_methods'))
        total_amount = None
        if payload.get('total_amount') is not None:
            total_amount = _decimal(payload.get('total_amount'), 'total_amount')

        invoice_date = lines[0].transaction_created_at.date()

        return CanonicalInvoice(
            external_invoice_id=str(invoice_id),
            bill_type=bill_type,
            organization=organization,
            invoice_date=invoice_date,
            branch_id=branch_id,
            branch_name=_optional_str(payload.get('branch_name')),
            clinic_id=clinic_id,
            clinic_name=_optional_str(payload.get('clinic_name')),
            cashier_id=_optional_str(payload.get('cashier_id')),
            cashier_name=_optional_str(payload.get('cashier_name')),
            mrn=mrn,
            insurance_company_id=insurance_company_id,
            insurance_company_name=insurance_company_name,
            lines=lines,
            payments=payments,
            total_amount=total_amount,
            source_payload_hash=_payload_hash(payload),
            raw_payload=payload,
        )

    def _adapt_services(self, services: list) -> list[CanonicalServiceLine]:
        lines = []
        for idx, raw in enumerate(services):
            data = _as_dict(raw, 'services[%s]' % idx)
            service_id = _optional_str(data.get('service_id'))
            if not service_id:
                raise ValidationError(
                    'service_id is required',
                    code='MISSING_SERVICE',
                    details={'line_index': idx},
                )
            tax_code = data.get('tax_code_id')
            if tax_code is None or tax_code == '':
                raise ValidationError(
                    'tax_code_id is required',
                    code='MISSING_TAX_CODE',
                    details={'line_index': idx},
                )
            created_at = _parse_datetime(
                data.get('transaction_created_at'),
                'services[%s].transaction_created_at' % idx,
            )
            price = _decimal(data.get('price'), 'services[%s].price' % idx)
            discount_amount = _decimal(
                data.get('discount_amount'),
                'services[%s].discount_amount' % idx,
                default=Decimal('0'),
            )
            if data.get('net_price') is not None:
                net_price = _decimal(data.get('net_price'), 'services[%s].net_price' % idx)
            else:
                net_price = price - discount_amount

            lines.append(CanonicalServiceLine(
                service_id=service_id,
                service_name=_optional_str(data.get('service_name')),
                service_group_id=_optional_str(data.get('service_group_id')),
                service_group_name=_optional_str(data.get('service_group_name')),
                doctor_id=_optional_str(data.get('doctor_id')),
                doctor_name=_optional_str(data.get('doctor_name')),
                price=price,
                discount_amount=discount_amount,
                net_price=net_price,
                tax_code_id=str(tax_code),
                insurance_net_without_vat=_decimal(
                    data.get('insurance_net_without_vat'),
                    'insurance_net_without_vat',
                    default=Decimal('0'),
                ),
                insurance_vat_amount=_decimal(
                    data.get('insurance_vat_amount'),
                    'insurance_vat_amount',
                    default=Decimal('0'),
                ),
                cash_net_without_vat=_decimal(
                    data.get('cash_net_without_vat'),
                    'cash_net_without_vat',
                    default=Decimal('0'),
                ),
                cash_vat_amount=_decimal(
                    data.get('cash_vat_amount'),
                    'cash_vat_amount',
                    default=Decimal('0'),
                ),
                transaction_created_at=created_at,
            ))
        return lines

    def _adapt_payments(self, payments: list) -> list[CanonicalPayment]:
        result = []
        for idx, raw in enumerate(payments):
            data = _as_dict(raw, 'pay_methods[%s]' % idx)
            method_id = data.get('pay_method_id')
            if method_id is None or method_id == '':
                raise ValidationError(
                    'pay_method_id is required',
                    code='MISSING_PAY_METHOD',
                    details={'payment_index': idx},
                )
            if not isinstance(method_id, (str, int)):
                raise ValidationError(
                    'pay_method_id must be a string or integer',
                    code='INVALID_TYPE',
                    details={'field': 'pay_method_id', 'payment_index': idx},
                )
            amount = _decimal(data.get('amount'), 'pay_methods[%s].amount' % idx)
            result.append(CanonicalPayment(
                pay_method_id=str(method_id),
                amount=amount,
            ))
        return result

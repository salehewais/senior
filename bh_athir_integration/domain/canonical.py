from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional


BillType = Literal['B2B', 'B2C']


@dataclass(frozen=True)
class CanonicalServiceLine:
    service_id: str
    price: Decimal
    discount_amount: Decimal
    net_price: Decimal
    tax_code_id: str
    transaction_created_at: datetime
    service_name: Optional[str] = None
    service_group_id: Optional[str] = None
    service_group_name: Optional[str] = None
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    insurance_net_without_vat: Decimal = Decimal('0')
    insurance_vat_amount: Decimal = Decimal('0')
    cash_net_without_vat: Decimal = Decimal('0')
    cash_vat_amount: Decimal = Decimal('0')


@dataclass(frozen=True)
class CanonicalPayment:
    pay_method_id: str
    amount: Decimal


@dataclass(frozen=True)
class CanonicalInvoice:
    external_invoice_id: str
    bill_type: BillType
    organization: str
    invoice_date: date
    branch_id: str
    clinic_id: str
    lines: list[CanonicalServiceLine]
    payments: list[CanonicalPayment]
    source_payload_hash: str
    mrn: Optional[str] = None
    insurance_company_id: Optional[str] = None
    insurance_company_name: Optional[str] = None
    branch_name: Optional[str] = None
    clinic_name: Optional[str] = None
    cashier_id: Optional[str] = None
    cashier_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    raw_payload: Optional[dict] = field(default=None, compare=False, hash=False)

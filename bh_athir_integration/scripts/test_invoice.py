#!/usr/bin/env python3
"""Manual HTTP smoke test for POST /api/athir/v1/invoices.

Fill CONFIG below (or set env vars / CLI flags), then run from PyCharm or:
  python3 scripts/test_invoice.py
  python3 scripts/test_invoice.py --b2b
  python3 scripts/test_invoice.py --invoice-id ATH-INV-9999
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Local defaults for IDE runs (env / CLI override these)
# ---------------------------------------------------------------------------
CONFIG = {
    'base_url': 'http://localhost:8019',
    'db': 'athir_test',  # must match the DB where the module is installed
    # Paste token from: Athir → API Credentials → Generate Token
    'token': '8MWJwXpHWPi2pX-SamYqZal5VOTUyOjruTpwhUqf7uw',
}


def sample_b2c_payload(invoice_id: str = 'ATH-INV-FLAT-1001') -> dict:
    return {
        'invoice_id': invoice_id,
        'bill_type': 'B2C',
        'organization': 'ORG-1',
        'branch_id': 'BR-1',
        'branch_name': 'Main Branch',
        'clinic_id': 'CL-1',
        'clinic_name': 'Dental',
        'cashier_id': 'CA-1',
        'cashier_name': 'Cashier One',
        'mrn': 'MRN-100',
        'total_amount': 115.0,
        'services': [
            {
                'service_id': 'SVC-1',
                'service_name': 'Consultation',
                'service_group_id': 'SG-1',
                'service_group_name': 'OPD',
                'doctor_id': 'DOC-1',
                'doctor_name': 'Dr Smith',
                'price': 100.0,
                'discount_amount': 0.0,
                'net_price': 100.0,
                'tax_code_id': 'TAX-15',
                'insurance_net_without_vat': 0.0,
                'insurance_vat_amount': 0.0,
                'cash_net_without_vat': 100.0,
                'cash_vat_amount': 15.0,
                'transaction_created_at': '2026-01-15T10:00:00',
            },
        ],
        'pay_methods': [
            {'pay_method_id': 'CASH', 'amount': 115.0},
        ],
    }


def sample_b2b_payload(invoice_id: str = 'ATH-INV-FLAT-2001') -> dict:
    payload = sample_b2c_payload(invoice_id=invoice_id)
    payload['bill_type'] = 'B2B'
    payload.pop('mrn', None)
    payload['insurance_company_id'] = 'INS-1'
    payload['insurance_company_name'] = 'Bupa'
    return payload


def post_invoice(
    base_url: str,
    token: str,
    payload: dict,
    database: str | None = None,
) -> tuple[int, str]:
    url = base_url.rstrip('/') + '/api/athir/v1/invoices'
    body = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token,
    }
    # Odoo multi-DB: without this you get
    # "No database is selected and the requested URL was not found..."
    if database:
        headers['X-Odoo-Database'] = database
    req = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode('utf-8', errors='replace')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Post a sample Athir invoice')
    parser.add_argument(
        '--base-url',
        default=os.environ.get('ATHIR_BASE_URL', CONFIG['base_url']),
        help='Odoo base URL',
    )
    parser.add_argument(
        '--token',
        default=os.environ.get('ATHIR_TOKEN', CONFIG['token']),
        help='API token (CONFIG/ATHIR_TOKEN/--token)',
    )
    parser.add_argument(
        '--db',
        default=os.environ.get('ATHIR_DB', CONFIG['db']),
        help='Odoo database name sent as X-Odoo-Database',
    )
    parser.add_argument('--b2b', action='store_true', help='Send B2B payload')
    parser.add_argument(
        '--invoice-id',
        default=None,
        help='Override invoice_id (use a new id for each successful create)',
    )
    parser.add_argument(
        '--print-payload',
        action='store_true',
        help='Print JSON payload and exit without calling the API',
    )
    args = parser.parse_args(argv)

    if args.b2b:
        invoice_id = args.invoice_id or 'ATH-INV-FLAT-2001'
        payload = sample_b2b_payload(invoice_id=invoice_id)
    else:
        invoice_id = args.invoice_id or 'ATH-INV-FLAT-1001'
        payload = sample_b2c_payload(invoice_id=invoice_id)

    if args.print_payload:
        print(json.dumps(payload, indent=2))
        return 0

    if not args.token:
        print(
            'Missing token. Set ATHIR_TOKEN or pass --token '
            '(Athir → API Credentials → Generate Token).',
            file=sys.stderr,
        )
        return 2

    if not args.db:
        print(
            'Warning: no --db / ATHIR_DB set. Multi-DB Odoo servers return 404 '
            'without X-Odoo-Database.',
            file=sys.stderr,
        )

    status, text = post_invoice(
        args.base_url,
        args.token,
        payload,
        database=args.db or None,
    )
    try:
        parsed = json.loads(text)
        print(status)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print(status)
        print(text)

    return 0 if 200 <= status < 300 else 1


if __name__ == '__main__':
    raise SystemExit(main())

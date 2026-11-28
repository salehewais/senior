import json
import logging
import uuid
from decimal import Decimal

from odoo.addons.bh_athir_integration.adapters.athir_invoice_adapter import (
    AthirInvoiceAdapter,
    _payload_hash,
)

_logger = logging.getLogger(__name__)
from odoo.addons.bh_athir_integration.domain.exceptions import (
    AthirIntegrationError,
    IdempotencyConflictError,
)
from odoo.addons.bh_athir_integration.domain.validators import validate_canonical_invoice
from odoo.addons.bh_athir_integration.gateways.accounting_gateway import AccountingGateway
from odoo.addons.bh_athir_integration.gateways.product_gateway import ProductGateway
from odoo.addons.bh_athir_integration.mappers.customer_mapper import CustomerMapper
from odoo.addons.bh_athir_integration.mappers.organization_mapper import OrganizationMapper
from odoo.addons.bh_athir_integration.mappers.payment_mapper import PaymentMapper
from odoo.addons.bh_athir_integration.mappers.product_mapper import ProductMapper
from odoo.addons.bh_athir_integration.mappers.tax_mapper import TaxMapper


class InvoiceProcessingStrategy:
    OPERATION = 'invoice'
    SOURCE_SYSTEM = 'athir'

    def __init__(self, env):
        self.env = env
        self.adapter = AthirInvoiceAdapter()
        self.org_mapper = OrganizationMapper(env)
        self.customer_mapper = CustomerMapper(env)
        self.product_mapper = ProductMapper(env)
        self.tax_mapper = TaxMapper(env)
        self.payment_mapper = PaymentMapper(env)
        self.product_gateway = ProductGateway(env)
        self.accounting = AccountingGateway(env)
        self.Processed = env['athir.processed.document']
        self.Log = env['athir.integration.log']

    def process(self, payload, credential=None, correlation_id=None):
        correlation_id = correlation_id or str(uuid.uuid4())
        log = self._create_log(
            status='received',
            correlation_id=correlation_id,
            credential=credential,
            payload=payload,
        )
        existing_doc = self.env['athir.processed.document'].browse()
        try:
            canonical = self.adapter.adapt(payload)
            log.write({
                'external_id': canonical.external_invoice_id,
                'payload_hash': canonical.source_payload_hash,
                'status': 'processing',
            })

            fallback_company = (
                credential.company_id
                if credential and credential.company_id
                else self.env.company
            )
            tolerance = Decimal(str(fallback_company.athir_financial_tolerance or 0.01))
            validate_canonical_invoice(canonical, tolerance=tolerance)

            idem = self.Processed.begin_or_replay(
                self.SOURCE_SYSTEM,
                self.OPERATION,
                canonical.external_invoice_id,
                canonical.source_payload_hash,
            )
            existing_doc = idem['document']

            if idem['action'] == 'replay':
                move = idem['move']
                log.write({
                    'status': 'duplicate',
                    'move_id': move.id if move else False,
                    'company_id': move.company_id.id if move else False,
                })
                return {
                    'success': True,
                    'status': 'already_processed',
                    'invoice_id': canonical.external_invoice_id,
                    'odoo_move_id': move.id if move else False,
                    'odoo_move_name': move.name if move else False,
                    'correlation_id': correlation_id,
                }

            if idem['action'] == 'conflict':
                raise IdempotencyConflictError(
                    'invoice_id already processed with a different payload',
                    details={'invoice_id': canonical.external_invoice_id},
                )

            resolved = self._resolve_all(canonical, fallback_company)
            # Savepoint so FINANCIAL_DISCREPANCY / create failures leave no draft move.
            with self.env.cr.savepoint():
                move = self.accounting.create_draft_customer_invoice(
                    canonical, resolved,
                )
                methods = [
                    self.payment_mapper.resolve(
                        payment.pay_method_id,
                        company=resolved['company'],
                        required=False,
                    )
                    for payment in canonical.payments
                ]
                self.accounting.create_payment_traces(
                    move, canonical.payments, methods, log=log,
                )

                self.Processed.mark_result(
                    self.SOURCE_SYSTEM,
                    self.OPERATION,
                    canonical.external_invoice_id,
                    canonical.source_payload_hash,
                    'succeeded',
                    move=move,
                    company=resolved['company'],
                    existing=existing_doc,
                )
                log.write({
                    'status': 'succeeded',
                    'move_id': move.id,
                    'company_id': resolved['company'].id,
                })
            return {
                'success': True,
                'status': 'created',
                'invoice_id': canonical.external_invoice_id,
                'odoo_move_id': move.id,
                'odoo_move_name': move.name,
                'move_state': move.state,
                'correlation_id': correlation_id,
            }
        except AthirIntegrationError as exc:
            self._fail(log, existing_doc, payload, exc)
            raise
        except Exception as exc:
            wrapped = AthirIntegrationError(str(exc), code='INTERNAL_ERROR')
            wrapped.http_status = 500
            self._fail(log, existing_doc, payload, wrapped)
            raise wrapped from exc

    def _resolve_all(self, canonical, fallback_company):
        company = self.org_mapper.resolve(
            canonical.organization,
            fallback_company=fallback_company,
        )
        partner = self.customer_mapper.resolve(canonical, company=company)
        lines = []
        for line in canonical.lines:
            product = self.product_gateway.as_product_product(
                self.product_mapper.resolve(line.service_id, company=company)
            )
            tax = self.tax_mapper.resolve(line.tax_code_id, company=company)
            lines.append({'product': product, 'tax': tax})
        return {
            'company': company,
            'partner': partner,
            'lines': lines,
        }

    def _create_log(self, status, correlation_id, credential, payload):
        vals = {
            'name': correlation_id,
            'operation': self.OPERATION,
            'status': status,
            'correlation_id': correlation_id,
            'credential_id': credential.id if credential else False,
        }
        company = (
            credential.company_id
            if credential and credential.company_id
            else self.env.company
        )
        if company.athir_store_raw_payload and isinstance(payload, dict):
            vals['raw_payload'] = json.dumps(payload, default=str)
        return self.Log.sudo().create(vals)

    def _fail(self, log, existing_doc, payload, exc):
        external_id = False
        payload_hash = False
        if isinstance(payload, dict):
            if payload.get('invoice_id'):
                external_id = str(payload['invoice_id'])
            try:
                payload_hash = _payload_hash(payload)
            except Exception:
                payload_hash = False

        code = getattr(exc, 'code', 'ERROR')
        status = 'failed'
        if (
            code.startswith('UNRESOLVED_')
            or code in {
                'AMBIGUOUS_MAPPING',
                'VALIDATION_ERROR',
                'MISSING_INVOICE_ID',
                'INVALID_BILL_TYPE',
                'MISSING_SERVICES',
                'MISSING_FIELD',
                'INVALID_TYPE',
                'INVALID_DATE',
                'INVALID_PRICE',
                'INVALID_DISCOUNT',
                'MISSING_TAX_CODE',
                'MISSING_SERVICE',
                'MISSING_MRN',
                'MISSING_INSURANCE',
                'MISSING_ORGANIZATION',
                'MISSING_BRANCH',
                'MISSING_CLINIC',
                'INCONSISTENT_LINE_DATES',
                'FINANCIAL_DISCREPANCY',
                'IDEMPOTENCY_CONFLICT',
                'REJECTED',
            }
        ):
            status = 'rejected'

        # Persist failure in its own savepoint so retries can proceed.
        if external_id and payload_hash:
            try:
                with self.env.cr.savepoint():
                    self.Processed.mark_result(
                        self.SOURCE_SYSTEM,
                        self.OPERATION,
                        external_id,
                        payload_hash,
                        'failed',
                        error_code=code,
                        error_message=str(exc),
                        existing=existing_doc if existing_doc else None,
                    )
            except Exception:
                _logger.exception(
                    'Failed to persist athir.processed.document for %s', external_id,
                )

        try:
            with self.env.cr.savepoint():
                log.sudo().write({
                    'status': status,
                    'external_id': external_id or log.external_id,
                    'payload_hash': payload_hash or log.payload_hash,
                    'error_code': code,
                    'error_message': str(exc),
                })
        except Exception:
            _logger.exception('Failed to update athir.integration.log %s', log.id)

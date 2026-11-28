import json
import logging
import uuid

from odoo import http
from odoo.http import request

from odoo.addons.bh_athir_integration.application.integration_facade import (
    IntegrationFacade,
)
from odoo.addons.bh_athir_integration.domain.exceptions import (
    AthirIntegrationError,
    AuthenticationError,
)

_logger = logging.getLogger(__name__)


class AthirController(http.Controller):

    def _error_envelope(self, exc, correlation_id=None):
        return {
            'success': False,
            'error': {
                'code': getattr(exc, 'code', 'ERROR'),
                'message': str(exc),
                'details': getattr(exc, 'details', {}) or {},
            },
            'correlation_id': correlation_id,
        }

    def _authenticate(self):
        Credential = request.env['athir.api.credential']
        token = Credential.extract_token_from_headers(request.httprequest.headers)
        if not token:
            raise AuthenticationError('Missing Authorization Bearer token or X-API-Key')
        credential = Credential.authenticate_token(token)
        if not credential:
            raise AuthenticationError('Invalid or revoked API credentials')
        return credential

    def _parse_json_body(self):
        raw = request.httprequest.get_data()
        if not raw:
            raise AthirIntegrationError('Empty request body', code='INVALID_PAYLOAD')
        try:
            return json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AthirIntegrationError(
                'Invalid JSON payload',
                code='INVALID_PAYLOAD',
            ) from exc

    def _handle(self, operation):
        correlation_id = (
            request.httprequest.headers.get('X-Correlation-Id')
            or str(uuid.uuid4())
        )
        try:
            credential = self._authenticate()
            env = credential.get_env_for_writes(request.env)
            payload = self._parse_json_body()
            facade = IntegrationFacade(env)
            result = facade.process(
                operation,
                payload,
                credential=credential,
                correlation_id=correlation_id,
            )
            return request.make_json_response(result, status=200)
        except AthirIntegrationError as exc:
            _logger.info(
                'Athir %s rejected/failed [%s]: %s',
                operation,
                getattr(exc, 'code', 'ERROR'),
                exc,
            )
            return request.make_json_response(
                self._error_envelope(exc, correlation_id=correlation_id),
                status=getattr(exc, 'http_status', 400),
            )
        except Exception:
            _logger.exception('Athir %s unexpected error', operation)
            exc = AthirIntegrationError('Internal server error', code='INTERNAL_ERROR')
            exc.http_status = 500
            return request.make_json_response(
                self._error_envelope(exc, correlation_id=correlation_id),
                status=500,
            )

    @http.route(
        '/api/athir/v1/invoices',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False,
    )
    def create_invoice(self, **kwargs):
        return self._handle('invoice')

    @http.route(
        '/api/athir/v1/refunds',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False,
    )
    def create_refund(self, **kwargs):
        return self._handle('refund')

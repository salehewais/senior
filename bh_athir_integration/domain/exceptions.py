class AthirIntegrationError(Exception):
    """Base domain error with stable machine-readable code."""

    code = 'ATHIR_ERROR'
    http_status = 400

    def __init__(self, message=None, *, code=None, details=None):
        self.message = message or self.code
        if code:
            self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AthirIntegrationError):
    code = 'UNAUTHORIZED'
    http_status = 401


class ValidationError(AthirIntegrationError):
    code = 'VALIDATION_ERROR'
    http_status = 422


class UnsupportedContractError(AthirIntegrationError):
    code = 'UNSUPPORTED_CONTRACT'
    http_status = 501


class UnresolvedMappingError(AthirIntegrationError):
    code = 'UNRESOLVED_MAPPING'
    http_status = 422


class AmbiguousMappingError(AthirIntegrationError):
    code = 'AMBIGUOUS_MAPPING'
    http_status = 422


class IdempotencyConflictError(AthirIntegrationError):
    code = 'IDEMPOTENCY_CONFLICT'
    http_status = 409


class FinancialDiscrepancyError(AthirIntegrationError):
    code = 'FINANCIAL_DISCREPANCY'
    http_status = 422


class RejectedError(AthirIntegrationError):
    code = 'REJECTED'
    http_status = 422

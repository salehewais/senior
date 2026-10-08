"""Domain failures. Presentation maps these to HTTP. It does not reinterpret them."""


class DomainError(Exception):
    """A business rule rejected the request. The message is safe to show a caller."""

    code = "DOMAIN_ERROR"

    def __init__(self, message: str, *, details: list[dict[str, str]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []


class DomainValidationError(DomainError):
    code = "VALIDATION_ERROR"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class InvalidStateTransition(DomainError):
    code = "INVALID_STATE_TRANSITION"


class ConflictError(DomainError):
    code = "CONFLICT"


class ConcurrentModificationError(ConflictError):
    code = "CONCURRENT_MODIFICATION"


class ProductNotOrderableError(ConflictError):
    code = "PRODUCT_NOT_ORDERABLE"


class UnauthenticatedError(DomainError):
    """Missing or invalid credentials. The message must not say which check failed."""

    code = "UNAUTHENTICATED"


class ForbiddenError(DomainError):
    """The caller is authenticated and is not allowed to do this."""

    code = "FORBIDDEN"


class DependencyUnavailableError(DomainError):
    code = "DEPENDENCY_UNAVAILABLE"

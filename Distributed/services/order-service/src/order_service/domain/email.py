"""Email is an identifier. Store one normalized form so lookups do not depend on case."""

from order_service.domain.exceptions import DomainValidationError


def normalize_email(value: str) -> str:
    if not isinstance(value, str):
        raise DomainValidationError("email must be text.")
    cleaned = value.strip().lower()
    if not cleaned:
        raise DomainValidationError("email is required.")
    if len(cleaned) > 254:
        raise DomainValidationError("email cannot be longer than 254 characters.")
    if "@" not in cleaned or cleaned.startswith("@") or cleaned.endswith("@"):
        raise DomainValidationError("email must contain a local part and a domain.")
    return cleaned

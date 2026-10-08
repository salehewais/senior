"""Load the RS256 key pair from PEM text or from files outside git."""

from pathlib import Path

from order_service.infrastructure.settings import Settings


class IncompleteSigningKeys(RuntimeError):
    pass


def load_signing_keys(settings: Settings) -> tuple[str, str] | None:
    private = _pem_text(settings.jwt_private_key_pem) or _pem_file(settings.jwt_private_key_path)
    public = _pem_text(settings.jwt_public_key_pem) or _pem_file(settings.jwt_public_key_path)
    if not private and not public:
        return None
    if not private or not public:
        raise IncompleteSigningKeys(
            "Set both JWT private and public keys, either as PEM text or as file paths."
        )
    return private, public


def _pem_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    # Env files sometimes store newlines as the two characters \n.
    if "\\n" in text and "\n" not in text:
        text = text.replace("\\n", "\n")
    return text


def _pem_file(path: str) -> str:
    cleaned = path.strip()
    if not cleaned:
        return ""
    file_path = Path(cleaned)
    if not file_path.is_file():
        raise IncompleteSigningKeys(f"JWT key file was not found: {cleaned}")
    return file_path.read_text(encoding="utf-8")

from pathlib import Path

import pytest

from order_service.infrastructure.security.keys import IncompleteSigningKeys, load_signing_keys
from order_service.infrastructure.settings import Settings


def _settings(**overrides: str) -> Settings:
    values = {
        "jwt_private_key_pem": "",
        "jwt_public_key_pem": "",
        "jwt_private_key_path": "",
        "jwt_public_key_path": "",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_missing_keys_leave_signing_unconfigured() -> None:
    assert load_signing_keys(_settings()) is None


def test_pem_text_is_preferred_and_escaped_newlines_are_restored() -> None:
    private, public = load_signing_keys(
        _settings(
            jwt_private_key_pem="-----BEGIN PRIVATE-----\\nline\\n-----END PRIVATE-----",
            jwt_public_key_pem="-----BEGIN PUBLIC-----\nline\n-----END PUBLIC-----",
            jwt_private_key_path="/does/not/matter.pem",
            jwt_public_key_path="/does/not/matter.pem",
        )
    )
    assert private == "-----BEGIN PRIVATE-----\nline\n-----END PRIVATE-----"
    assert "BEGIN PUBLIC" in public


def test_paths_are_read_when_pem_text_is_empty(tmp_path: Path) -> None:
    private_path = tmp_path / "jwt_private.pem"
    public_path = tmp_path / "jwt_public.pem"
    private_path.write_text("private-pem", encoding="utf-8")
    public_path.write_text("public-pem", encoding="utf-8")
    loaded = load_signing_keys(
        _settings(
            jwt_private_key_path=str(private_path),
            jwt_public_key_path=str(public_path),
        )
    )
    assert loaded == ("private-pem", "public-pem")


def test_one_key_without_the_other_fails_closed() -> None:
    with pytest.raises(IncompleteSigningKeys):
        load_signing_keys(_settings(jwt_private_key_pem="only-private"))

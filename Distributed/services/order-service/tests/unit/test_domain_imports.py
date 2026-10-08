"""The domain package stays free of the web framework, the database, and the broker."""

import ast
from pathlib import Path

_DOMAIN = Path(__file__).resolve().parents[2] / "src" / "order_service" / "domain"
_FORBIDDEN = {"aio_pika", "pika", "fastapi", "sqlalchemy"}


def test_domain_package_has_no_framework_or_broker_imports() -> None:
    offenders: list[str] = []
    for path in sorted(_DOMAIN.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            for module in modules:
                root = module.split(".", 1)[0]
                if root in _FORBIDDEN:
                    offenders.append(f"{path.name}: {module}")
    assert offenders == []

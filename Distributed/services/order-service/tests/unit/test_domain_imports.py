"""Domain and application stay free of the web framework, the database, and the broker.

Application may depend on the domain. It does not import infrastructure, presentation,
or the observability package. Callers pass a trace carrier in when they have one.
"""

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2] / "src" / "order_service"
_DOMAIN = _ROOT / "domain"
_APPLICATION = _ROOT / "application"
_FORBIDDEN = {"aio_pika", "pika", "fastapi", "sqlalchemy", "redis", "opentelemetry"}
_APPLICATION_PREFIXES = (
    "order_service.infrastructure",
    "order_service.presentation",
    "order_service.observability",
)


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_domain_package_has_no_framework_or_broker_imports() -> None:
    offenders = _offenders(_DOMAIN, prefixes=())
    assert offenders == []


def test_application_package_has_no_framework_broker_or_adapter_imports() -> None:
    offenders = _offenders(_APPLICATION, prefixes=_APPLICATION_PREFIXES)
    assert offenders == []


def _offenders(package: Path, *, prefixes: tuple[str, ...]) -> list[str]:
    offenders: list[str] = []
    for path in sorted(package.rglob("*.py")):
        for module in _imported_modules(path):
            root = module.split(".", 1)[0]
            if root in _FORBIDDEN or module.startswith(prefixes):
                offenders.append(f"{path.relative_to(package)}: {module}")
    return offenders

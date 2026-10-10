"""Django TestCase modules live here. The mark is applied so a plain pytest function can use the database."""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config, items) -> None:
    del config
    for item in items:
        if "tests/django/" in str(item.path):
            item.add_marker(pytest.mark.django_db)

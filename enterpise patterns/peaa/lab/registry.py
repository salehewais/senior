"""Demo name → callable. تسجيل أسماء المعامل."""

from __future__ import annotations

from collections.abc import Callable

DEMOS: dict[str, Callable[[], None]] = {}


def register(name: str) -> Callable:
    def deco(fn: Callable[[], None]) -> Callable[[], None]:
        if name in DEMOS:
            raise ValueError(f"duplicate demo {name}")
        DEMOS[name] = fn
        return fn

    return deco

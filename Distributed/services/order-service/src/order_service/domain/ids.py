"""UUID wrappers so raw strings do not wander through the domain."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass


def uuid7() -> uuid.UUID:
    """UUID version 7 (time-ordered). The stdlib adds this in 3.14; 3.12 needs it here.

    Layout follows RFC 9562: 48-bit unix milliseconds, version nibble 7, 12 random bits,
    the RFC variant, then 62 random bits.
    """

    unix_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    value = (unix_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return uuid.UUID(int=value)


def _parse(value: uuid.UUID | str) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("expected a UUID") from exc


@dataclass(frozen=True, slots=True)
class OrderId:
    value: uuid.UUID

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _parse(self.value))

    @classmethod
    def generate(cls) -> OrderId:
        return cls(uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ProductId:
    value: uuid.UUID

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _parse(self.value))

    @classmethod
    def generate(cls) -> ProductId:
        return cls(uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class AccountId:
    value: uuid.UUID

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _parse(self.value))

    @classmethod
    def generate(cls) -> AccountId:
        return cls(uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class CustomerId:
    value: uuid.UUID

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _parse(self.value))

    @classmethod
    def generate(cls) -> CustomerId:
        return cls(uuid7())

    def __str__(self) -> str:
        return str(self.value)

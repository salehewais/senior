"""UUID version 7. Python 3.12 does not ship it; 3.14 will."""

from __future__ import annotations

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """Time-ordered UUID. Layout follows RFC 9562."""

    unix_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    value = (unix_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return uuid.UUID(int=value)

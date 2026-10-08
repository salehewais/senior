"""Constant-time compare for the internal fulfillment header.

Hashing both sides first keeps the compare from returning early on length.
"""

import hashlib
import hmac


def service_token_matches(presented: str, expected: str) -> bool:
    if not expected or not presented:
        return False
    presented_digest = hashlib.sha256(presented.encode("utf-8")).digest()
    expected_digest = hashlib.sha256(expected.encode("utf-8")).digest()
    return hmac.compare_digest(presented_digest, expected_digest)

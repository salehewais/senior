"""Lifetimes from the security design. Access tokens are not stored. Refresh hashes are."""

from datetime import timedelta

ACCESS_TOKEN_TTL = timedelta(minutes=15)
ACCESS_TOKEN_TTL_SECONDS = int(ACCESS_TOKEN_TTL.total_seconds())
REFRESH_TOKEN_TTL = timedelta(days=7)

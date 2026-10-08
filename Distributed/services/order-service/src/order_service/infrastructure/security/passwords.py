"""argon2id password hashes. The plaintext never leaves the hasher."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from argon2.low_level import Type


class Argon2PasswordHasher:
    def __init__(self, *, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4) -> None:
        self._hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            type=Type.ID,
        )
        # A real hash so an unknown email still pays for a verify.
        self._dummy = self._hasher.hash("not-a-user-password")

    def hash_password(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def verify_dummy(self, password: str) -> None:
        self.verify_password(password, self._dummy)

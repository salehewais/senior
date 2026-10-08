"""Create an admin or manager from the environment. Public register cannot do this.

Run: python -m order_service.infrastructure.seed_staff

The account is inserted only when both the email and password variables are set,
and only when that email is not already an account. The password is not printed.
"""

from __future__ import annotations

import os

from order_service.application.clock import SystemClock
from order_service.application.use_cases.auth import CreateStaffAccount
from order_service.domain.exceptions import ConflictError, DomainError
from order_service.domain.roles import Role
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork
from order_service.infrastructure.security.passwords import Argon2PasswordHasher
from order_service.infrastructure.settings import get_settings

_PAIRS = (
    ("SEED_ADMIN_EMAIL", "SEED_ADMIN_PASSWORD", Role.ADMIN),
    ("SEED_MANAGER_EMAIL", "SEED_MANAGER_PASSWORD", Role.MANAGER),
)


def main() -> None:
    settings = get_settings()
    engine = make_engine(settings)
    sessions = make_session_factory(engine)
    passwords = Argon2PasswordHasher()
    clock = SystemClock()
    try:
        for email_var, password_var, role in _PAIRS:
            email = os.environ.get(email_var, "").strip()
            password = os.environ.get(password_var, "")
            if not email and not password:
                continue
            if not email or not password:
                print(f"{email_var} and {password_var} must both be set to seed a {role.value}.")
                continue
            uow = SqlUnitOfWork(sessions())
            try:
                account_id = CreateStaffAccount(clock, passwords).execute(
                    uow,
                    email=email,
                    password=password,
                    role=role,
                )
            except ConflictError:
                uow.close()
                print(f"{role.value} already exists for that email. Skipped.")
                continue
            except DomainError as exc:
                uow.close()
                print(exc.message)
                continue
            uow.close()
            print(f"Created {role.value} account {account_id}.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

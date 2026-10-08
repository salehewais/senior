from sqlalchemy.orm import Session

from order_service.application.unit_of_work import UnitOfWork
from order_service.infrastructure.database.repositories import (
    SqlAccountRepository,
    SqlCustomerRepository,
    SqlOrderRepository,
    SqlProductRepository,
    SqlRefreshTokenRepository,
)


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        self._session = session
        self._committed = False
        self.products = SqlProductRepository(session)
        self.customers = SqlCustomerRepository(session)
        self.orders = SqlOrderRepository(session)
        self.accounts = SqlAccountRepository(session)
        self.refresh_tokens = SqlRefreshTokenRepository(session)

    def commit(self) -> None:
        self._session.commit()
        self._committed = True

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        if not self._committed:
            self._session.rollback()
        self._session.close()

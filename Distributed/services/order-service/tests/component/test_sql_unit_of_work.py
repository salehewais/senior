"""SqlUnitOfWork translates constraint failures before they reach HTTP."""

from sqlalchemy.exc import IntegrityError, OperationalError

from order_service.domain.exceptions import ConflictError, DependencyUnavailableError
from order_service.infrastructure.database.unit_of_work import SqlUnitOfWork


class _Session:
    def __init__(self, *, fail: str) -> None:
        self.fail = fail
        self.rolled_back = False
        self.closed = False

    def flush(self, objects=None) -> None:
        del objects
        if self.fail == "flush":
            raise IntegrityError("INSERT", {}, Exception("duplicate key"))

    def commit(self) -> None:
        if self.fail == "commit":
            raise IntegrityError("COMMIT", {}, Exception("duplicate key"))

    def get(self, entity, ident):
        del entity, ident
        if self.fail == "get":
            raise OperationalError("SELECT", {}, Exception("connection refused"))
        return None

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True

    def add(self, row: object) -> None:
        del row


def test_flush_integrity_error_is_a_domain_conflict() -> None:
    session = _Session(fail="flush")
    uow = SqlUnitOfWork(session)  # type: ignore[arg-type]
    try:
        session.flush()
    except ConflictError as exc:
        assert exc.code == "CONFLICT"
        assert exc.message == "The request conflicts with data already stored."
    else:
        raise AssertionError("flush did not raise ConflictError")
    uow.close()
    assert session.rolled_back is True
    assert session.closed is True


def test_query_operational_error_is_dependency_unavailable() -> None:
    session = _Session(fail="get")
    SqlUnitOfWork(session)  # type: ignore[arg-type]
    try:
        session.get(object, "id")
    except DependencyUnavailableError as exc:
        assert exc.code == "DEPENDENCY_UNAVAILABLE"
        assert exc.message == "The order database is unavailable."
    else:
        raise AssertionError("get did not raise DependencyUnavailableError")


def test_commit_integrity_error_is_a_domain_conflict() -> None:
    session = _Session(fail="commit")
    uow = SqlUnitOfWork(session)  # type: ignore[arg-type]
    try:
        uow.commit()
    except ConflictError as exc:
        assert exc.code == "CONFLICT"
    else:
        raise AssertionError("commit did not raise ConflictError")
    assert uow._committed is False

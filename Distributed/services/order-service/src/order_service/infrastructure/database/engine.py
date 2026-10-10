from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from order_service.infrastructure.settings import Settings


def make_engine(settings: Settings) -> Engine:
    timeout = settings.db_statement_timeout_ms
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_timeout=settings.db_connect_timeout_seconds,
        connect_args={
            "connect_timeout": settings.db_connect_timeout_seconds,
            "options": f"-c statement_timeout={timeout}",
        },
    )


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def database_ready(engine: Engine) -> bool:
    """True when order_db accepts a connection. Operational failures are not ready."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        return False
    return True

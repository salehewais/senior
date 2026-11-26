import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Uses your local Postgres role via Unix socket (peer auth).
# Override anytime with: export DATABASE_URL="postgresql+psycopg://..."
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://saleh@/mydb?host=/var/run/postgresql",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
Base = declarative_base()

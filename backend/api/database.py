"""
Database setup for ChainTrace (Person E — Phase 1).

Phase 1 uses SQLite. Do not switch to PostgreSQL here — that migration
belongs to a later phase per the team plan (Person F owns infra).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./chaintrace.db"

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling (multiple requests may share the connection pool).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

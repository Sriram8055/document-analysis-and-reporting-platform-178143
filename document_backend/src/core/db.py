import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Ensure SQLite enforces foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):  # pragma: no cover
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        # Not all drivers support PRAGMA; safe to ignore
        pass


# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Return database URL from env var DATABASE_URL or default to local SQLite file.

    Env:
      - DATABASE_URL: full SQLAlchemy URL (e.g., sqlite:///./data/app.db)
    Fallback:
      - Uses STORAGE_DIR (default ./data) to build sqlite path.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    storage_dir = os.getenv("STORAGE_DIR", "./data")
    os.makedirs(storage_dir, exist_ok=True)
    # Use absolute path to avoid working dir ambiguity
    sqlite_path = os.path.abspath(os.path.join(storage_dir, "app.db"))
    # For Windows paths with spaces
    sqlite_path_escaped = quote_plus(sqlite_path)
    return f"sqlite:///{sqlite_path_escaped}"


DATABASE_URL = get_database_url()

# For SQLite, need check_same_thread=False when used with FastAPI threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# Dependency/utility for getting DB sessions
@contextmanager
# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Context manager yielding a SQLAlchemy session, with automatic close/rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create database tables if they don't exist."""
    # Import models to ensure they are registered with Base.metadata
    from src.models import job, file, result, progress  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Convenience CRUD helpers (minimal, for unblocking API work)
# PUBLIC_INTERFACE
def create_row(db: Session, instance) -> object:
    """Add and commit a new ORM instance."""
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


# PUBLIC_INTERFACE
def get_by_id(db: Session, model, id_) -> Optional[object]:
    """Get a row by primary key id."""
    return db.get(model, id_)


# PUBLIC_INTERFACE
def update_fields(db: Session, instance, **fields) -> object:
    """Update fields on an ORM instance and persist."""
    for k, v in fields.items():
        setattr(instance, k, v)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


# PUBLIC_INTERFACE
def now_utc() -> datetime:
    """Return current UTC timestamp without tzinfo (compatible with SQLite)."""
    return datetime.utcnow()

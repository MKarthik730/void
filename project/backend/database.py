"""
VOID — Database Connection (Lazy)
Connects to PostgreSQL + pgvector on first use, not at import time.
This prevents app crash when PostgreSQL is down or credentials are wrong.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError
from config import DATABASE_URL
import logging

# ── Engine (created lazily) ───────────────────────────────────────────────────
_engine = None
_SessionLocal = None
SessionLocal = None  # Public alias — may be None if DB is unavailable
Base = declarative_base()
_db_available = False
_pgvector_available = False


def _get_engine():
    """Get or create the database engine. Returns None if DB is unavailable."""
    global _engine, _SessionLocal, _db_available, _pgvector_available

    # If we already have a working engine, return it
    if _engine is not None and _db_available:
        return _engine

    # If engine was previously created but failed, reset and retry
    if _engine is not None and not _db_available:
        _engine = None
        _SessionLocal = None

    try:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        # Test connection
        with _engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("SELECT 1"))

        _db_available = True
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        # Update public alias so downstream imports work
        globals()["SessionLocal"] = _SessionLocal
        print(f"[VOID DB] Connected to PostgreSQL at {DATABASE_URL[:50]}...")

        # Enable pgvector extension (optional)
        try:
            with _engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            _pgvector_available = True
        except Exception as e:
            print(f"[VOID DB] pgvector not available (vector search disabled): {e}")
            _pgvector_available = False

        # Create tables
        try:
            Base.metadata.create_all(bind=_engine)
            print("[VOID DB] Tables created/verified")
        except Exception as e:
            print(f"[VOID DB] Table creation failed: {e}")

        return _engine

    except OperationalError as e:
        print(f"[VOID DB] PostgreSQL not available: {e}")
        print("[VOID DB] Falling back — services without DB dependency will still work")
        _engine = None
        _SessionLocal = None
        _db_available = False
        return None


def get_db():
    """Get database session. Yields None if DB is unavailable."""
    global _SessionLocal

    if not _db_available:
        _get_engine()  # retry

    if _SessionLocal is None:
        yield None
        return

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables. Safe to call even if DB is down."""
    engine = _get_engine()
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"[VOID DB] init_db failed: {e}")


def is_db_available() -> bool:
    """Check if database is currently available."""
    global _db_available
    if not _db_available:
        _get_engine()  # retry
    return _db_available

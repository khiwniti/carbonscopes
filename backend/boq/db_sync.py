"""
Synchronous Database Session Management for BOQ Carbon Pipeline.

Provides synchronous SQLAlchemy session management for the carbon calculation
pipeline, which doesn't require async operations.

Note: This is a simplified version for the BOQ pipeline. The main async db.py
is used for the FastAPI application.
"""

import os
import logging
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)


def _get_sync_database_url() -> str:
    """
    Get synchronous PostgreSQL database URL.

    Returns:
        Database URL with psycopg2 driver (synchronous)
    """
    # Try to get from environment
    url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_POOLER_URL")

    if not url:
        raise RuntimeError("DATABASE_URL or DATABASE_POOLER_URL environment variable required")

    # Convert to synchronous psycopg2 driver
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql://")
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://")

    return url


# Global engine and session factory
_engine = None
_session_factory = None


def init_sync_db():
    """Initialize synchronous database engine and session factory."""
    global _engine, _session_factory

    if _engine is not None:
        return

    database_url = _get_sync_database_url()

    # Create engine with appropriate pool settings
    is_supavisor = "pooler.supabase.com" in database_url or ":6543" in database_url

    if is_supavisor:
        # Use NullPool for Supavisor
        _engine = create_engine(
            database_url,
            poolclass=NullPool,
            echo=False
        )
        logger.info("Initialized sync database with NullPool (Supavisor)")
    else:
        # Use QueuePool for direct connections
        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
        logger.info("Initialized sync database with QueuePool")

    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get a synchronous database session.

    Usage:
        with get_db() as db:
            result = db.query(Model).all()

    Yields:
        SQLAlchemy Session
    """
    if _session_factory is None:
        init_sync_db()

    session = _session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def close_sync_db():
    """Close the synchronous database engine."""
    global _engine, _session_factory

    if _engine:
        _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Closed sync database connection")

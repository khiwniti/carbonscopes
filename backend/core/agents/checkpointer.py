"""PostgreSQL checkpointer for LangGraph state persistence.

This module provides PostgreSQL-based state persistence for the multi-agent system,
enabling conversation memory and scenario forking across agent invocations.
"""

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import dict_row
import os
import logging

logger = logging.getLogger("agent.checkpointer")

# Global persistent checkpointer instance
_checkpointer: PostgresSaver | None = None
_connection = None


def initialize_checkpointer() -> PostgresSaver:
    """Initialize persistent PostgreSQL checkpointer for LangGraph state persistence.

    Creates a PostgresSaver instance with a persistent connection that stores
    LangGraph state in PostgreSQL. This should be called once during application startup.

    Skip initialization in LOCAL mode when DATABASE_URL contains a placeholder password
    to avoid tripping the Supabase circuit breaker during development.

    Environment Variables:
        DATABASE_URL: PostgreSQL connection string (default: postgresql://localhost/carbonscope)

    Returns:
        PostgresSaver instance configured for the database

    Raises:
        Exception: If database connection fails or setup encounters errors

    Example:
        >>> # During application startup
        >>> checkpointer = initialize_checkpointer()
        >>> graph = create_supervisor_graph(checkpointer)
        >>> # State persists across invocations with same thread_id
        >>> result = graph.invoke(state, config={"configurable": {"thread_id": "user-123"}})
    """
    global _checkpointer, _connection

    if _checkpointer is not None:
        logger.debug("Checkpointer already initialized, returning existing instance")
        return _checkpointer

    # Try CHECKPOINT_DATABASE_URL first (dedicated checkpoint store),
    # then DATABASE_URL, then SUPABASE_DATABASE_URL
    db_url = (
        os.getenv("CHECKPOINT_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DATABASE_URL")
    )

    if not db_url:
        raise ValueError(
            "No database URL configured. Set DATABASE_URL or SUPABASE_DATABASE_URL environment variable."
        )

    # In LOCAL mode, skip if password is still a placeholder — avoids hammering
    # Supabase's circuit breaker with bad credentials during development.
    from core.utils.config import config, EnvMode
    if config.ENV_MODE == EnvMode.LOCAL and ':***@' in db_url:
        logger.warning(
            "[CHECKPOINTER] Skipping init in LOCAL mode — DATABASE_URL has placeholder password (***). "
            "Set the real password in backend/.env to enable checkpointing."
        )
        return None

    # Extract host info for logging (hide credentials)
    db_host_info = db_url.split('@')[-1] if '@' in db_url else "unknown"
    logger.info(f"Initializing PostgreSQL checkpointer with database: {db_host_info}")

    try:
        # Create persistent connection
        # prepare_threshold=None disables server-side prepared statements,
        # avoiding "prepared statement already exists" errors on reconnect.
        _connection = Connection.connect(
            db_url,
            autocommit=True,
            prepare_threshold=None,
            row_factory=dict_row
        )

        # Create checkpointer with persistent connection
        _checkpointer = PostgresSaver(_connection)
        _checkpointer.setup()  # Creates checkpoints table if not exists

        logger.info("PostgreSQL checkpointer initialized successfully")
        return _checkpointer

    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL checkpointer: {e}")
        _checkpointer = None
        _connection = None
        raise


def get_checkpointer() -> PostgresSaver:
    """Get or initialize the global PostgreSQL checkpointer instance.

    Returns the existing checkpointer if already initialized, otherwise creates a new one.

    Returns:
        PostgresSaver instance configured for the database

    Raises:
        Exception: If database connection fails or setup encounters errors
    """
    global _checkpointer

    if _checkpointer is None:
        return initialize_checkpointer()

    return _checkpointer


def close_checkpointer() -> None:
    """Close the checkpointer and its database connection.

    This should be called during application shutdown.
    """
    global _checkpointer, _connection

    if _connection is not None:
        try:
            _connection.close()
            logger.info("Checkpointer connection closed")
        except Exception as e:
            logger.error(f"Error closing checkpointer connection: {e}")
        finally:
            _connection = None
            _checkpointer = None

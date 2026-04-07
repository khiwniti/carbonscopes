"""
Unit tests for core/services/supabase.py – specifically the race condition
fix in DBConnection.initialize() and the updated error-classification helpers.

All tests run without a real Supabase connection; the async client factory is
mocked at the module level.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db():
    """Return a *fresh* (uninitialized) DBConnection instance."""
    # Reset the singleton so each test gets a clean state
    from core.services import supabase as supa_mod
    supa_mod.DBConnection._instance = None
    return supa_mod.DBConnection()


# ---------------------------------------------------------------------------
# DBConnection.initialize() – race condition / lock correctness
# ---------------------------------------------------------------------------

class TestDBConnectionInitialize:
    """DBConnection.initialize() is idempotent and concurrency-safe."""

    @pytest.mark.asyncio
    async def test_initialize_sets_initialized_flag(self):
        db = _make_db()
        mock_client = MagicMock()
        mock_client.postgrest = MagicMock()
        mock_client.storage = MagicMock()

        with patch(
            "core.services.supabase.create_async_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            await db.initialize()

        assert db._initialized is True
        assert db._client is mock_client

    @pytest.mark.asyncio
    async def test_initialize_is_idempotent(self):
        """Calling initialize() twice must not create a second client."""
        db = _make_db()
        mock_client = MagicMock()
        mock_client.postgrest = MagicMock()
        mock_client.storage = MagicMock()

        call_count = 0

        async def fake_create(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            return mock_client

        with patch("core.services.supabase.create_async_client", side_effect=fake_create):
            await db.initialize()
            await db.initialize()  # second call must be a no-op

        assert call_count == 1, "create_async_client should be called exactly once"

    @pytest.mark.asyncio
    async def test_concurrent_initialize_calls_create_one_client(self):
        """
        Simulate the race condition that caused the circuit breaker:
        multiple coroutines calling initialize() concurrently should result
        in exactly ONE Supabase client being created, not N.
        """
        db = _make_db()
        mock_client = MagicMock()
        mock_client.postgrest = MagicMock()
        mock_client.storage = MagicMock()

        call_count = 0
        create_event = asyncio.Event()

        async def slow_create(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # simulate network latency
            return mock_client

        with patch("core.services.supabase.create_async_client", side_effect=slow_create):
            # Launch 10 concurrent initialize() calls (the old bug)
            await asyncio.gather(*[db.initialize() for _ in range(10)])

        assert call_count == 1, (
            f"Expected 1 client creation but got {call_count}. "
            "Concurrent calls are not protected by the lock."
        )
        assert db._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_raises_when_url_missing(self):
        db = _make_db()
        with patch("core.services.supabase.config") as mock_cfg:
            mock_cfg.SUPABASE_URL = ""
            mock_cfg.SUPABASE_SERVICE_ROLE_KEY = ""
            mock_cfg.SUPABASE_ANON_KEY = ""
            with pytest.raises(RuntimeError, match="SUPABASE_URL"):
                await db.initialize()

    @pytest.mark.asyncio
    async def test_reset_connection_clears_state(self):
        db = _make_db()
        mock_client = AsyncMock()
        mock_client.postgrest = MagicMock()
        mock_client.storage = MagicMock()

        with patch("core.services.supabase.create_async_client", return_value=mock_client):
            await db.initialize()

        assert db._initialized is True
        await db.reset_connection()
        assert db._initialized is False
        assert db._client is None


# ---------------------------------------------------------------------------
# Error classification helpers
# ---------------------------------------------------------------------------

class TestIsRecoverableConnectionError:
    """is_recoverable_connection_error now detects circuit-breaker errors."""

    def setup_method(self):
        from core.services.supabase import DBConnection
        self.fn = DBConnection.is_recoverable_connection_error

    def test_circuit_breaker_is_recoverable(self):
        assert self.fn(Exception("FATAL: Circuit breaker open")) is True

    def test_too_many_authentication_is_recoverable(self):
        assert self.fn(Exception("too many authentication errors")) is True

    def test_client_closed_is_recoverable(self):
        assert self.fn(Exception("client has been closed")) is True

    def test_cannot_send_closed_is_recoverable(self):
        assert self.fn(Exception("cannot send a request, as the client has been closed")) is True

    def test_route_not_found_is_recoverable(self):
        assert self.fn(Exception("route /v1/agents not found")) is True

    def test_generic_404_is_not_recoverable(self):
        # A genuine 404 from the DB (e.g. wrong table) is NOT recoverable
        assert self.fn(Exception("HTTP 404: table does not exist")) is False

    def test_auth_error_401_is_not_recoverable(self):
        assert self.fn(Exception("invalid JWT: 401 Unauthorized")) is False


class TestIsDbUnavailableError:
    """is_db_unavailable_error classifies service-level outages."""

    def setup_method(self):
        from core.services.supabase import DBConnection
        self.fn = DBConnection.is_db_unavailable_error

    def test_circuit_breaker(self):
        assert self.fn(Exception("Circuit breaker open: Too many authentication errors")) is True

    def test_connection_refused(self):
        assert self.fn(Exception("connection refused")) is True

    def test_too_many_connections(self):
        assert self.fn(Exception("too many connections")) is True

    def test_server_closed_connection(self):
        assert self.fn(Exception("server closed the connection")) is True

    def test_application_error_is_not_unavailable(self):
        assert self.fn(ValueError("invalid model name")) is False

    def test_json_decode_is_not_unavailable(self):
        assert self.fn(Exception("JSON decode error")) is False


# ---------------------------------------------------------------------------
# execute_with_reconnect
# ---------------------------------------------------------------------------

class TestExecuteWithReconnect:
    """execute_with_reconnect retries recoverable errors via force_reconnect."""

    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self):
        from core.services.supabase import execute_with_reconnect, DBConnection

        db = _make_db()
        db._initialized = True
        db._client = MagicMock()

        async def op(client):
            return "ok"

        result = await execute_with_reconnect(db, op)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_circuit_breaker_error(self):
        from core.services.supabase import execute_with_reconnect, DBConnection

        db = _make_db()
        db._initialized = True
        db._client = MagicMock()

        call_count = 0

        async def op(client):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("circuit breaker open")
            return "recovered"

        db.force_reconnect = AsyncMock()

        result = await execute_with_reconnect(db, op, max_retries=2)
        assert result == "recovered"
        db.force_reconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_after_max_retries_exceeded(self):
        from core.services.supabase import execute_with_reconnect

        db = _make_db()
        db._initialized = True
        db._client = MagicMock()
        db.force_reconnect = AsyncMock()

        async def always_fail(client):
            raise Exception("circuit breaker open")

        with pytest.raises(Exception, match="circuit breaker open"):
            await execute_with_reconnect(db, always_fail, max_retries=1)

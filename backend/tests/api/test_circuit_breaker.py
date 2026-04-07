"""
Unit tests for the app-level DB circuit breaker introduced in core/services/db.py.

These tests run entirely in memory with no real DB connections.  They verify:
- _is_db_unavailable correctly identifies circuit-breaker / connectivity errors
- _is_transient correctly covers all error patterns including the new ones
- _circuit_breaker_check raises when the breaker is open
- _maybe_trip_circuit_breaker opens the breaker on unavailability errors
- The breaker auto-recovers after the cooldown window
"""

import time
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers to import db module with a fresh state each test
# ---------------------------------------------------------------------------

def _fresh_db():
    """Re-import core.services.db so module-level state is reset."""
    import importlib
    import core.services.db as db_mod
    importlib.reload(db_mod)
    return db_mod


# ---------------------------------------------------------------------------
# _is_db_unavailable
# ---------------------------------------------------------------------------

class TestIsDbUnavailable:
    """core.services.db._is_db_unavailable correctly classifies errors."""

    @pytest.fixture(autouse=True)
    def _db(self):
        self.db = _fresh_db()

    def test_circuit_breaker_open(self):
        e = Exception("FATAL: Circuit breaker open: Too many authentication errors")
        assert self.db._is_db_unavailable(e) is True

    def test_too_many_authentication(self):
        e = Exception("too many authentication failures")
        assert self.db._is_db_unavailable(e) is True

    def test_connection_refused(self):
        e = Exception("connection refused to 57.182.231.186:6543")
        assert self.db._is_db_unavailable(e) is True

    def test_could_not_connect(self):
        e = Exception("could not connect to server: Connection refused")
        assert self.db._is_db_unavailable(e) is True

    def test_remaining_connection_slots(self):
        e = Exception("FATAL: remaining connection slots are reserved for non-replication superuser connections")
        assert self.db._is_db_unavailable(e) is True

    def test_too_many_connections(self):
        e = Exception("too many connections")
        assert self.db._is_db_unavailable(e) is True

    def test_server_closed_connection(self):
        e = Exception("server closed the connection unexpectedly")
        assert self.db._is_db_unavailable(e) is True

    def test_generic_error_is_not_unavailable(self):
        e = ValueError("some unrelated application error")
        assert self.db._is_db_unavailable(e) is False

    def test_syntax_error_is_not_unavailable(self):
        e = Exception("syntax error at or near SELECT")
        assert self.db._is_db_unavailable(e) is False

    def test_statement_timeout_is_not_unavailable(self):
        # Statement timeout is transient but NOT a full service outage
        e = Exception("canceling statement due to statement timeout")
        assert self.db._is_db_unavailable(e) is False


# ---------------------------------------------------------------------------
# _is_transient (existing + new patterns)
# ---------------------------------------------------------------------------

class TestIsTransient:
    """_is_transient covers all patterns including new circuit-breaker ones."""

    @pytest.fixture(autouse=True)
    def _db(self):
        self.db = _fresh_db()

    def test_circuit_breaker_is_transient(self):
        e = Exception("Circuit breaker open")
        assert self.db._is_transient(e) is True

    def test_too_many_authentication_is_transient(self):
        e = Exception("Too many authentication errors detected")
        assert self.db._is_transient(e) is True

    def test_connection_reset_is_transient(self):
        assert self.db._is_transient(Exception("connection reset by peer")) is True

    def test_connection_refused_is_transient(self):
        assert self.db._is_transient(Exception("connection refused")) is True

    def test_ssl_closed_is_transient(self):
        assert self.db._is_transient(Exception("ssl connection has been closed unexpectedly")) is True

    def test_too_many_connections_is_transient(self):
        assert self.db._is_transient(Exception("too many connections")) is True

    def test_statement_timeout_is_transient(self):
        assert self.db._is_transient(Exception("canceling statement due to statement timeout")) is True

    def test_permission_denied_is_not_transient(self):
        assert self.db._is_transient(Exception("permission denied for table users")) is False

    def test_unique_violation_is_not_transient(self):
        assert self.db._is_transient(Exception("duplicate key value violates unique constraint")) is False


# ---------------------------------------------------------------------------
# _circuit_breaker_check
# ---------------------------------------------------------------------------

class TestCircuitBreakerCheck:
    """_circuit_breaker_check raises when breaker is open, passes when closed."""

    @pytest.fixture(autouse=True)
    def _db(self):
        self.db = _fresh_db()

    def test_passes_when_breaker_closed(self):
        """Should not raise when _cb_open_until is 0 (default closed state)."""
        self.db._cb_open_until = 0.0
        self.db._circuit_breaker_check()  # must not raise

    def test_raises_when_breaker_open(self):
        """Should raise RuntimeError when breaker is still within cooldown."""
        self.db._cb_open_until = time.time() + 60  # open for 60 more seconds
        with pytest.raises(RuntimeError, match="circuit breaker"):
            self.db._circuit_breaker_check()

    def test_passes_after_cooldown_expired(self):
        """Should not raise once the cooldown timestamp has passed."""
        self.db._cb_open_until = time.time() - 1  # expired 1 second ago
        self.db._circuit_breaker_check()  # must not raise

    def test_error_message_contains_remaining_seconds(self):
        self.db._cb_open_until = time.time() + 30
        with pytest.raises(RuntimeError) as exc_info:
            self.db._circuit_breaker_check()
        assert "30" in str(exc_info.value) or "29" in str(exc_info.value)


# ---------------------------------------------------------------------------
# _maybe_trip_circuit_breaker
# ---------------------------------------------------------------------------

class TestMaybeTripCircuitBreaker:
    """_maybe_trip_circuit_breaker opens the breaker on DB-unavailable errors."""

    @pytest.fixture(autouse=True)
    def _db(self):
        self.db = _fresh_db()

    def test_trips_on_circuit_breaker_error(self):
        before = time.time()
        self.db._maybe_trip_circuit_breaker(
            Exception("FATAL: Circuit breaker open: Too many authentication errors")
        )
        assert self.db._cb_open_until > before

    def test_trips_on_connection_refused(self):
        self.db._maybe_trip_circuit_breaker(Exception("connection refused"))
        assert self.db._cb_open_until > time.time() - 1

    def test_does_not_trip_on_generic_error(self):
        self.db._cb_open_until = 0.0
        self.db._maybe_trip_circuit_breaker(ValueError("some unrelated error"))
        assert self.db._cb_open_until == 0.0

    def test_does_not_trip_on_statement_timeout(self):
        self.db._cb_open_until = 0.0
        self.db._maybe_trip_circuit_breaker(
            Exception("canceling statement due to statement timeout")
        )
        assert self.db._cb_open_until == 0.0

    def test_cooldown_uses_db_cb_cooldown_seconds_env(self, monkeypatch):
        monkeypatch.setenv("DB_CB_COOLDOWN_SECONDS", "5")
        db = _fresh_db()
        before = time.time()
        db._maybe_trip_circuit_breaker(Exception("circuit breaker open"))
        # Should be approximately now + 5s
        assert db._cb_open_until == pytest.approx(before + 5, abs=1)

    def test_trip_is_idempotent(self):
        """Calling twice with CB error keeps the breaker open (extends or equal)."""
        self.db._maybe_trip_circuit_breaker(Exception("circuit breaker open"))
        first_open_until = self.db._cb_open_until
        self.db._maybe_trip_circuit_breaker(Exception("circuit breaker open"))
        # Second call should not decrease the open_until time
        assert self.db._cb_open_until >= first_open_until

"""
Unit tests verifying that the /accounts, /agents, /agent-runs/active, and
/threads endpoints return HTTP 503 (not 500) when the database is unavailable,
and HTTP 500 for generic application errors.

Also verifies that error responses do NOT leak internal infrastructure details
(IP addresses, hostnames, stack traces).

All tests use FastAPI's TestClient with mocked DB layers – no real database
connections are made.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

JWT_HEADER = {"Authorization": "Bearer test-token"}

# Canonical DB-unavailability error message (mirrors the Supabase circuit breaker)
CB_ERROR = (
    "(psycopg.OperationalError) connection failed: FATAL: "
    "Circuit breaker open: Too many authentication errors"
)

# A generic, non-DB application error
APP_ERROR = "KeyError: 'agent_id' missing from response"


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient with JWT auth dependency bypassed."""
    from api import app
    from core.utils.auth_utils import verify_and_get_user_id_from_jwt

    # Override the JWT dependency so we don't need a real Supabase JWT
    app.dependency_overrides[verify_and_get_user_id_from_jwt] = lambda: "test-user-id"

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# /accounts endpoint
# ---------------------------------------------------------------------------

class TestAccountsEndpointErrors:

    def test_returns_503_on_circuit_breaker(self, client):
        with patch(
            "core.endpoints.accounts_repo.get_user_accounts",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/accounts", headers=JWT_HEADER)

        assert r.status_code == 503, f"Expected 503, got {r.status_code}: {r.text}"

    def test_503_has_retry_after_header(self, client):
        with patch(
            "core.endpoints.accounts_repo.get_user_accounts",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/accounts", headers=JWT_HEADER)

        assert "retry-after" in {k.lower() for k in r.headers}

    def test_503_does_not_leak_internal_details(self, client):
        with patch(
            "core.endpoints.accounts_repo.get_user_accounts",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/accounts", headers=JWT_HEADER)

        body = r.text
        # Must not expose IP addresses, hostnames, or psycopg internals
        assert "57.182.231.186" not in body
        assert "psycopg" not in body
        assert "pooler.supabase.com" not in body

    def test_returns_500_on_generic_app_error(self, client):
        with patch(
            "core.endpoints.accounts_repo.get_user_accounts",
            new_callable=AsyncMock,
            side_effect=Exception(APP_ERROR),
        ):
            r = client.get("/v1/accounts", headers=JWT_HEADER)

        assert r.status_code == 500, f"Expected 500, got {r.status_code}: {r.text}"

    def test_500_does_not_leak_stack_trace(self, client):
        with patch(
            "core.endpoints.accounts_repo.get_user_accounts",
            new_callable=AsyncMock,
            side_effect=Exception(APP_ERROR),
        ):
            r = client.get("/v1/accounts", headers=JWT_HEADER)

        body = r.text
        assert "Traceback" not in body
        assert "File " not in body


# ---------------------------------------------------------------------------
# /agents endpoint
# ---------------------------------------------------------------------------

class TestAgentsEndpointErrors:

    def test_returns_503_on_circuit_breaker(self, client):
        with patch(
            "core.agents.agent_service.AgentService.get_agents_paginated",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/agents", headers=JWT_HEADER)

        assert r.status_code == 503, f"Expected 503, got {r.status_code}: {r.text}"

    def test_503_has_retry_after_header(self, client):
        with patch(
            "core.agents.agent_service.AgentService.get_agents_paginated",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/agents", headers=JWT_HEADER)

        assert "retry-after" in {k.lower() for k in r.headers}

    def test_503_body_is_sanitized(self, client):
        with patch(
            "core.agents.agent_service.AgentService.get_agents_paginated",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/agents", headers=JWT_HEADER)

        body = r.text
        assert "pooler.supabase.com" not in body
        assert "Circuit breaker" not in body  # must be sanitized

    def test_returns_500_on_generic_error(self, client):
        with patch(
            "core.agents.agent_service.AgentService.get_agents_paginated",
            new_callable=AsyncMock,
            side_effect=Exception(APP_ERROR),
        ):
            r = client.get("/v1/agents", headers=JWT_HEADER)

        assert r.status_code == 500


# ---------------------------------------------------------------------------
# /agent-runs/active endpoint
# ---------------------------------------------------------------------------

class TestActiveAgentRunsErrors:

    def test_returns_503_on_circuit_breaker(self, client):
        with patch(
            "core.agents.repo.get_active_agent_runs",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/agent-runs/active", headers=JWT_HEADER)

        assert r.status_code == 503, f"Expected 503, got {r.status_code}: {r.text}"

    def test_503_has_retry_after_header(self, client):
        with patch(
            "core.agents.repo.get_active_agent_runs",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/agent-runs/active", headers=JWT_HEADER)

        assert "retry-after" in {k.lower() for k in r.headers}

    def test_returns_200_when_db_healthy(self, client):
        with patch(
            "core.agents.repo.get_active_agent_runs",
            new_callable=AsyncMock,
            return_value=[],
        ):
            r = client.get("/v1/agent-runs/active", headers=JWT_HEADER)

        assert r.status_code == 200
        assert r.json() == {"active_runs": []}


# ---------------------------------------------------------------------------
# /threads endpoint
# ---------------------------------------------------------------------------

class TestThreadsEndpointErrors:

    def test_returns_503_on_circuit_breaker(self, client):
        with patch(
            "core.threads.repo.list_user_threads",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/threads", headers=JWT_HEADER)

        assert r.status_code == 503, f"Expected 503, got {r.status_code}: {r.text}"

    def test_503_has_retry_after_header(self, client):
        with patch(
            "core.threads.repo.list_user_threads",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/threads", headers=JWT_HEADER)

        assert "retry-after" in {k.lower() for k in r.headers}

    def test_503_body_sanitized(self, client):
        with patch(
            "core.threads.repo.list_user_threads",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get("/v1/threads", headers=JWT_HEADER)

        body = r.text
        assert "psycopg" not in body
        assert "18.176.230.146" not in body  # IP from error logs

    def test_returns_200_when_db_healthy(self, client):
        with patch(
            "core.threads.repo.list_user_threads",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            r = client.get("/v1/threads", headers=JWT_HEADER)

        assert r.status_code == 200
        data = r.json()
        assert "threads" in data
        assert "pagination" in data

    def test_returns_500_on_generic_error(self, client):
        with patch(
            "core.threads.repo.list_user_threads",
            new_callable=AsyncMock,
            side_effect=AttributeError(APP_ERROR),
        ):
            r = client.get("/v1/threads", headers=JWT_HEADER)

        assert r.status_code == 500


# ---------------------------------------------------------------------------
# Thread detail endpoint (GET /threads/{thread_id})
# ---------------------------------------------------------------------------

class TestThreadDetailErrors:
    THREAD_ID = "6f18c80c-db33-4d4f-9701-0dbbdc2dd2f5"

    def test_returns_503_on_circuit_breaker(self, client):
        with patch(
            "core.threads.repo.get_thread_by_id",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get(f"/v1/threads/{self.THREAD_ID}", headers=JWT_HEADER)

        assert r.status_code == 503

    def test_503_does_not_leak_psycopg_trace(self, client):
        with patch(
            "core.threads.repo.get_thread_by_id",
            new_callable=AsyncMock,
            side_effect=Exception(CB_ERROR),
        ):
            r = client.get(f"/v1/threads/{self.THREAD_ID}", headers=JWT_HEADER)

        assert "psycopg" not in r.text
        assert "aws-1-ap-northeast-1" not in r.text

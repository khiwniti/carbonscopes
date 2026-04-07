"""
Comprehensive TDD tests for the /v1/chat endpoint.

RED  -> run tests, watch them fail
GREEN -> minimal implementation makes them pass
REFACTOR -> clean up without breaking tests

Run:
    cd backend && uv run pytest tests/test_chat_endpoint.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from core.chat.api import router as chat_router
from core.utils.auth_utils import verify_and_get_user_id_from_jwt

FAKE_USER = "test-user-uuid-1234"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    _app = FastAPI()
    _app.dependency_overrides[verify_and_get_user_id_from_jwt] = lambda: FAKE_USER
    _app.include_router(chat_router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Context manager that mocks all heavy I/O in core.chat.api
# ---------------------------------------------------------------------------

def _make_mock_db():
    """Return a DBConnection mock whose .client is awaitable."""
    mock_db_instance = MagicMock()
    # db.client is an async property: `await db.client` calls __get__ then awaits
    # Simplest way: make client a coroutine function so await works
    fake_client = MagicMock()
    async def _client_coro():
        return fake_client
    type(mock_db_instance).client = property(lambda self: _client_coro())
    return mock_db_instance


def _mock_chat_internals(thread_id="t1", project_id="p1", model="gpt-4"):
    """Patch all external I/O so tests run without DB / Redis / LLM."""
    mock_db_instance = _make_mock_db()

    return [
        patch("core.chat.api.DBConnection", return_value=mock_db_instance),
        patch(
            "core.chat.api.threads_repo.create_new_thread_with_project",
            new=AsyncMock(return_value={"thread_id": thread_id, "project_id": project_id}),
        ),
        patch(
            "core.chat.api.threads_repo.get_thread_with_project",
            new=AsyncMock(return_value={"project_id": project_id, "account_id": FAKE_USER}),
        ),
        patch(
            "core.chat.api.model_manager.get_default_model_for_user",
            new=AsyncMock(return_value=model),
        ),
        patch("core.chat.api.execute_agent_run", new=AsyncMock(return_value=None)),
    ]


def _apply_patches(patches):
    """Enter a list of context managers and return them."""
    entered = []
    mocks = []
    for p in patches:
        m = p.__enter__()
        entered.append(p)
        mocks.append(m)
    return entered, mocks


def _exit_patches(patches):
    for p in patches:
        p.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# RED: tests that define the expected contract
# ---------------------------------------------------------------------------


class TestChatEndpointContract:
    """These tests define what the /chat endpoint MUST do."""

    def test_post_with_valid_prompt_returns_200(self, client):
        patches = _mock_chat_internals()
        ctxs, _ = _apply_patches(patches)
        try:
            resp = client.post("/chat", json={"prompt": "open a browser"})
        finally:
            _exit_patches(ctxs)
        assert resp.status_code == 200

    def test_response_contains_required_fields(self, client):
        patches = _mock_chat_internals()
        ctxs, _ = _apply_patches(patches)
        try:
            resp = client.post("/chat", json={"prompt": "search the web"})
        finally:
            _exit_patches(ctxs)
        data = resp.json()
        assert "response" in data
        assert "status" in data
        assert "thread_id" in data
        assert "agent_run_id" in data

    def test_empty_prompt_returns_400(self, client):
        resp = client.post("/chat", json={"prompt": ""})
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    def test_whitespace_only_prompt_returns_400(self, client):
        resp = client.post("/chat", json={"prompt": "   "})
        assert resp.status_code == 400

    def test_missing_prompt_field_returns_422(self, client):
        resp = client.post("/chat", json={})
        assert resp.status_code == 422

    def test_valid_prompt_triggers_agent_run(self, client):
        """Agent run must actually be triggered when a prompt is sent."""
        mock_run = AsyncMock(return_value=None)
        mock_db = _make_mock_db()

        with patch("core.chat.api.DBConnection", return_value=mock_db), \
             patch("core.chat.api.threads_repo.create_new_thread_with_project",
                   new=AsyncMock(return_value={"thread_id": "t1", "project_id": "p1"})), \
             patch("core.chat.api.model_manager.get_default_model_for_user",
                   new=AsyncMock(return_value="gpt-4")), \
             patch("core.chat.api.execute_agent_run", new=mock_run):
            client.post("/chat", json={"prompt": "activate computer use"})

        mock_run.assert_awaited_once()

    def test_existing_thread_id_reuses_thread(self, client):
        """When thread_id is supplied, no new thread should be created."""
        mock_create = AsyncMock(return_value={"thread_id": "new", "project_id": "p1"})
        mock_get = AsyncMock(return_value={"project_id": "p1", "account_id": FAKE_USER})
        mock_db = _make_mock_db()

        with patch("core.chat.api.DBConnection", return_value=mock_db), \
             patch("core.chat.api.threads_repo.create_new_thread_with_project", new=mock_create), \
             patch("core.chat.api.threads_repo.get_thread_with_project", new=mock_get), \
             patch("core.chat.api.model_manager.get_default_model_for_user",
                   new=AsyncMock(return_value="gpt-4")), \
             patch("core.chat.api.execute_agent_run", new=AsyncMock()):
            resp = client.post(
                "/chat",
                json={"prompt": "do something", "thread_id": "existing-thread-id"},
            )

        mock_create.assert_not_awaited()
        assert resp.status_code == 200

    def test_unknown_thread_id_returns_404(self, client):
        mock_db = _make_mock_db()

        with patch("core.chat.api.DBConnection", return_value=mock_db), \
             patch("core.chat.api.threads_repo.get_thread_with_project",
                   new=AsyncMock(return_value=None)):
            resp = client.post(
                "/chat",
                json={"prompt": "do something", "thread_id": "ghost-thread"},
            )

        assert resp.status_code == 404

    def test_internal_error_returns_500(self, client):
        mock_db = _make_mock_db()

        with patch("core.chat.api.DBConnection", return_value=mock_db), \
             patch("core.chat.api.threads_repo.create_new_thread_with_project",
                   new=AsyncMock(side_effect=RuntimeError("DB exploded"))):
            resp = client.post("/chat", json={"prompt": "trigger error"})

        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Frontend compatibility: verify JSON shape matches what the UI expects
# ---------------------------------------------------------------------------


class TestChatResponseShape:
    """Ensure the response shape matches what apps/frontend expects."""

    def test_status_is_started_on_success(self, client):
        patches = _mock_chat_internals(thread_id="thread-42")
        ctxs, _ = _apply_patches(patches)
        try:
            resp = client.post("/chat", json={"prompt": "hello world"})
        finally:
            _exit_patches(ctxs)
        assert resp.json()["status"] == "started"

    def test_thread_id_in_response_matches_created_thread(self, client):
        patches = _mock_chat_internals(thread_id="thread-999")
        ctxs, _ = _apply_patches(patches)
        try:
            resp = client.post("/chat", json={"prompt": "hello world"})
        finally:
            _exit_patches(ctxs)
        assert resp.json()["thread_id"] == "thread-999"

    def test_agent_run_id_is_present_and_non_empty(self, client):
        patches = _mock_chat_internals()
        ctxs, _ = _apply_patches(patches)
        try:
            resp = client.post("/chat", json={"prompt": "run something"})
        finally:
            _exit_patches(ctxs)
        run_id = resp.json().get("agent_run_id")
        assert run_id is not None and run_id != ""

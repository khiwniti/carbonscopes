"""
E2EFixture — base class for CarbonScope API end-to-end tests.

Handles:
- Authenticated httpx client lifecycle
- Test user creation and JWT minting
- Per-test resource tracking for automatic cleanup
- App readiness check before each test
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator, Dict, List, Any

import httpx
import jwt
import pytest
import pytest_asyncio
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("e2e.fixture")

_DEFAULT_BASE_URL = "http://localhost:8000/v1"
_DEFAULT_TIMEOUT = 30.0


class E2EFixture:
    """
    Base class for CarbonScope E2E API tests.

    Inherit from this class to get a pre-authenticated API client,
    automatic resource cleanup, and app readiness guarantees.

    Example::

        class TestCarbonFlow(E2EFixture):
            async def test_create_assessment(self):
                response = await self.client.post("/assessments", json={...})
                assert response.status_code == 201

    The ``client`` attribute is an authenticated ``httpx.AsyncClient`` pointed
    at the running backend.  The ``api`` attribute exposes higher-level
    domain helpers (see ``CarbonScopeAPIClient``).
    """

    # ── class-level config (override in subclass or via env) ──────────────
    base_url: str = os.getenv("TEST_API_URL", _DEFAULT_BASE_URL)
    request_timeout: float = float(os.getenv("TEST_REQUEST_TIMEOUT", str(_DEFAULT_TIMEOUT)))
    agent_timeout: float = float(os.getenv("TEST_AGENT_TIMEOUT", "120.0"))

    # Set True to skip cleanup on failure (useful for debugging)
    skip_cleanup_on_failure: bool = False

    # ── instance state ─────────────────────────────────────────────────────
    client: httpx.AsyncClient
    user_info: Dict[str, str]
    _resources_to_cleanup: List[Dict[str, Any]]
    _test_failed: bool

    # ── pytest setup / teardown ────────────────────────────────────────────

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_fixture(self) -> AsyncGenerator[None, None]:
        """Pytest fixture that wires up the authenticated client for each test."""
        self._resources_to_cleanup = []
        self._test_failed = False

        self.user_info = await self._get_or_create_test_user()
        token = self._mint_jwt(self.user_info["user_id"])

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=self.request_timeout,
            follow_redirects=True,
        ) as client:
            self.client = client
            from .api_client import CarbonScopeAPIClient
            self.api = CarbonScopeAPIClient(client)

            await self._wait_for_app_ready()
            await self.setup()

            try:
                yield
            except Exception:
                self._test_failed = True
                raise
            finally:
                await self.teardown()
                if not (self._test_failed and self.skip_cleanup_on_failure):
                    await self._cleanup_resources()

    # ── override hooks ─────────────────────────────────────────────────────

    async def setup(self) -> None:
        """Override to run custom setup before each test."""

    async def teardown(self) -> None:
        """Override to run custom teardown after each test."""

    # ── helpers ────────────────────────────────────────────────────────────

    def track_resource(self, resource_type: str, resource_id: str) -> None:
        """
        Register a resource for automatic deletion after the test.

        Args:
            resource_type: One of "project", "thread", "agent_run"
            resource_id:   The resource's ID string
        """
        self._resources_to_cleanup.append({"type": resource_type, "id": resource_id})

    async def assert_app_ready(self) -> None:
        """Assert the backend is reachable and healthy."""
        response = await self.client.get("/health")
        assert response.status_code == 200, f"Backend not ready: {response.text}"

    # ── private ────────────────────────────────────────────────────────────

    async def _wait_for_app_ready(self, retries: int = 5) -> None:
        """Poll /health until the app responds or retries are exhausted."""
        from .async_assert import AsyncAssert

        async def _is_healthy() -> bool:
            try:
                r = await self.client.get("/health")
                return r.status_code == 200
            except Exception:
                return False

        await AsyncAssert.wait_until(_is_healthy, "backend /health to respond", timeout=30.0)

    async def _cleanup_resources(self) -> None:
        """Delete all tracked resources in reverse creation order."""
        for resource in reversed(self._resources_to_cleanup):
            try:
                rtype = resource["type"]
                rid = resource["id"]
                if rtype == "project":
                    await self.client.delete(f"/projects/{rid}")
                elif rtype == "thread":
                    await self.client.delete(f"/threads/{rid}")
                elif rtype == "agent_run":
                    await self.client.post(f"/agent-run/{rid}/stop")
                else:
                    logger.warning(f"Unknown resource type for cleanup: {rtype}")
            except Exception as exc:
                logger.debug(f"Cleanup error (non-fatal): {exc}")

    # ── static helpers ─────────────────────────────────────────────────────

    @staticmethod
    async def _get_or_create_test_user() -> Dict[str, str]:
        """Delegate to the shared conftest helper or create inline."""
        # Re-use the session-scoped helper from the parent conftest when available.
        # This avoids creating a new Supabase user for every test class.
        from tests.conftest import _ensure_test_user_exists
        from tests.config import E2ETestConfig

        config = E2ETestConfig()
        return await _ensure_test_user_exists(config)

    @staticmethod
    def _mint_jwt(user_id: str) -> str:
        """Mint a short-lived JWT for the given user_id."""
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set — cannot mint test JWT")

        payload = {
            "sub": user_id,
            "aud": "authenticated",
            "role": "authenticated",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp(),
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

"""
Infrastructure verification tests — prove the E2E scaffold works.

Run these first after scaffolding to confirm everything is wired up.

    uv run pytest tests/e2e/test_infrastructure.py -v -m e2e

Three tests mirror the structure of the game E2E example tests:
  1. App loads and is healthy (equivalent to "GameLoadsAndReachesReadyState")
  2. API client can interact with endpoints (equivalent to "InputSimulatorCanClickButtons")
  3. ScenarioBuilder can set up state (equivalent to "ScenarioBuilderCanConfigureState")
"""

import pytest
import pytest_asyncio
from tests.e2e.infrastructure import E2EFixture, ScenarioBuilder, AsyncAssert


@pytest.mark.e2e
class TestInfrastructureVerification(E2EFixture):
    """
    Verifies the E2E infrastructure scaffold is correctly wired up.
    Inheriting from E2EFixture gives us ``self.client``, ``self.api``,
    and automatic auth + cleanup.
    """

    async def test_infrastructure_app_loads_and_is_healthy(self):
        """
        Verify the base fixture:
        - Backend is reachable
        - Health endpoint returns OK
        - Authenticated client is configured
        - API helper is non-null
        """
        # client and api are provided by E2EFixture._setup_fixture
        assert self.client is not None, "httpx client should be initialized"
        assert self.api is not None, "CarbonScopeAPIClient should be initialized"

        # Verify app is healthy
        health = await self.api.get_health()
        assert isinstance(health, dict), "health response should be a dict"
        # Accept either {"status": "ok"} or {"checkpointer": "connected"} etc.
        assert health, "health response should not be empty"

        # Verify auth token is accepted
        account = await self.api.get_account_state()
        assert account, "authenticated account state should return data"

    async def test_infrastructure_api_client_can_call_endpoints(self):
        """
        Verify the API client helpers work for common operations.
        This is the API equivalent of "InputSimulatorCanClickButtons".
        """
        # List projects (may be empty — that's fine)
        projects = await self.api.list_projects()
        assert isinstance(projects, list), "list_projects should return a list"

        # List threads (may be empty)
        threads = await self.api.list_threads()
        assert isinstance(threads, list), "list_threads should return a list"

        # List accounts
        accounts = await self.api.list_accounts()
        assert isinstance(accounts, list), "list_accounts should return a list"

        # Verify HTTP 404 handling (unknown route should not crash the client)
        response = await self.client.get("/nonexistent-route-12345")
        assert response.status_code == 404, "unknown routes should return 404"

    async def test_infrastructure_scenario_builder_can_configure_state(self):
        """
        Verify ScenarioBuilder executes actions and returns populated state.
        This is the equivalent of "ScenarioBuilderCanConfigureState".

        NOTE: This test may be skipped if the /projects endpoint does not
        yet exist in your backend.  Adjust the ScenarioBuilder actions to
        match your actual API endpoints.
        """
        # Build a scenario with a project
        state = await (
            ScenarioBuilder(self.client)
            .with_project(
                name="Infrastructure Test Project",
                description="Auto-created by test_infrastructure.py",
            )
            .build()
        )

        # State should contain the created project (if endpoint exists)
        if state.get("project"):
            project = state["project"]
            assert "id" in project or "project_id" in project, (
                "project should have an ID"
            )
            # Register for cleanup
            project_id = project.get("id") or project.get("project_id")
            if project_id:
                self.track_resource("project", project_id)
        else:
            # Endpoint may not exist yet — verify builder ran without error
            assert isinstance(state, dict), "build() should return a dict"

    async def test_infrastructure_async_assert_utilities_work(self):
        """
        Verify AsyncAssert utilities function correctly.
        """
        # wait_until with immediate condition
        await AsyncAssert.wait_until(
            lambda: True,
            "immediate condition",
            timeout=1.0,
        )

        # wait_for_value
        counter = {"value": 0}

        import asyncio

        async def increment_and_check() -> bool:
            counter["value"] += 1
            return counter["value"] >= 3

        await AsyncAssert.wait_until(
            increment_and_check,
            "counter to reach 3",
            timeout=5.0,
            poll_interval=0.1,
        )
        assert counter["value"] >= 3

        # assert_never_true
        await AsyncAssert.assert_never_true(
            lambda: False,
            "always-false condition",
            duration=0.5,
        )

        # wait_for_not_none
        result = await AsyncAssert.wait_for_not_none(
            lambda: "ready",
            "non-None value",
            timeout=1.0,
        )
        assert result == "ready"

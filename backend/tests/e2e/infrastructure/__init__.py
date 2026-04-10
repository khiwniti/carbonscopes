"""
CarbonScope E2E Test Infrastructure

Provides base fixtures, scenario builders, API helpers, and async assertion
utilities for writing reliable, maintainable end-to-end API tests.

Usage:
    from tests.e2e.infrastructure import E2EFixture, ScenarioBuilder, AsyncAssert

    class TestMyFlow(E2EFixture):
        async def test_something(self):
            scenario = await ScenarioBuilder(self.client).with_project("Test Project").build()
            await AsyncAssert.wait_until(lambda: ..., "condition description")
"""

from .e2e_fixture import E2EFixture
from .scenario_builder import ScenarioBuilder
from .api_client import CarbonScopeAPIClient
from .async_assert import AsyncAssert

__all__ = ["E2EFixture", "ScenarioBuilder", "CarbonScopeAPIClient", "AsyncAssert"]

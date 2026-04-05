"""Shared pytest fixtures for agent testing.

This module provides reusable fixtures for LangGraph agent tests:
- Mock agents with configurable capabilities
- Configured routers with registered test agents
- Initial state fixtures
- Checkpointer fixtures (MemorySaver for fast tests)
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from core.agents.base import Agent
from core.agents.state import AgentState
from core.agents.router import SupervisorRouter


class MockAgent(Agent):
    """Mock agent for testing supervisor routing and state management."""

    def __init__(self, name: str, capabilities: set[str]):
        super().__init__(name, capabilities)

    async def execute(self, state: AgentState) -> dict[str, any]:
        """Execute mock agent logic - returns agent name for verification."""
        return {"executed": True, "agent": self.name}


@pytest.fixture
def mock_carbon_calculator():
    """Mock carbon calculator agent."""
    return MockAgent("carbon_calculator", {"calculate:carbon"})


@pytest.fixture
def mock_material_analyst():
    """Mock material analyst agent with multiple capabilities."""
    return MockAgent("material_analyst", {"match:materials", "optimize:carbon"})


@pytest.fixture
def mock_boq_parser():
    """Mock BOQ parser agent."""
    return MockAgent("boq_parser", {"parse:boq"})


@pytest.fixture
def mock_knowledge_graph():
    """Mock knowledge graph agent."""
    return MockAgent("knowledge_graph", {"query:kg", "reason:semantic"})


@pytest.fixture
def mock_scenario_manager():
    """Mock scenario manager agent."""
    return MockAgent("scenario_manager", {"manage:scenario"})


@pytest.fixture
def mock_user_interaction():
    """Mock user interaction agent."""
    return MockAgent("user_interaction", {"interact:user"})


@pytest.fixture
def configured_router(
    mock_carbon_calculator,
    mock_material_analyst,
    mock_boq_parser,
    mock_knowledge_graph,
    mock_scenario_manager,
    mock_user_interaction,
):
    """SupervisorRouter with all mock agents registered."""
    router = SupervisorRouter()
    router.register_agent(mock_carbon_calculator)
    router.register_agent(mock_material_analyst)
    router.register_agent(mock_boq_parser)
    router.register_agent(mock_knowledge_graph)
    router.register_agent(mock_scenario_manager)
    router.register_agent(mock_user_interaction)
    return router


@pytest.fixture
def initial_state():
    """Minimal initial AgentState for testing."""
    return {
        "user_query": "Calculate carbon footprint",
        "current_agent": "",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }


@pytest.fixture
def memory_checkpointer():
    """MemorySaver checkpointer for fast testing without PostgreSQL."""
    return MemorySaver()


@pytest.fixture
def thread_config():
    """Standard thread configuration for checkpointed tests."""
    return {"configurable": {"thread_id": "test-thread-1"}}

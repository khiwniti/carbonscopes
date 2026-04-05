"""Tests for Agent base class and AgentRegistry."""

import pytest
from core.agents.base import Agent, AgentRegistry
from core.agents.state import AgentState


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, name: str, capabilities: set[str], should_fail: bool = False):
        super().__init__(name, capabilities)
        self.should_fail = should_fail
        self.execute_called = False

    async def execute(self, state: AgentState) -> dict[str, any]:
        """Mock execution."""
        self.execute_called = True

        if self.should_fail:
            raise ValueError("Mock agent failure")

        return {
            "result": "success",
            "query_processed": state["user_query"],
        }


@pytest.fixture
def mock_state():
    """Fixture providing a mock AgentState."""
    return {
        "user_query": "Test query",
        "current_agent": "test_agent",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }


@pytest.mark.asyncio
async def test_agent_abstract_class():
    """Test that Agent is abstract and requires execute() implementation."""
    with pytest.raises(TypeError):
        # Cannot instantiate abstract class
        Agent("test", {"test:capability"})


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization with name and capabilities."""
    agent = MockAgent("test_agent", {"test:capability", "test:another"})

    assert agent.name == "test_agent"
    assert agent.capabilities == {"test:capability", "test:another"}
    assert agent.logger.name == "agent.test_agent"


@pytest.mark.asyncio
async def test_get_capabilities():
    """Test get_capabilities() returns agent capability set."""
    capabilities = {"match:materials", "optimize:materials"}
    agent = MockAgent("material_analyst", capabilities)

    assert agent.get_capabilities() == capabilities


@pytest.mark.asyncio
async def test_execute_success(mock_state):
    """Test successful agent execution."""
    agent = MockAgent("test_agent", {"test:capability"})

    result = await agent.execute(mock_state)

    assert agent.execute_called
    assert result["result"] == "success"
    assert result["query_processed"] == "Test query"


@pytest.mark.asyncio
async def test_execute_with_metrics_success(mock_state):
    """Test execute_with_metrics() wrapper for successful execution."""
    agent = MockAgent("test_agent", {"test:capability"})

    result = await agent.execute_with_metrics(mock_state)

    assert result["status"] == "success"
    assert result["agent_name"] == "test_agent"
    assert "duration_ms" in result
    assert result["duration_ms"] > 0
    assert "result" in result
    assert result["result"]["result"] == "success"


@pytest.mark.asyncio
async def test_execute_with_metrics_failure(mock_state):
    """Test execute_with_metrics() handles failures and re-raises."""
    agent = MockAgent("test_agent", {"test:capability"}, should_fail=True)

    with pytest.raises(ValueError, match="Mock agent failure"):
        await agent.execute_with_metrics(mock_state)

    # Verify execute was called despite failure
    assert agent.execute_called


def test_agent_registry_initialization():
    """Test AgentRegistry initialization."""
    registry = AgentRegistry()

    assert registry.count() == 0
    assert registry.list_agents() == {}


def test_register_agent():
    """Test registering an agent."""
    registry = AgentRegistry()
    agent = MockAgent("test_agent", {"test:capability"})

    registry.register_agent(agent)

    assert registry.count() == 1
    assert "test_agent" in registry.list_agents()
    assert registry.list_agents()["test_agent"] == {"test:capability"}


def test_register_duplicate_agent_raises():
    """Test that registering duplicate agent name raises ValueError."""
    registry = AgentRegistry()
    agent1 = MockAgent("test_agent", {"capability1"})
    agent2 = MockAgent("test_agent", {"capability2"})

    registry.register_agent(agent1)

    with pytest.raises(ValueError, match="already registered"):
        registry.register_agent(agent2)


def test_get_agent():
    """Test retrieving agent by name."""
    registry = AgentRegistry()
    agent = MockAgent("test_agent", {"test:capability"})
    registry.register_agent(agent)

    retrieved = registry.get_agent("test_agent")

    assert retrieved is agent
    assert retrieved.name == "test_agent"


def test_get_agent_not_found():
    """Test get_agent raises KeyError for unknown agent."""
    registry = AgentRegistry()

    with pytest.raises(KeyError):
        registry.get_agent("nonexistent_agent")


def test_get_agents_with_capability():
    """Test finding agents by capability."""
    registry = AgentRegistry()

    agent1 = MockAgent("agent1", {"match:materials", "optimize:materials"})
    agent2 = MockAgent("agent2", {"calculate:carbon"})
    agent3 = MockAgent("agent3", {"match:materials"})

    registry.register_agent(agent1)
    registry.register_agent(agent2)
    registry.register_agent(agent3)

    # Find agents with "match:materials"
    agents_with_match = registry.get_agents_with_capability("match:materials")
    assert agents_with_match == {"agent1", "agent3"}

    # Find agents with "calculate:carbon"
    agents_with_carbon = registry.get_agents_with_capability("calculate:carbon")
    assert agents_with_carbon == {"agent2"}

    # Find agents with non-existent capability
    agents_with_unknown = registry.get_agents_with_capability("unknown:capability")
    assert agents_with_unknown == set()


def test_list_agents():
    """Test list_agents() returns all agents with capabilities."""
    registry = AgentRegistry()

    agent1 = MockAgent("agent1", {"capability1", "capability2"})
    agent2 = MockAgent("agent2", {"capability3"})

    registry.register_agent(agent1)
    registry.register_agent(agent2)

    agents = registry.list_agents()

    assert len(agents) == 2
    assert agents["agent1"] == {"capability1", "capability2"}
    assert agents["agent2"] == {"capability3"}


def test_agent_registry_count():
    """Test agent count tracking."""
    registry = AgentRegistry()

    assert registry.count() == 0

    registry.register_agent(MockAgent("agent1", {"cap1"}))
    assert registry.count() == 1

    registry.register_agent(MockAgent("agent2", {"cap2"}))
    assert registry.count() == 2


def test_capability_index_multiple_agents():
    """Test that capability index tracks multiple agents per capability."""
    registry = AgentRegistry()

    agent1 = MockAgent("agent1", {"shared:capability", "unique1"})
    agent2 = MockAgent("agent2", {"shared:capability", "unique2"})
    agent3 = MockAgent("agent3", {"shared:capability"})

    registry.register_agent(agent1)
    registry.register_agent(agent2)
    registry.register_agent(agent3)

    # All three agents share "shared:capability"
    agents_with_shared = registry.get_agents_with_capability("shared:capability")
    assert agents_with_shared == {"agent1", "agent2", "agent3"}

    # Only agent1 has "unique1"
    agents_with_unique1 = registry.get_agents_with_capability("unique1")
    assert agents_with_unique1 == {"agent1"}


@pytest.mark.asyncio
async def test_agent_logger_name():
    """Test that agent logger has correct name."""
    agent = MockAgent("material_analyst", {"match:materials"})

    assert agent.logger.name == "agent.material_analyst"

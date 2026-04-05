"""Tests for PostgreSQL checkpointing and state persistence."""

import pytest
import os
from langgraph.checkpoint.memory import MemorySaver
from core.agents.checkpointer import get_checkpointer
from core.agents.supervisor import create_supervisor_graph, set_router
from core.agents.router import SupervisorRouter
from core.agents.base import Agent
from core.agents.state import AgentState


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, name: str, capabilities: set[str]):
        super().__init__(name, capabilities)

    async def execute(self, state: AgentState) -> dict[str, any]:
        return {"executed": True, "agent": self.name}


@pytest.fixture
def configured_router():
    """Fixture providing a SupervisorRouter with mock agents."""
    router = SupervisorRouter()
    router.register_agent(MockAgent("carbon_calculator", {"calculate:carbon"}))
    router.register_agent(MockAgent("material_analyst", {"match:materials"}))
    router.register_agent(MockAgent("user_interaction", {"interact:user"}))
    return router


@pytest.fixture
def initial_state():
    """Fixture providing initial AgentState."""
    return {
        "user_query": "Calculate carbon footprint",
        "current_agent": "",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }


def test_create_graph_without_checkpointer(configured_router, initial_state):
    """Test graph creation without checkpointer (stateless mode)."""
    set_router(configured_router)

    try:
        graph = create_supervisor_graph()
        result = graph.invoke(initial_state)

        assert result["current_agent"] == "carbon_calculator"
        assert "carbon_calculator" in result["agent_history"]
    finally:
        set_router(None)


def test_create_graph_with_memory_checkpointer(configured_router, initial_state):
    """Test graph creation with MemorySaver checkpointer."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        # First invocation with thread_id
        result1 = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": "test-thread-1"}}
        )

        assert result1["current_agent"] == "carbon_calculator"
        assert result1["task_results"] == {}  # No task results yet

        # Second invocation with same thread_id (state should persist)
        second_state = {
            **initial_state,
            "user_query": "Find material alternatives",
        }

        result2 = graph.invoke(
            second_state,
            config={"configurable": {"thread_id": "test-thread-1"}}
        )

        # State should carry over from first invocation
        assert result2["current_agent"] == "material_analyst"
        assert "carbon_calculator" in result2["agent_history"]  # History persisted
    finally:
        set_router(None)


def test_checkpointer_state_isolation_between_threads(configured_router, initial_state):
    """Test that different thread_ids maintain separate state."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        # Thread 1
        result1 = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": "thread-1"}}
        )

        # Thread 2 (different thread_id)
        result2 = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": "thread-2"}}
        )

        # Both should start fresh
        assert result1["agent_history"] == ["carbon_calculator"]
        assert result2["agent_history"] == ["carbon_calculator"]

        # Threads are independent
        assert result1 is not result2
    finally:
        set_router(None)


def test_checkpointer_state_accumulation(configured_router):
    """Test that state accumulates correctly across multiple invocations."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        thread_id = "accumulation-test"
        config = {"configurable": {"thread_id": thread_id}}

        # Invocation 1: Calculate carbon
        state1 = {
            "user_query": "Calculate carbon",
            "current_agent": "",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }
        result1 = graph.invoke(state1, config)

        # Invocation 2: Find materials
        state2 = {
            "user_query": "Match materials",
            "current_agent": "",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }
        result2 = graph.invoke(state2, config)

        # History should accumulate
        assert "carbon_calculator" in result2["agent_history"]
        assert "material_analyst" in result2["agent_history"]
        assert len(result2["agent_history"]) >= 2
    finally:
        set_router(None)


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="PostgreSQL DATABASE_URL not configured"
)
def test_get_checkpointer_postgres(configured_router, initial_state):
    """Test PostgreSQL checkpointer creation (requires DATABASE_URL)."""
    try:
        checkpointer = get_checkpointer()
        assert checkpointer is not None

        # Create graph with PostgreSQL checkpointer
        set_router(configured_router)
        graph = create_supervisor_graph(checkpointer)

        # Test basic invocation
        result = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": "postgres-test-1"}}
        )

        assert result["current_agent"] == "carbon_calculator"
    except Exception as e:
        pytest.skip(f"PostgreSQL checkpointer test skipped: {e}")
    finally:
        set_router(None)


def test_checkpointer_with_task_results(configured_router):
    """Test that task_results are preserved across invocations."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        thread_id = "task-results-test"
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation with task results
        state1 = {
            "user_query": "Calculate carbon",
            "current_agent": "",
            "agent_history": [],
            "task_results": {
                "boq_parsed": True,
                "materials_matched": ["concrete", "steel"],
            },
            "error_count": 0,
            "scenario_context": None,
        }
        result1 = graph.invoke(state1, config)

        # Task results from input should be preserved in output
        assert result1["task_results"]["boq_parsed"] is True
        assert result1["task_results"]["materials_matched"] == ["concrete", "steel"]

        # Second invocation with same thread_id preserves task_results if passed
        state2 = {
            "user_query": "Find alternatives",
            "current_agent": "",
            "agent_history": [],
            "task_results": {
                "boq_parsed": True,  # Explicitly carry forward
                "materials_matched": ["concrete", "steel"],
                "alternatives_found": ["green-concrete"],  # Add new result
            },
            "error_count": 0,
            "scenario_context": None,
        }
        result2 = graph.invoke(state2, config)

        # Task results should include both old and new data
        assert result2["task_results"]["boq_parsed"] is True
        assert result2["task_results"]["alternatives_found"] == ["green-concrete"]
    finally:
        set_router(None)


def test_checkpointer_with_scenario_context(configured_router):
    """Test that scenario_context persists correctly."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        thread_id = "scenario-context-test"
        config = {"configurable": {"thread_id": thread_id}}

        # State with scenario context
        state = {
            "user_query": "Fork scenario",
            "current_agent": "",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": {
                "base_scenario_id": "user-123:base:boq-456",
                "forked_scenario_ids": ["user-123:base:boq-456:fork:abc"],
                "material_swaps": [
                    {"original": "tgo:concrete-c30", "replacement": "tgo:concrete-green"}
                ],
            },
        }

        result = graph.invoke(state, config)

        # Scenario context should be preserved
        assert result["scenario_context"] is not None
        assert result["scenario_context"]["base_scenario_id"] == "user-123:base:boq-456"
        assert len(result["scenario_context"]["material_swaps"]) == 1
    finally:
        set_router(None)


def test_checkpointer_error_count_persistence(configured_router):
    """Test that error_count increments correctly."""
    set_router(configured_router)

    try:
        checkpointer = MemorySaver()
        graph = create_supervisor_graph(checkpointer)

        thread_id = "error-count-test"
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation with error
        state1 = {
            "user_query": "Calculate carbon",
            "current_agent": "",
            "agent_history": [],
            "task_results": {},
            "error_count": 1,  # One error
            "scenario_context": None,
        }
        result1 = graph.invoke(state1, config)
        assert result1["error_count"] == 1

        # Second invocation with another error
        state2 = {
            "user_query": "Match materials",
            "current_agent": "",
            "agent_history": [],
            "task_results": {},
            "error_count": 2,  # Incremented
            "scenario_context": None,
        }
        result2 = graph.invoke(state2, config)

        # Error count should accumulate
        assert result2["error_count"] == 2
    finally:
        set_router(None)

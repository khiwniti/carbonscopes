"""Tests for Supervisor agent and LangGraph integration."""

import pytest
from core.agents.supervisor import supervisor_node, create_supervisor_graph
from core.agents.state import AgentState
from core.agents.router import SupervisorRouter
from core.agents.base import Agent


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, name: str, capabilities: set[str]):
        super().__init__(name, capabilities)

    async def execute(self, state: AgentState) -> dict[str, any]:
        return {"executed": True, "agent": self.name}


@pytest.fixture
def mock_state():
    """Fixture providing a mock AgentState."""
    return {
        "user_query": "Test query",
        "current_agent": "",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }


@pytest.fixture
def configured_router():
    """Fixture providing a SupervisorRouter with mock agents registered."""
    router = SupervisorRouter()

    # Register mock agents with different capabilities
    router.register_agent(MockAgent("carbon_calculator", {"calculate:carbon"}))
    router.register_agent(MockAgent("material_analyst", {"match:materials", "optimize:carbon"}))
    router.register_agent(MockAgent("boq_parser", {"parse:boq"}))
    router.register_agent(MockAgent("knowledge_graph", {"query:kg", "reason:semantic"}))
    router.register_agent(MockAgent("scenario_manager", {"manage:scenario"}))
    router.register_agent(MockAgent("user_interaction", {"interact:user"}))

    return router


def test_supervisor_node_routes_carbon_query(mock_state, configured_router):
    """Test supervisor routes carbon calculation queries correctly."""
    mock_state["user_query"] = "Calculate carbon footprint"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "carbon_calculator"
    assert result["agent_history"] == ["carbon_calculator"]
    assert result["user_query"] == "Calculate carbon footprint"


def test_supervisor_node_routes_material_query(mock_state, configured_router):
    """Test supervisor routes material matching queries correctly."""
    mock_state["user_query"] = "Match materials to TGO database"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "material_analyst"
    assert result["agent_history"] == ["material_analyst"]


def test_supervisor_node_routes_parsing_query(mock_state, configured_router):
    """Test supervisor routes BOQ parsing queries correctly."""
    mock_state["user_query"] = "Parse this Excel BOQ file"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "boq_parser"
    assert result["agent_history"] == ["boq_parser"]


def test_supervisor_node_routes_knowledge_graph_query(mock_state, configured_router):
    """Test supervisor routes knowledge graph queries correctly."""
    mock_state["user_query"] = "Query knowledge graph for TREES compliance"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "knowledge_graph"
    assert result["agent_history"] == ["knowledge_graph"]


def test_supervisor_node_routes_scenario_query(mock_state, configured_router):
    """Test supervisor routes scenario management queries correctly."""
    mock_state["user_query"] = "Compare scenarios"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "scenario_manager"
    assert result["agent_history"] == ["scenario_manager"]


def test_supervisor_node_fallback_to_user_interaction(mock_state, configured_router):
    """Test supervisor falls back to user_interaction for unclear queries."""
    mock_state["user_query"] = "xyz random abc def"

    result = supervisor_node(mock_state, configured_router)

    assert result["current_agent"] == "user_interaction"
    assert result["agent_history"] == ["user_interaction"]


def test_supervisor_node_preserves_state_fields(mock_state, configured_router):
    """Test supervisor preserves all original state fields."""
    mock_state["user_query"] = "Calculate carbon"
    mock_state["task_results"] = {"existing": "data"}
    mock_state["error_count"] = 2

    result = supervisor_node(mock_state, configured_router)

    assert result["user_query"] == "Calculate carbon"
    assert result["task_results"] == {"existing": "data"}
    assert result["error_count"] == 2
    assert result["scenario_context"] is None


def test_create_supervisor_graph_compiles():
    """Test create_supervisor_graph returns compiled StateGraph."""
    graph = create_supervisor_graph()

    assert graph is not None
    # Graph should be compiled and ready for invoke
    assert hasattr(graph, "invoke")


def test_supervisor_graph_execution(mock_state, configured_router):
    """Test supervisor graph executes and routes correctly."""
    from core.agents.supervisor import set_router

    mock_state["user_query"] = "Find material alternatives"

    # Set the global router for graph execution
    set_router(configured_router)

    try:
        graph = create_supervisor_graph()
        result = graph.invoke(mock_state)

        assert result["current_agent"] == "material_analyst"
        assert "material_analyst" in result["agent_history"]
    finally:
        # Clean up global router
        set_router(None)


def test_supervisor_graph_with_different_queries(configured_router):
    """Test supervisor graph handles various query types."""
    from core.agents.supervisor import set_router

    test_cases = [
        ("Calculate carbon footprint", "carbon_calculator"),
        ("Match materials", "material_analyst"),
        ("Parse BOQ", "boq_parser"),
        ("SPARQL query", "knowledge_graph"),
        ("Fork scenario", "scenario_manager"),
    ]

    # Set the global router for graph execution
    set_router(configured_router)

    try:
        graph = create_supervisor_graph()

        for query, expected_agent in test_cases:
            state = {
                "user_query": query,
                "current_agent": "",
                "agent_history": [],
                "task_results": {},
                "error_count": 0,
                "scenario_context": None,
            }

            result = graph.invoke(state)
            assert result["current_agent"] == expected_agent, f"Query '{query}' should route to {expected_agent}"
    finally:
        # Clean up global router
        set_router(None)


def test_supervisor_node_case_insensitive_routing(mock_state, configured_router):
    """Test supervisor routing is case insensitive."""
    test_queries = [
        "CALCULATE CARBON",
        "Calculate Carbon",
        "calculate carbon",
    ]

    for query in test_queries:
        mock_state["user_query"] = query
        result = supervisor_node(mock_state, configured_router)
        assert result["current_agent"] == "carbon_calculator", f"Query '{query}' should route to carbon_calculator"


def test_supervisor_node_multiple_keyword_match(mock_state, configured_router):
    """Test supervisor handles queries matching multiple capabilities."""
    # Query matching both "match" and "carbon" keywords
    # Should route based on highest score
    mock_state["user_query"] = "Find low-carbon material alternatives"

    result = supervisor_node(mock_state, configured_router)

    # material_analyst matches both "match" (alternatives) and "optimize" (low-carbon)
    assert result["current_agent"] == "material_analyst"


def test_supervisor_graph_preserves_task_results(configured_router):
    """Test supervisor graph preserves existing task results."""
    from core.agents.supervisor import set_router

    state = {
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

    # Set the global router for graph execution
    set_router(configured_router)

    try:
        graph = create_supervisor_graph()
        result = graph.invoke(state)

        # Task results should be preserved
        assert result["task_results"]["boq_parsed"] is True
        assert result["task_results"]["materials_matched"] == ["concrete", "steel"]
    finally:
        # Clean up global router
        set_router(None)

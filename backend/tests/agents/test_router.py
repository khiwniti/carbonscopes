"""Tests for SupervisorRouter capability-based routing."""

import pytest
from core.agents.router import SupervisorRouter, CAPABILITY_KEYWORDS
from core.agents.base import Agent
from core.agents.state import AgentState


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, name: str, capabilities: set[str]):
        super().__init__(name, capabilities)

    async def execute(self, state: AgentState) -> dict[str, any]:
        return {"executed": True}


def test_router_initialization():
    """Test router initializes empty."""
    router = SupervisorRouter()

    assert len(router.agents) == 0
    assert len(router.capability_index) == 0
    assert router.list_agents() == []


def test_register_agent():
    """Test registering an agent."""
    router = SupervisorRouter()
    agent = MockAgent("test_agent", {"test:capability"})

    router.register_agent(agent)

    assert "test_agent" in router.agents
    assert router.get_agent("test_agent") is agent
    assert router.list_agents() == ["test_agent"]


def test_register_duplicate_agent_raises():
    """Test that registering duplicate agent name raises."""
    router = SupervisorRouter()
    agent1 = MockAgent("agent", {"cap1"})
    agent2 = MockAgent("agent", {"cap2"})

    router.register_agent(agent1)

    with pytest.raises(ValueError, match="already registered"):
        router.register_agent(agent2)


def test_capability_indexing():
    """Test that capabilities are indexed correctly."""
    router = SupervisorRouter()

    agent1 = MockAgent("agent1", {"match:materials", "optimize:carbon"})
    agent2 = MockAgent("agent2", {"calculate:carbon"})
    agent3 = MockAgent("agent3", {"match:materials"})

    router.register_agent(agent1)
    router.register_agent(agent2)
    router.register_agent(agent3)

    capabilities = router.list_capabilities()

    assert set(capabilities["match:materials"]) == {"agent1", "agent3"}
    assert capabilities["optimize:carbon"] == ["agent1"]
    assert capabilities["calculate:carbon"] == ["agent2"]


def test_route_carbon_calculation():
    """Test routing carbon calculation queries."""
    router = SupervisorRouter()

    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})
    material_analyst = MockAgent("material_analyst", {"match:materials"})

    router.register_agent(carbon_calc)
    router.register_agent(material_analyst)

    # These queries should route to carbon_calculator
    assert router.route("Calculate carbon footprint") == "carbon_calculator"
    assert router.route("What is the CO2 emission?") == "carbon_calculator"
    assert router.route("Calculate GHG emissions") == "carbon_calculator"


def test_route_material_matching():
    """Test routing material matching queries."""
    router = SupervisorRouter()

    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})
    material_analyst = MockAgent("material_analyst", {"match:materials"})

    router.register_agent(carbon_calc)
    router.register_agent(material_analyst)

    # These should route to material_analyst
    assert router.route("Match materials to TGO database") == "material_analyst"
    assert router.route("Find this material in the database") == "material_analyst"
    assert router.route("Identify concrete materials") == "material_analyst"


def test_route_multiple_capability_match():
    """Test routing when query matches multiple capabilities."""
    router = SupervisorRouter()

    # This agent has 2 capabilities
    material_analyst = MockAgent(
        "material_analyst", {"match:materials", "optimize:carbon"}
    )
    # This agent has 1 capability
    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})

    router.register_agent(material_analyst)
    router.register_agent(carbon_calc)

    # Query matches both "optimize" and "material" keywords
    # material_analyst should win with 2 points vs carbon_calc with 0
    result = router.route("Find alternative materials to reduce carbon")

    assert result == "material_analyst"


def test_route_fallback_to_user_interaction():
    """Test fallback to user_interaction when no match."""
    router = SupervisorRouter()

    user_interaction = MockAgent("user_interaction", {"interact:user"})
    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})

    router.register_agent(user_interaction)
    router.register_agent(carbon_calc)

    # Query with no keyword matches
    result = router.route("xyz abc def")

    assert result == "user_interaction"


def test_route_fallback_when_no_user_interaction():
    """Test fallback when user_interaction not registered."""
    router = SupervisorRouter()

    agent1 = MockAgent("agent1", {"test:capability"})
    router.register_agent(agent1)

    # No keyword match and no user_interaction agent
    # Should fall back to any available agent
    result = router.route("random query")

    assert result == "agent1"


def test_route_no_agents_raises():
    """Test that routing with no agents raises ValueError."""
    router = SupervisorRouter()

    with pytest.raises(ValueError, match="No agents registered"):
        router.route("test query")


def test_get_agent():
    """Test retrieving agent by name."""
    router = SupervisorRouter()
    agent = MockAgent("test_agent", {"test:capability"})
    router.register_agent(agent)

    retrieved = router.get_agent("test_agent")

    assert retrieved is agent


def test_get_agent_not_found():
    """Test get_agent raises KeyError for unknown agent."""
    router = SupervisorRouter()

    with pytest.raises(KeyError):
        router.get_agent("nonexistent")


def test_list_capabilities():
    """Test listing all capabilities."""
    router = SupervisorRouter()

    agent1 = MockAgent("agent1", {"cap1", "cap2"})
    agent2 = MockAgent("agent2", {"cap2", "cap3"})

    router.register_agent(agent1)
    router.register_agent(agent2)

    capabilities = router.list_capabilities()

    assert set(capabilities.keys()) == {"cap1", "cap2", "cap3"}
    assert capabilities["cap1"] == ["agent1"]
    assert set(capabilities["cap2"]) == {"agent1", "agent2"}
    assert capabilities["cap3"] == ["agent2"]


def test_explain_routing():
    """Test explain_routing provides transparency."""
    router = SupervisorRouter()

    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})
    material_analyst = MockAgent("material_analyst", {"match:materials"})

    router.register_agent(carbon_calc)
    router.register_agent(material_analyst)

    # Query: "Calculate carbon footprint for materials"
    # Matches: "calculate" + "carbon" → calculate:carbon → carbon_calculator (1 point)
    #          "materials" → match:materials → material_analyst (1 point)
    # Both agents tied, so first registered wins (carbon_calculator)
    explanation = router.explain_routing("Calculate the carbon footprint")

    # Should route to carbon_calculator (no "materials" keyword to cause tie)
    assert explanation["selected_agent"] == "carbon_calculator"
    assert "carbon_calculator" in explanation["scores"]
    assert explanation["scores"]["carbon_calculator"] >= 1
    assert "calculate:carbon" in explanation["matched_capabilities"]
    assert "calculate" in explanation["matched_keywords"] or "carbon" in explanation["matched_keywords"]


def test_explain_routing_no_match():
    """Test explain_routing when no capabilities match."""
    router = SupervisorRouter()

    user_interaction = MockAgent("user_interaction", {"interact:user"})
    router.register_agent(user_interaction)

    explanation = router.explain_routing("xyz abc def")

    assert explanation["selected_agent"] == "user_interaction"
    assert explanation["scores"] == {}
    assert explanation["matched_capabilities"] == []
    assert explanation["matched_keywords"] == []


def test_capability_keywords_coverage():
    """Test that CAPABILITY_KEYWORDS covers expected domains."""
    expected_capabilities = {
        'parse:boq',
        'match:materials',
        'calculate:carbon',
        'query:tgo',
        'query:kg',
        'reason:semantic',
        'optimize:carbon',
        'interact:user',
        'manage:scenario',
    }

    assert expected_capabilities <= set(CAPABILITY_KEYWORDS.keys())

    # Ensure each expected capability has at least one keyword mapped
    for cap in expected_capabilities:
        assert len(CAPABILITY_KEYWORDS[cap]) > 0, f"Capability '{cap}' has no keywords mapped"


def test_route_boq_parsing():
    """Test routing BOQ parsing queries."""
    router = SupervisorRouter()

    boq_parser = MockAgent("boq_parser", {"parse:boq"})
    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})

    router.register_agent(boq_parser)
    router.register_agent(carbon_calc)

    assert router.route("Parse this Excel file") == "boq_parser"
    assert router.route("Upload BOQ document") == "boq_parser"
    assert router.route("Extract materials from file") == "boq_parser"


def test_route_knowledge_graph_queries():
    """Test routing knowledge graph queries."""
    router = SupervisorRouter()

    kg_agent = MockAgent("knowledge_graph", {"query:kg", "reason:semantic"})
    tgo_agent = MockAgent("tgo_database", {"query:tgo"})

    router.register_agent(kg_agent)
    router.register_agent(tgo_agent)

    assert router.route("Query knowledge graph for TREES compliance") == "knowledge_graph"
    assert router.route("Run SPARQL query on ontology") == "knowledge_graph"
    assert router.route("Check semantic compliance") == "knowledge_graph"


def test_route_scenario_management():
    """Test routing scenario management queries."""
    router = SupervisorRouter()

    scenario_mgr = MockAgent("scenario_manager", {"manage:scenario"})
    carbon_calc = MockAgent("carbon_calculator", {"calculate:carbon"})

    router.register_agent(scenario_mgr)
    router.register_agent(carbon_calc)

    assert router.route("Compare scenarios") == "scenario_manager"
    assert router.route("Create what-if variant") == "scenario_manager"
    assert router.route("Fork this scenario") == "scenario_manager"


def test_route_case_insensitive():
    """Test that routing is case-insensitive."""
    router = SupervisorRouter()

    agent = MockAgent("agent", {"calculate:carbon"})
    router.register_agent(agent)

    # All these should match "calculate" keyword
    assert router.route("CALCULATE carbon") == "agent"
    assert router.route("Calculate Carbon") == "agent"
    assert router.route("calculate CARBON") == "agent"


def test_route_with_context_parameter():
    """Test that route() accepts optional context parameter."""
    router = SupervisorRouter()

    agent = MockAgent("agent", {"calculate:carbon"})
    router.register_agent(agent)

    # Context parameter is reserved for future use but should not error
    result = router.route("Calculate carbon", context={"user_id": "123"})

    assert result == "agent"

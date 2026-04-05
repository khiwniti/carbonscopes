"""Tests for Material Analyst Agent.

Tests cover:
- Agent initialization and inheritance
- Capability registration
- Material matching and alternatives finding
- Material ID extraction from queries
- Carbon reduction calculations
- Integration with Phase 2 material matching
- Mock mode operation (no GraphDB dependency)
"""

import pytest
from decimal import Decimal
from core.agents.material_analyst import MaterialAnalystAgent
from core.agents.base import Agent
from core.agents.state import AgentState


class TestMaterialAnalystAgent:
    """Test suite for MaterialAnalystAgent class."""

    def test_agent_inheritance(self):
        """Test that MaterialAnalystAgent properly inherits from Agent."""
        agent = MaterialAnalystAgent()
        assert isinstance(agent, Agent)
        assert agent.name == "material_analyst"

    def test_capabilities_registration(self):
        """Test that agent registers correct capabilities."""
        agent = MaterialAnalystAgent()
        capabilities = agent.get_capabilities()

        assert isinstance(capabilities, set)
        assert "match:materials" in capabilities
        assert "query:tgo" in capabilities
        assert "optimize:carbon" in capabilities
        assert len(capabilities) == 3

    @pytest.mark.asyncio
    async def test_execute_returns_alternatives_structure(self):
        """Test that execute() returns proper alternatives structure."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "Find alternatives for concrete",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # Verify structure
        assert isinstance(result, dict)
        assert "alternatives" in result
        assert "match_count" in result
        assert "confidence" in result
        assert "carbon_reduction_potential" in result
        assert "analysis_summary" in result

    @pytest.mark.asyncio
    async def test_execute_with_material_in_query(self):
        """Test execution when material is mentioned in query."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "What are alternatives for steel rebar?",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        assert result["match_count"] > 0
        assert len(result["alternatives"]) > 0
        assert result["confidence"] > 0
        assert isinstance(result["analysis_summary"], str)

    @pytest.mark.asyncio
    async def test_execute_with_boq_materials(self):
        """Test execution when BOQ materials are in task_results."""
        agent = MaterialAnalystAgent()
        boq_materials = [
            {
                "line_number": 1,
                "description_th": "คอนกรีตเสริมเหล็ก",
                "description_en": "Reinforced Concrete",
                "quantity": 100.5,
                "unit": "m³",
                "unit_raw": "ลบ.ม.",
            },
            {
                "line_number": 2,
                "description_th": "เหล็กเสริม",
                "description_en": "Steel Reinforcement",
                "quantity": 5000.0,
                "unit": "kg",
                "unit_raw": "กก.",
            },
        ]

        state = {
            "user_query": "Analyze BOQ materials",
            "current_agent": "material_analyst",
            "agent_history": ["boq_parser"],
            "task_results": {"boq_materials": boq_materials},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # In mock mode, should still return results
        assert result["match_count"] >= 0
        assert isinstance(result["alternatives"], list)
        assert result["confidence"] >= 0
        assert result["carbon_reduction_potential"] >= 0

    @pytest.mark.asyncio
    async def test_execute_with_no_material_context(self):
        """Test execution when no material context is available."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "Hello",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # Should return empty results gracefully
        assert result["match_count"] == 0
        assert len(result["alternatives"]) == 0
        assert result["confidence"] == 0
        assert "No alternative materials found" in result["analysis_summary"]

    def test_extract_material_id_concrete(self):
        """Test material ID extraction for concrete."""
        agent = MaterialAnalystAgent()
        material_id = agent._extract_material_id("Find alternatives for concrete")
        assert material_id == "concrete"

    def test_extract_material_id_steel(self):
        """Test material ID extraction for steel."""
        agent = MaterialAnalystAgent()
        material_id = agent._extract_material_id("What about steel reinforcement?")
        assert material_id == "steel"

    def test_extract_material_id_quoted(self):
        """Test material ID extraction from quoted strings."""
        agent = MaterialAnalystAgent()
        material_id = agent._extract_material_id('Find data for "recycled aggregate"')
        assert material_id == "recycled aggregate"

    def test_extract_material_id_tgo_format(self):
        """Test material ID extraction for TGO format IDs."""
        agent = MaterialAnalystAgent()
        material_id = agent._extract_material_id("Query tgo:concrete_c30 material")
        assert material_id == "tgo:concrete_c30"

    def test_extract_material_id_no_match(self):
        """Test material ID extraction when no material is mentioned."""
        agent = MaterialAnalystAgent()
        material_id = agent._extract_material_id("Hello, how are you?")
        assert material_id is None

    def test_extract_material_id_case_insensitive(self):
        """Test that material extraction is case-insensitive."""
        agent = MaterialAnalystAgent()
        assert agent._extract_material_id("CONCRETE analysis") == "concrete"
        assert agent._extract_material_id("Steel REBAR") == "steel"
        assert agent._extract_material_id("Aluminum frame") == "aluminum"

    @pytest.mark.asyncio
    async def test_find_alternatives_mock_mode(self):
        """Test _find_alternatives in mock mode (no GraphDB)."""
        agent = MaterialAnalystAgent(graphdb_client=None)
        alternatives = await agent._find_alternatives("concrete")

        assert isinstance(alternatives, list)
        assert len(alternatives) > 0

        # Check structure of mock alternatives
        for alt in alternatives:
            assert "material_id" in alt
            assert "label" in alt
            assert "confidence" in alt
            assert "emission_factor" in alt
            assert "carbon_reduction" in alt

    def test_rank_by_carbon_reduction(self):
        """Test ranking of alternatives by carbon reduction."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"material_id": "a", "emission_factor": 300.0, "confidence": 0.9},
            {"material_id": "b", "emission_factor": 200.0, "confidence": 0.8},
            {"material_id": "c", "emission_factor": 100.0, "confidence": 0.7},
        ]

        ranked = agent._rank_by_carbon_reduction(alternatives)

        # Should be sorted by carbon reduction (lowest emission first)
        assert ranked[0]["material_id"] == "c"  # Lowest emission
        assert ranked[1]["material_id"] == "b"
        assert ranked[2]["material_id"] == "a"  # Highest emission

        # Check carbon reduction scores are added
        assert "carbon_reduction" in ranked[0]
        assert ranked[0]["carbon_reduction"] > ranked[1]["carbon_reduction"]
        assert ranked[1]["carbon_reduction"] > ranked[2]["carbon_reduction"]

    def test_rank_by_carbon_reduction_empty_list(self):
        """Test ranking with empty alternatives list."""
        agent = MaterialAnalystAgent()
        ranked = agent._rank_by_carbon_reduction([])
        assert ranked == []

    def test_calculate_carbon_reduction(self):
        """Test carbon reduction calculation."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"carbon_reduction": 30.0},
            {"carbon_reduction": 20.0},
            {"carbon_reduction": 10.0},
        ]

        avg_reduction = agent._calculate_carbon_reduction(alternatives)
        assert avg_reduction == 20.0

    def test_calculate_carbon_reduction_empty(self):
        """Test carbon reduction with no alternatives."""
        agent = MaterialAnalystAgent()
        avg_reduction = agent._calculate_carbon_reduction([])
        assert avg_reduction == 0.0

    def test_calculate_carbon_reduction_missing_values(self):
        """Test carbon reduction with missing values."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"carbon_reduction": 30.0},
            {"other_field": "value"},  # Missing carbon_reduction
            {"carbon_reduction": 10.0},
        ]

        avg_reduction = agent._calculate_carbon_reduction(alternatives)
        assert avg_reduction == 20.0  # Average of 30 and 10

    def test_generate_summary_significant_reduction(self):
        """Test summary generation for significant carbon reduction."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"confidence": 0.9, "carbon_reduction": 25.0},
            {"confidence": 0.85, "carbon_reduction": 30.0},
        ]

        summary = agent._generate_summary(alternatives, 27.5)

        assert "2 alternative materials" in summary
        assert "significant carbon reduction" in summary
        assert "27.5%" in summary

    def test_generate_summary_moderate_reduction(self):
        """Test summary generation for moderate carbon reduction."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"confidence": 0.7, "carbon_reduction": 15.0},
        ]

        summary = agent._generate_summary(alternatives, 15.0)

        assert "1 alternative" in summary
        assert "moderate carbon reduction" in summary

    def test_generate_summary_minor_reduction(self):
        """Test summary generation for minor carbon reduction."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"confidence": 0.6, "carbon_reduction": 5.0},
        ]

        summary = agent._generate_summary(alternatives, 5.0)

        assert "minor carbon reduction" in summary

    def test_generate_summary_no_alternatives(self):
        """Test summary generation when no alternatives found."""
        agent = MaterialAnalystAgent()
        summary = agent._generate_summary([], 0.0)
        assert summary == "No alternative materials found"

    def test_generate_summary_high_confidence_count(self):
        """Test that summary reports high-confidence matches."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"confidence": 0.95, "carbon_reduction": 20.0},  # High
            {"confidence": 0.85, "carbon_reduction": 15.0},  # High
            {"confidence": 0.70, "carbon_reduction": 10.0},  # Not high
        ]

        summary = agent._generate_summary(alternatives, 15.0)
        assert "2 high-confidence matches" in summary

    def test_get_mock_alternatives(self):
        """Test mock alternatives generation."""
        agent = MaterialAnalystAgent()
        alternatives = agent._get_mock_alternatives("concrete")

        assert len(alternatives) > 0
        assert all("material_id" in alt for alt in alternatives)
        assert all("label" in alt for alt in alternatives)
        assert all("confidence" in alt for alt in alternatives)
        assert all("emission_factor" in alt for alt in alternatives)
        assert all("carbon_reduction" in alt for alt in alternatives)
        assert all(alt["source"] == "mock" for alt in alternatives)

    def test_get_mock_alternatives_material_specific(self):
        """Test that mock alternatives include material-specific IDs."""
        agent = MaterialAnalystAgent()
        alternatives = agent._get_mock_alternatives("steel")

        # Check that material ID includes the input material
        assert any("steel" in alt["material_id"].lower() for alt in alternatives)
        assert any("Steel" in alt["label"] for alt in alternatives)

    @pytest.mark.asyncio
    async def test_alternatives_limited_to_top_10(self):
        """Test that execute() returns maximum 10 alternatives."""
        agent = MaterialAnalystAgent()

        # Create state that would generate alternatives
        state = {
            "user_query": "Find alternatives for concrete",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # Even if more alternatives exist, should return max 10
        assert len(result["alternatives"]) <= 10

    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self):
        """Test that average confidence is calculated correctly."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "alternatives for timber",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # Confidence should be between 0 and 1
        assert 0.0 <= result["confidence"] <= 1.0

        # If alternatives exist, confidence should be rounded to 2 decimals
        if result["match_count"] > 0:
            assert len(str(result["confidence"]).split(".")[-1]) <= 2

    @pytest.mark.asyncio
    async def test_carbon_reduction_rounded(self):
        """Test that carbon reduction is rounded to 2 decimals."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "optimize aluminum",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {},
            "error_count": 0,
            "scenario_context": None,
        }

        result = await agent.execute(state)

        # Carbon reduction should be rounded
        reduction_str = str(result["carbon_reduction_potential"])
        if "." in reduction_str:
            decimals = len(reduction_str.split(".")[-1])
            assert decimals <= 2


class TestMaterialAnalystIntegration:
    """Integration tests with fixtures from conftest.py."""

    @pytest.mark.asyncio
    async def test_with_initial_state_fixture(self, initial_state):
        """Test agent execution with initial_state fixture."""
        agent = MaterialAnalystAgent()
        # Modify initial state for material analysis
        initial_state["user_query"] = "Find concrete alternatives"

        result = await agent.execute(initial_state)

        assert isinstance(result, dict)
        assert "alternatives" in result

    @pytest.mark.asyncio
    async def test_agent_with_history(self, initial_state):
        """Test agent execution with agent history populated."""
        agent = MaterialAnalystAgent()
        initial_state["user_query"] = "material alternatives"
        initial_state["agent_history"] = ["boq_parser"]
        initial_state["task_results"] = {
            "boq_materials": [
                {
                    "line_number": 1,
                    "description_th": "คอนกรีต",
                    "quantity": 100,
                    "unit": "m³",
                    "unit_raw": "ลบ.ม.",
                }
            ]
        }

        result = await agent.execute(initial_state)

        # Should handle BOQ materials from previous agent
        assert isinstance(result["alternatives"], list)
        assert result["match_count"] >= 0


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_handles_invalid_state_gracefully(self):
        """Test that agent handles invalid state without crashing."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": None,  # Invalid
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": None,  # Invalid
            "error_count": 0,
            "scenario_context": None,
        }

        # Should not raise exception
        result = await agent.execute(state)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_handles_malformed_boq_materials(self):
        """Test handling of malformed BOQ materials."""
        agent = MaterialAnalystAgent()
        state = {
            "user_query": "analyze materials",
            "current_agent": "material_analyst",
            "agent_history": [],
            "task_results": {
                "boq_materials": [
                    {"invalid": "structure"},  # Missing required fields
                    None,  # Invalid entry
                ]
            },
            "error_count": 0,
            "scenario_context": None,
        }

        # Should handle gracefully
        result = await agent.execute(state)
        assert isinstance(result, dict)
        assert result["match_count"] >= 0

    def test_rank_with_missing_emission_factors(self):
        """Test ranking when some alternatives have missing emission factors."""
        agent = MaterialAnalystAgent()
        alternatives = [
            {"material_id": "a", "emission_factor": 300.0},
            {"material_id": "b"},  # Missing emission_factor
            {"material_id": "c", "emission_factor": 100.0},
        ]

        # Should not crash
        ranked = agent._rank_by_carbon_reduction(alternatives)
        assert isinstance(ranked, list)
        assert len(ranked) == 3

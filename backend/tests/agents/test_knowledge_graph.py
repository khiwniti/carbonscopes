"""Tests for KnowledgeGraphAgent — new query types: carbon_credit_eligibility,
epd_search, and material_lifecycle.
"""

import pytest
from core.agents.knowledge_graph import KnowledgeGraphAgent
from core.agents.state import AgentState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_state(query: str, task_results: dict | None = None) -> AgentState:
    """Build a minimal AgentState for testing."""
    return {  # type: ignore[return-value]
        "user_query": query,
        "current_agent": "knowledge_graph",
        "agent_history": [],
        "task_results": task_results or {},
        "error_count": 0,
        "scenario_context": None,
        "pipeline_queue": None,
    }


# ---------------------------------------------------------------------------
# _classify_query — new keywords
# ---------------------------------------------------------------------------

class TestClassifyQueryNewTypes:
    """_classify_query correctly identifies the three new query types."""

    def test_carbon_credit_keyword_carbon_credit(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Check carbon credit eligibility") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_vcs(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Does this project qualify for VCS?") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_gold_standard(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Gold Standard certification check") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_offset(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("What is the carbon offset potential?") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_additionality(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Assess additionality for this project") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_permanence(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Evaluate permanence risk") == "carbon_credit_eligibility"

    def test_carbon_credit_keyword_redd(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Is this project REDD+ eligible?") == "carbon_credit_eligibility"

    def test_epd_search_keyword_epd(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Find EPD for this concrete") == "epd_search"

    def test_epd_search_keyword_environmental_product_declaration(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Search environmental product declaration database") == "epd_search"

    def test_epd_search_keyword_declared_unit(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("What is the declared unit?") == "epd_search"

    def test_epd_search_keyword_pcr(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Which PCR applies to this product?") == "epd_search"

    def test_epd_search_keyword_gwp(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Get GWP value for steel") == "epd_search"

    def test_lifecycle_keyword_lifecycle(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Show lifecycle data for concrete") == "material_lifecycle"

    def test_lifecycle_keyword_life_cycle(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Life cycle assessment for concrete C30") == "material_lifecycle"

    def test_lifecycle_keyword_cradle_to_gate(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("Cradle to gate emissions for rebar") == "material_lifecycle"

    def test_lifecycle_keyword_en15978(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("EN 15978 module breakdown") == "material_lifecycle"

    def test_lifecycle_keyword_a1(self):
        agent = KnowledgeGraphAgent()
        assert agent._classify_query("What are A1 emissions?") == "material_lifecycle"


# ---------------------------------------------------------------------------
# _check_carbon_credit_eligibility — mock mode
# ---------------------------------------------------------------------------

class TestCarbonCreditEligibility:
    """Carbon credit eligibility checks in mock mode."""

    @pytest.mark.asyncio
    async def test_returns_correct_query_type(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit check", {})
        assert result["query_type"] == "carbon_credit_eligibility"

    @pytest.mark.asyncio
    async def test_mock_mode_eligible(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("VCS credit eligibility", {})
        assert result["eligible"] is True

    @pytest.mark.asyncio
    async def test_mock_mode_standard_is_vcs(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("VCS offset", {})
        assert result["standard"] == "VCS"

    @pytest.mark.asyncio
    async def test_mock_mode_additionality_score(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("additionality check", {})
        assert isinstance(result["additionality_score"], float)
        assert 0.0 <= result["additionality_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_mock_mode_estimated_credits(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit", {})
        assert result["estimated_credits_tco2e"] == pytest.approx(375.0, abs=0.1)

    @pytest.mark.asyncio
    async def test_mock_mode_baseline_greater_than_project(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit", {})
        assert result["baseline_emissions_tco2e"] > result["project_emissions_tco2e"]

    @pytest.mark.asyncio
    async def test_mock_mode_permanence_risk_valid(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("permanence check", {})
        assert result["permanence_risk"] in ("low", "medium", "high")

    @pytest.mark.asyncio
    async def test_mock_mode_co_benefits_list(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit", {})
        assert isinstance(result["co_benefits"], list)

    @pytest.mark.asyncio
    async def test_mock_mode_requirements_met_list(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit", {})
        assert isinstance(result["requirements_met"], list)

    @pytest.mark.asyncio
    async def test_mock_mode_details_string(self):
        agent = KnowledgeGraphAgent()
        result = await agent._check_carbon_credit_eligibility("carbon credit", {})
        assert isinstance(result["details"], str)
        assert len(result["details"]) > 0

    @pytest.mark.asyncio
    async def test_execute_dispatches_carbon_credit(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Check carbon credit eligibility for our project")
        result = await agent.execute(state)
        assert result["query_type"] == "carbon_credit_eligibility"


# ---------------------------------------------------------------------------
# _search_epd — mock mode
# ---------------------------------------------------------------------------

class TestEpdSearch:
    """EPD search in mock mode."""

    @pytest.mark.asyncio
    async def test_returns_correct_query_type(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("Find EPD for concrete", {})
        assert result["query_type"] == "epd_search"

    @pytest.mark.asyncio
    async def test_mock_mode_two_epds_returned(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD search", {})
        assert result["total_found"] == 2
        assert len(result["epds_found"]) == 2

    @pytest.mark.asyncio
    async def test_mock_mode_epd_has_required_keys(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD for steel", {})
        required_keys = {
            "epd_id", "material_name", "manufacturer", "declared_unit",
            "gwp_a1_a3_kgco2e", "gwp_total_kgco2e", "lifecycle_stages",
            "validity_date", "program_operator", "verified",
        }
        for epd in result["epds_found"]:
            assert required_keys.issubset(epd.keys()), (
                f"EPD missing keys: {required_keys - epd.keys()}"
            )

    @pytest.mark.asyncio
    async def test_mock_mode_coverage_in_range(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD search", {})
        assert 0.0 <= result["coverage"] <= 1.0

    @pytest.mark.asyncio
    async def test_mock_mode_gwp_values_positive(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD", {})
        for epd in result["epds_found"]:
            assert epd["gwp_a1_a3_kgco2e"] > 0
            assert epd["gwp_total_kgco2e"] > 0

    @pytest.mark.asyncio
    async def test_mock_mode_verified_boolean(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD", {})
        for epd in result["epds_found"]:
            assert isinstance(epd["verified"], bool)

    @pytest.mark.asyncio
    async def test_mock_mode_lifecycle_stages_list(self):
        agent = KnowledgeGraphAgent()
        result = await agent._search_epd("EPD", {})
        for epd in result["epds_found"]:
            assert isinstance(epd["lifecycle_stages"], list)

    @pytest.mark.asyncio
    async def test_mock_mode_uses_boq_materials_for_coverage(self):
        agent = KnowledgeGraphAgent()
        task_results = {"boq_materials": ["concrete", "steel", "timber", "glass"]}
        result = await agent._search_epd("EPD search", task_results)
        # 2 EPDs found against 4 materials → coverage = 0.5
        assert result["coverage"] == pytest.approx(0.5, abs=0.01)

    @pytest.mark.asyncio
    async def test_execute_dispatches_epd_search(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Search EPD for concrete materials")
        result = await agent.execute(state)
        assert result["query_type"] == "epd_search"

    @pytest.mark.asyncio
    async def test_execute_dispatches_gwp_keyword(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("What is the GWP of this product?")
        result = await agent.execute(state)
        assert result["query_type"] == "epd_search"


# ---------------------------------------------------------------------------
# _query_material_lifecycle — mock mode
# ---------------------------------------------------------------------------

class TestMaterialLifecycle:
    """Material lifecycle queries in mock mode."""

    @pytest.mark.asyncio
    async def test_returns_correct_query_type(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle of concrete", {})
        assert result["query_type"] == "material_lifecycle"

    @pytest.mark.asyncio
    async def test_mock_mode_has_all_lifecycle_stage_keys(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        expected_keys = {
            "A1_raw_material_supply", "A2_transport_to_factory", "A3_manufacturing",
            "A1_A3_total", "A4_transport_to_site", "A5_installation",
            "B1_B7_use_phase", "C1_deconstruction", "C2_transport_to_waste",
            "C3_waste_processing", "C4_disposal", "D_reuse_recovery",
        }
        assert expected_keys.issubset(result["lifecycle_stages"].keys())

    @pytest.mark.asyncio
    async def test_mock_mode_has_grouped_aggregate_keys(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        # Check both granular and grouped keys present
        assert "A1_raw_material_supply" in result["lifecycle_stages"]
        assert "A1-A3" in result["lifecycle_stages"]
        assert "A4-A5" in result["lifecycle_stages"]
        assert "B1-B7" in result["lifecycle_stages"]
        assert "C1-C4" in result["lifecycle_stages"]
        assert "D" in result["lifecycle_stages"]

    @pytest.mark.asyncio
    async def test_mock_mode_total_gwp_numeric(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        assert isinstance(result["total_gwp_kgco2e"], (int, float))

    @pytest.mark.asyncio
    async def test_mock_mode_standard_en15978(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        assert result["standard"] == "EN 15978:2011"

    @pytest.mark.asyncio
    async def test_mock_mode_reference_service_life(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        assert result["reference_service_life_years"] == 50

    @pytest.mark.asyncio
    async def test_mock_mode_functional_unit_string(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        assert isinstance(result["functional_unit"], str)
        assert "m³" in result["functional_unit"]

    @pytest.mark.asyncio
    async def test_mock_mode_d_stage_can_be_negative(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        d_val = result["lifecycle_stages"]["D_reuse_recovery"]["gwp_kgco2e"]
        assert d_val < 0  # recovery benefit should be negative

    @pytest.mark.asyncio
    async def test_mock_mode_a1_a3_total_approximately_sum(self):
        agent = KnowledgeGraphAgent()
        result = await agent._query_material_lifecycle("lifecycle", {})
        stages = result["lifecycle_stages"]
        a1 = stages["A1_raw_material_supply"]["gwp_kgco2e"]
        a2 = stages["A2_transport_to_factory"]["gwp_kgco2e"]
        a3 = stages["A3_manufacturing"]["gwp_kgco2e"]
        total = stages["A1_A3_total"]["gwp_kgco2e"]
        assert abs((a1 + a2 + a3) - total) < 1.0

    @pytest.mark.asyncio
    async def test_execute_dispatches_lifecycle(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Show lifecycle data for concrete C30")
        result = await agent.execute(state)
        assert result["query_type"] == "material_lifecycle"

    @pytest.mark.asyncio
    async def test_execute_dispatches_en15978_keyword(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("EN 15978 module breakdown for steel")
        result = await agent.execute(state)
        assert result["query_type"] == "material_lifecycle"

    @pytest.mark.asyncio
    async def test_execute_dispatches_cradle_to_gate(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Cradle to gate emissions for rebar")
        result = await agent.execute(state)
        assert result["query_type"] == "material_lifecycle"


# ---------------------------------------------------------------------------
# Existing query types still work (regression)
# ---------------------------------------------------------------------------

class TestExistingQueryTypesRegression:
    """Ensure existing query types are not broken."""

    @pytest.mark.asyncio
    async def test_trees_mr1_still_works(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Check trees mr1 recycled content")
        result = await agent.execute(state)
        assert result["query_type"] == "trees_mr1_eligibility"

    @pytest.mark.asyncio
    async def test_trees_mr3_still_works(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Check trees mr3 sustainable materials")
        result = await agent.execute(state)
        assert result["query_type"] == "trees_mr3_eligibility"

    @pytest.mark.asyncio
    async def test_edge_certification_still_works(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("EDGE certification check")
        result = await agent.execute(state)
        assert result["query_type"] == "edge_certification"

    @pytest.mark.asyncio
    async def test_material_classification_still_works(self):
        agent = KnowledgeGraphAgent()
        state = _make_state("Classify this material")
        result = await agent.execute(state)
        assert result["query_type"] == "material_classification"

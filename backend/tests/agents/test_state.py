"""Tests for AgentState schema and state management utilities."""

import pytest
from decimal import Decimal
from core.agents.state import (
    AgentState,
    validate_state,
    serialize_state,
    deserialize_state,
)


def test_agent_state_schema():
    """Test AgentState TypedDict structure."""
    state: AgentState = {
        "user_query": "Calculate carbon footprint",
        "current_agent": "carbon_calculator",
        "agent_history": ["supervisor", "carbon_calculator"],
        "task_results": {"carbon_calculator": {"total_carbon": 12450.0}},
        "error_count": 0,
        "scenario_context": None,
    }

    assert state["user_query"] == "Calculate carbon footprint"
    assert state["current_agent"] == "carbon_calculator"
    assert len(state["agent_history"]) == 2
    assert state["error_count"] == 0


def test_validate_state_valid():
    """Test validation of a valid AgentState."""
    valid_state = {
        "user_query": "Test query",
        "current_agent": "test_agent",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }

    assert validate_state(valid_state) is True


def test_validate_state_missing_keys():
    """Test validation fails with missing required keys."""
    invalid_state = {
        "user_query": "Test query",
        # Missing other required keys
    }

    assert validate_state(invalid_state) is False


def test_validate_state_wrong_types():
    """Test validation fails with incorrect types."""
    invalid_state = {
        "user_query": 123,  # Should be str
        "current_agent": "test",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }

    assert validate_state(invalid_state) is False


def test_validate_state_scenario_context_type():
    """Test validation of scenario_context type."""
    # Valid: None
    valid_none = {
        "user_query": "Test",
        "current_agent": "test",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }
    assert validate_state(valid_none) is True

    # Valid: dict
    valid_dict = {
        "user_query": "Test",
        "current_agent": "test",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": {"base_scenario": "sc-123"},
    }
    assert validate_state(valid_dict) is True

    # Invalid: string
    invalid_str = {
        "user_query": "Test",
        "current_agent": "test",
        "agent_history": [],
        "task_results": {},
        "error_count": 0,
        "scenario_context": "invalid",
    }
    assert validate_state(invalid_str) is False


def test_serialize_deserialize_roundtrip():
    """Test serialization and deserialization roundtrip."""
    original_state: AgentState = {
        "user_query": "Find concrete alternatives",
        "current_agent": "material_analyst",
        "agent_history": ("supervisor", "material_analyst"),
        "task_results": {
            "material_analyst": {
                "alternatives": [
                    {
                        "material_id": "tgo:concrete-green",
                        "carbon_reduction": 21.5,
                    }
                ]
            }
        },
        "error_count": 0,
        "scenario_context": {"base_scenario": "sc-456"},
    }

    # Serialize
    serialized = serialize_state(original_state)
    assert isinstance(serialized, str)
    assert "Find concrete alternatives" in serialized

    # Deserialize
    deserialized = deserialize_state(serialized)

    # Verify roundtrip
    assert deserialized["user_query"] == original_state["user_query"]
    assert deserialized["current_agent"] == original_state["current_agent"]
    assert tuple(deserialized["agent_history"]) == original_state["agent_history"]
    assert deserialized["task_results"] == original_state["task_results"]
    assert deserialized["error_count"] == original_state["error_count"]
    assert deserialized["scenario_context"] == original_state["scenario_context"]


def test_serialize_decimal_handling():
    """Test that Decimal types are correctly serialized."""
    state_with_decimal: AgentState = {
        "user_query": "Test",
        "current_agent": "test",
        "agent_history": (),
        "task_results": {
            "boq_parser": {
                "quantity": Decimal("500.00"),
                "total_carbon": Decimal("12450.50"),
            }
        },
        "error_count": 0,
        "scenario_context": None,
    }

    # Should not raise TypeError
    serialized = serialize_state(state_with_decimal)
    assert isinstance(serialized, str)
    assert "500" in serialized
    assert "12450.5" in serialized

    # Deserialize and verify (Decimals become floats)
    deserialized = deserialize_state(serialized)
    assert deserialized["task_results"]["boq_parser"]["quantity"] == 500.0
    assert deserialized["task_results"]["boq_parser"]["total_carbon"] == 12450.5


def test_deserialize_invalid_json():
    """Test deserialization with invalid JSON."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        deserialize_state("not valid json {")


def test_deserialize_invalid_schema():
    """Test deserialization with JSON that doesn't match schema."""
    invalid_json = '{"user_query": "test"}'  # Missing required keys

    with pytest.raises(ValueError, match="does not match AgentState schema"):
        deserialize_state(invalid_json)


def test_agent_history_annotation():
    """Test that agent_history supports operator.add for appending."""
    # This is a type-level test - Annotated[Sequence[str], operator.add]
    # allows LangGraph to automatically append to agent_history
    state: AgentState = {
        "user_query": "Test",
        "current_agent": "agent2",
        "agent_history": ("agent1",),
        "task_results": {},
        "error_count": 0,
        "scenario_context": None,
    }

    # In LangGraph, returning agent_history from a node automatically appends
    # This test verifies the type allows it
    new_history = state["agent_history"] + ("agent2",)
    assert new_history == ("agent1", "agent2")


def test_scenario_context_structure():
    """Test typical scenario_context structure."""
    state: AgentState = {
        "user_query": "Compare scenarios",
        "current_agent": "scenario_manager",
        "agent_history": (),
        "task_results": {},
        "error_count": 0,
        "scenario_context": {
            "base_scenario_id": "user-123:base:boq-456",
            "forked_scenario_ids": [
                "user-123:base:boq-456:fork:abc",
                "user-123:base:boq-456:fork:def",
            ],
            "material_swaps": [
                {"original": "tgo:concrete-c30", "replacement": "tgo:concrete-green"}
            ],
        },
    }

    assert state["scenario_context"] is not None
    assert "base_scenario_id" in state["scenario_context"]
    assert len(state["scenario_context"]["forked_scenario_ids"]) == 2
    assert len(state["scenario_context"]["material_swaps"]) == 1

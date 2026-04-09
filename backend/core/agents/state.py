"""LangGraph AgentState schema and state management utilities.

This module defines the state structure shared across all agents in the
multi-agent system, plus serialization/deserialization for checkpointing.
"""

from typing import TypedDict, Sequence, Dict, Any, Optional, Annotated
import operator
import json
from decimal import Decimal


class AgentState(TypedDict):
    """State shared across all agents in the LangGraph system.

    Attributes:
        user_query: Original user query or task description
        current_agent: Name of the currently active agent
        agent_history: Sequential list of agents invoked (supports append via operator.add)
        task_results: Dictionary mapping agent names to their execution results
        error_count: Number of errors encountered during execution
        scenario_context: Optional dictionary with scenario comparison state
        pipeline_queue: Ordered list of remaining agent names in a multi-agent pipeline.
                        Populated by supervisor_node when a complex query is detected.
                        Each agent pops itself from the front when it runs.
    """
    user_query: str
    current_agent: str
    agent_history: Annotated[Sequence[str], operator.add]
    task_results: Dict[str, Any]
    error_count: int
    scenario_context: Optional[Dict[str, Any]]
    pipeline_queue: Optional[Sequence[str]]


def validate_state(state: Dict[str, Any]) -> bool:
    """Validate that a state dictionary conforms to AgentState schema.

    Args:
        state: Dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    required_keys = {
        "user_query",
        "current_agent",
        "agent_history",
        "task_results",
        "error_count",
        "scenario_context",
    }

    if not isinstance(state, dict):
        return False

    if not required_keys.issubset(state.keys()):
        return False

    # Type checks
    if not isinstance(state["user_query"], str):
        return False
    if not isinstance(state["current_agent"], str):
        return False
    if not isinstance(state["agent_history"], (list, tuple)):
        return False
    if not isinstance(state["task_results"], dict):
        return False
    if not isinstance(state["error_count"], int):
        return False
    if state["scenario_context"] is not None and not isinstance(
        state["scenario_context"], dict
    ):
        return False
    # pipeline_queue is optional
    pq = state.get("pipeline_queue")
    if pq is not None and not isinstance(pq, (list, tuple)):
        return False

    return True


def serialize_state(state: AgentState) -> str:
    """Serialize AgentState to JSON string for checkpointing.

    Handles Decimal serialization for BOQ quantities and carbon calculations.

    Args:
        state: AgentState instance to serialize

    Returns:
        JSON string representation of state
    """

    def decimal_encoder(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return json.dumps(dict(state), default=decimal_encoder, ensure_ascii=False)


def deserialize_state(data: str) -> AgentState:
    """Deserialize JSON string back to AgentState.

    Args:
        data: JSON string from serialize_state()

    Returns:
        AgentState instance

    Raises:
        ValueError: If data is not valid JSON or doesn't match AgentState schema
    """
    try:
        state_dict = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    if not validate_state(state_dict):
        raise ValueError("Deserialized data does not match AgentState schema")

    # Convert agent_history back to tuple (TypedDict expects Sequence)
    state_dict["agent_history"] = tuple(state_dict["agent_history"])

    return state_dict  # type: ignore

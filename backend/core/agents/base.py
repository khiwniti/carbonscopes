"""Base agent class for LangGraph multi-agent system.

This module provides the abstract base class that all specialist agents inherit from,
with standardized execute interface and observability hooks.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, Any
from .state import AgentState
import time
import logging


class Agent(ABC):
    """Abstract base class for all specialist agents in the system.

    All agents must:
    1. Declare their capability tags (e.g., "parse:boq", "calculate:carbon")
    2. Implement async execute(state) -> result
    3. Handle errors gracefully with fallback behavior

    Attributes:
        name: Unique agent identifier (e.g., "material_analyst")
        capabilities: Set of capability tags for routing
        logger: Structured logger for agent actions
    """

    def __init__(self, name: str, capabilities: Set[str]):
        """Initialize agent with name and capabilities.

        Args:
            name: Unique agent identifier
            capabilities: Set of capability tags (e.g., {"match:materials", "optimize:materials"})
        """
        self.name = name
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute agent logic based on current state.

        This method must be implemented by all subclasses. It receives the current
        AgentState and returns a dictionary of results that will be merged into
        task_results.

        Args:
            state: Current AgentState with user_query, agent_history, task_results, etc.

        Returns:
            Dictionary with agent execution results. Keys should be descriptive of
            the result type (e.g., {"materials_matched": [...], "confidence": 0.92})

        Raises:
            Exception: If execution fails. The supervisor will catch this and
                       increment error_count in state.

        Example:
            ```python
            class MaterialAnalystAgent(Agent):
                async def execute(self, state: AgentState) -> Dict[str, Any]:
                    materials = state["task_results"]["boq_materials"]
                    matches = await self.match_materials(materials)
                    return {
                        "materials_matched": matches,
                        "match_count": len(matches),
                        "confidence": 0.95
                    }
            ```
        """
        pass

    def get_capabilities(self) -> Set[str]:
        """Return agent's capability tags for routing.

        Returns:
            Set of capability tags (e.g., {"parse:boq", "match:materials"})
        """
        return self.capabilities

    async def execute_with_metrics(self, state: AgentState) -> Dict[str, Any]:
        """Execute agent with timing and error tracking.

        This wrapper around execute() provides:
        - Execution timing (duration_ms)
        - Structured logging
        - Error tracking

        This method is called by the supervisor, not by agent implementations.

        Args:
            state: Current AgentState

        Returns:
            Dictionary with:
                - result: Agent execution results from execute()
                - duration_ms: Execution time in milliseconds
                - agent_name: Name of this agent
                - status: "success" or "error"

        Raises:
            Exception: If execute() fails, re-raises after logging
        """
        start = time.time()

        try:
            result = await self.execute(state)
            duration = (time.time() - start) * 1000  # Convert to milliseconds

            self.logger.info(
                f"{self.name} executed successfully",
                extra={
                    "agent_name": self.name,
                    "duration_ms": duration,
                    "result_keys": list(result.keys()),
                    "user_query": state.get("user_query", ""),
                },
            )

            return {
                "result": result,
                "duration_ms": duration,
                "agent_name": self.name,
                "status": "success",
            }

        except Exception as e:
            duration = (time.time() - start) * 1000

            self.logger.error(
                f"{self.name} execution failed",
                extra={
                    "agent_name": self.name,
                    "duration_ms": duration,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "user_query": state.get("user_query", ""),
                },
                exc_info=True,
            )

            # Re-raise for supervisor to handle
            raise


class AgentRegistry:
    """Registry for managing all specialist agents in the system.

    The supervisor uses this registry to:
    1. Look up agents by name
    2. Find agents with specific capabilities
    3. Get agent metadata for observability

    This is a singleton pattern - there should be one registry per application.
    """

    def __init__(self):
        """Initialize empty agent registry."""
        self.agents: Dict[str, Agent] = {}
        self.capability_index: Dict[str, Set[str]] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register an agent and index its capabilities.

        Args:
            agent: Agent instance to register

        Raises:
            ValueError: If agent with same name already registered
        """
        if agent.name in self.agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")

        self.agents[agent.name] = agent

        # Index capabilities
        for capability in agent.get_capabilities():
            if capability not in self.capability_index:
                self.capability_index[capability] = set()
            self.capability_index[capability].add(agent.name)

    def get_agent(self, name: str) -> Agent:
        """Get agent by name.

        Args:
            name: Agent name (e.g., "material_analyst")

        Returns:
            Agent instance

        Raises:
            KeyError: If agent not found
        """
        return self.agents[name]

    def get_agents_with_capability(self, capability: str) -> Set[str]:
        """Find all agent names with a specific capability.

        Args:
            capability: Capability tag (e.g., "match:materials")

        Returns:
            Set of agent names with this capability
        """
        return self.capability_index.get(capability, set())

    def list_agents(self) -> Dict[str, Set[str]]:
        """List all registered agents with their capabilities.

        Returns:
            Dictionary mapping agent names to their capability sets
        """
        return {name: agent.get_capabilities() for name, agent in self.agents.items()}

    def count(self) -> int:
        """Return number of registered agents.

        Returns:
            Agent count
        """
        return len(self.agents)

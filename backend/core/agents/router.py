"""Capability-based routing for multi-agent system.

This module implements the routing logic used by the supervisor to select
which agent should handle a given query based on capability matching.
"""

from typing import Dict, List
from .base import Agent


# Capability keyword mapping for query analysis
# Each capability maps to keywords that indicate the need for that capability
CAPABILITY_KEYWORDS = {
    # Original 5 agent capabilities
    'parse:boq': ['parse', 'boq', 'excel', 'file', 'upload', 'extract'],
    'match:materials': ['match', 'material', 'find', 'identify', 'map'],
    'calculate:carbon': ['calculate', 'carbon', 'footprint', 'emission', 'co2', 'ghg'],
    'query:tgo': ['tgo', 'database', 'emission factor', 'lookup', 'fetch', 'query tgo'],
    'query:kg': ['sparql', 'knowledge graph', 'ontology'],
    'reason:semantic': ['reasoning', 'semantic'],
    'validate:compliance': ['compliance', 'trees', 'edge', 'check trees', 'check edge', 'certification'],
    'interact:user': ['question', 'explain', 'chat', 'help', 'what can i do'],
    # 6 additional agent capabilities (Plan 03-03)
    'optimize:carbon': ['optimize', 'optimization', 'strategies', 'reduce'],
    'recommend:strategies': ['recommend', 'strategies', 'strategy', 'suggestion'],
    'analyze:cost': ['cost', 'analyze cost', 'cost impact', 'tradeoff', 'cost-carbon'],
    'optimize:cost': ['cost-effective', 'minimize cost', 'budget'],
    'check:trees': ['trees', 'check trees', 'trees compliance', 'mr1', 'mr3'],
    'check:edge': ['edge', 'check edge', 'edge certification', 'edge v3'],
    'generate:report': ['report', 'generate', 'pdf', 'excel', 'export'],
    'validate:data': ['validate', 'validation', 'data quality', 'check quality', 'sanity'],
    'check:quality': ['quality', 'data quality', 'check data'],
    # Additional helpers
    'manage:scenario': ['scenario', 'compare', 'fork', 'variant', 'what-if'],
}


class SupervisorRouter:
    """Routes queries to appropriate agents based on capability matching.

    The router uses keyword matching to determine which agent capabilities
    are needed for a given query, then selects the best agent from the registry.

    Attributes:
        agents: Dictionary mapping agent names to Agent instances
        capability_index: Reverse index mapping capabilities to agent names
    """

    def __init__(self):
        """Initialize empty router."""
        self.agents: Dict[str, Agent] = {}
        self.capability_index: Dict[str, List[str]] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register an agent and index its capabilities.

        Args:
            agent: Agent instance to register

        Raises:
            ValueError: If agent with same name already registered
        """
        if agent.name in self.agents:
            raise ValueError(f"Agent '{agent.name}' is already registered in router")

        self.agents[agent.name] = agent

        # Index capabilities for faster routing
        for cap in agent.get_capabilities():
            if cap not in self.capability_index:
                self.capability_index[cap] = []
            self.capability_index[cap].append(agent.name)

    def route(self, query: str, context: Dict = None) -> str:
        """Route query to best agent based on capability matching.

        Uses keyword matching to score each agent's suitability, then returns
        the agent name with highest score. Falls back to user_interaction agent
        if no clear match.

        Args:
            query: User query or task description
            context: Optional context dictionary (reserved for future use)

        Returns:
            Agent name (e.g., "material_analyst")

        Example:
            >>> router.route("Calculate carbon footprint for this BOQ")
            'carbon_calculator'

            >>> router.route("Find low-carbon alternatives for concrete")
            'material_analyst'
        """
        query_lower = query.lower()
        scores: Dict[str, int] = {}

        # Score each agent based on capability keyword matches
        for cap, keywords in CAPABILITY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                # This capability is relevant to the query
                if cap in self.capability_index:
                    # All agents with this capability get a point
                    for agent_name in self.capability_index[cap]:
                        scores[agent_name] = scores.get(agent_name, 0) + 1

        # No matches found - use fallback
        if not scores:
            return self._get_fallback_agent()

        # Return agent with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def _get_fallback_agent(self) -> str:
        """Get fallback agent when no capability match found.

        Returns:
            Agent name for fallback (defaults to 'user_interaction')
        """
        # Check if user_interaction agent is registered
        if 'user_interaction' in self.agents:
            return 'user_interaction'

        # If not, return any registered agent (development fallback)
        if self.agents:
            return next(iter(self.agents.keys()))

        # No agents registered at all (should not happen in production)
        raise ValueError("No agents registered in router - cannot route query")

    def get_agent(self, name: str) -> Agent:
        """Get agent instance by name.

        Args:
            name: Agent name

        Returns:
            Agent instance

        Raises:
            KeyError: If agent not found
        """
        return self.agents[name]

    def list_agents(self) -> List[str]:
        """List all registered agent names.

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def list_capabilities(self) -> Dict[str, List[str]]:
        """List all capabilities and their associated agents.

        Returns:
            Dictionary mapping capability tags to lists of agent names
        """
        return dict(self.capability_index)

    def explain_routing(self, query: str) -> Dict[str, any]:
        """Explain why a query would be routed to a specific agent.

        Useful for debugging and transparency.

        Args:
            query: User query

        Returns:
            Dictionary with routing explanation:
                - selected_agent: The chosen agent name
                - scores: Dictionary of all agent scores
                - matched_capabilities: List of capabilities that matched
                - matched_keywords: List of keywords that matched

        Example:
            >>> router.explain_routing("Calculate carbon for BOQ")
            {
                'selected_agent': 'carbon_calculator',
                'scores': {'carbon_calculator': 2, 'boq_parser': 1},
                'matched_capabilities': ['calculate:carbon', 'parse:boq'],
                'matched_keywords': ['calculate', 'carbon', 'boq']
            }
        """
        query_lower = query.lower()
        scores: Dict[str, int] = {}
        matched_capabilities: List[str] = []
        matched_keywords: List[str] = []

        # Score each agent and track matches
        for cap, keywords in CAPABILITY_KEYWORDS.items():
            matched_kws = [kw for kw in keywords if kw in query_lower]
            if matched_kws:
                matched_capabilities.append(cap)
                matched_keywords.extend(matched_kws)

                if cap in self.capability_index:
                    for agent_name in self.capability_index[cap]:
                        scores[agent_name] = scores.get(agent_name, 0) + 1

        # Determine selected agent
        if scores:
            selected_agent = max(scores.items(), key=lambda x: x[1])[0]
        else:
            selected_agent = self._get_fallback_agent()

        return {
            'selected_agent': selected_agent,
            'scores': scores,
            'matched_capabilities': matched_capabilities,
            'matched_keywords': list(set(matched_keywords)),  # Deduplicate
        }

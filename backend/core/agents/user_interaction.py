"""User Interaction Agent for handling chat and user queries.

This agent provides conversational interface, help information, and
explanations for the multi-agent system.
"""

from typing import Dict, Any, List
from .base import Agent
from .state import AgentState
import logging

logger = logging.getLogger(__name__)


class UserInteractionAgent(Agent):
    """Agent for user interaction, help, and explanations.

    Capabilities:
        - interact:user: Handle user chat and general questions

    This agent serves as the conversational interface when queries
    don't match specific specialist capabilities.
    """

    def __init__(self):
        """Initialize User Interaction Agent."""
        super().__init__(
            name="user_interaction",
            capabilities={"interact:user"}
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Handle user chat and questions.

        Args:
            state: Current AgentState with user query and task results

        Returns:
            Dictionary with:
                - message: User-friendly response message
                - suggested_actions: List of suggested next steps
                - help_topics: Available help topics (if help requested)

        Example:
            {
                "message": "I can help you with carbon analysis...",
                "suggested_actions": [
                    "Calculate carbon footprint for BOQ",
                    "Find alternative materials"
                ]
            }
        """
        query = state["user_query"]
        task_results = state.get("task_results", {})

        self.logger.info(f"User interaction for query: {query}")

        query_lower = query.lower()

        # Check query type and respond accordingly
        if self._is_help_request(query_lower):
            result = await self._provide_help()

        elif self._is_explanation_request(query_lower):
            result = await self._explain_results(task_results)

        elif self._is_greeting(query_lower):
            result = self._greet_user()

        elif self._is_status_request(query_lower):
            result = self._provide_status(state)

        else:
            # Generic response with suggestions
            result = self._provide_generic_response(query)

        self.logger.info(f"User interaction complete: {result.get('message', '')[:50]}...")

        return result

    async def _provide_help(self) -> Dict[str, Any]:
        """Provide help information about available features.

        Returns:
            Help information dictionary
        """
        return {
            "message": "I can help you with carbon-conscious BIM analysis for construction projects.",
            "help_topics": [
                "Carbon Calculation - Calculate embodied carbon from BOQ",
                "Material Alternatives - Find lower-carbon material options",
                "Compliance Checks - Verify TREES and EDGE certification criteria",
                "Material Database - Query TGO material emission factors",
                "Scenario Comparison - Compare different material scenarios"
            ],
            "suggested_actions": [
                "Upload a BOQ file to start carbon analysis",
                "Ask about alternative materials for a specific material type",
                "Request TREES or EDGE compliance assessment"
            ],
            "example_queries": [
                "Calculate carbon footprint for my BOQ",
                "Find alternatives for concrete with lower carbon",
                "Check if this material qualifies for TREES MR1",
                "What is the emission factor for steel?"
            ]
        }

    async def _explain_results(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Explain previous calculation results.

        Args:
            task_results: Previous agent execution results

        Returns:
            Explanation dictionary
        """
        explanations = []

        # Check for carbon calculation results
        if "total_carbon" in task_results:
            total = task_results["total_carbon"]
            explanations.append(
                f"The total embodied carbon is {total:,.1f} kgCO2e. "
                f"This represents the greenhouse gas emissions from producing and transporting the materials."
            )

            if "by_category" in task_results:
                categories = task_results["by_category"]
                top_category = max(categories.items(), key=lambda x: x[1])
                explanations.append(
                    f"The largest contributor is {top_category[0]} "
                    f"({top_category[1]:,.1f} kgCO2e, "
                    f"{(top_category[1]/total*100):.1f}% of total)."
                )

        # Check for material alternatives
        if "alternatives" in task_results:
            alternatives = task_results["alternatives"]
            if alternatives:
                count = len(alternatives)
                explanations.append(
                    f"Found {count} alternative material{'s' if count != 1 else ''} "
                    f"with carbon reduction potential."
                )

        # Check for compliance results
        if "trees_compliant" in task_results or "edge_compliant" in task_results:
            if task_results.get("trees_compliant"):
                explanations.append("This design meets TREES certification criteria.")
            if task_results.get("edge_compliant"):
                edge_level = task_results.get("edge_level", "unknown")
                explanations.append(f"This design qualifies for EDGE {edge_level} certification.")

        if not explanations:
            return {
                "message": "No previous results to explain. Please run an analysis first.",
                "suggested_actions": [
                    "Calculate carbon footprint",
                    "Find material alternatives",
                    "Check compliance"
                ]
            }

        return {
            "message": " ".join(explanations),
            "details": task_results,
            "suggested_actions": [
                "Find material alternatives to reduce carbon",
                "Check TREES/EDGE compliance",
                "Export results for reporting"
            ]
        }

    def _greet_user(self) -> Dict[str, Any]:
        """Greet the user.

        Returns:
            Greeting dictionary
        """
        return {
            "message": "Hello! I'm your carbon-conscious BIM assistant. I can help you analyze embodied carbon in construction projects and find sustainable material alternatives.",
            "suggested_actions": [
                "Upload a BOQ file to analyze carbon footprint",
                "Ask about material alternatives",
                "Learn about TREES/EDGE certification"
            ]
        }

    def _provide_status(self, state: AgentState) -> Dict[str, Any]:
        """Provide current analysis status.

        Args:
            state: Current AgentState

        Returns:
            Status dictionary
        """
        agent_history = state.get("agent_history", [])
        task_results = state.get("task_results", {})
        error_count = state.get("error_count", 0)

        # Count completed analyses
        completed = []
        if "total_carbon" in task_results:
            completed.append("Carbon calculation")
        if "alternatives" in task_results:
            completed.append("Material alternatives")
        if "trees_compliant" in task_results or "edge_compliant" in task_results:
            completed.append("Compliance check")

        status_message = f"Agents invoked: {len(agent_history)}"

        if completed:
            status_message += f". Completed: {', '.join(completed)}"

        if error_count > 0:
            status_message += f". {error_count} error(s) encountered"

        return {
            "message": status_message,
            "agent_history": list(agent_history),
            "completed_analyses": completed,
            "error_count": error_count,
            "suggested_actions": [
                "View detailed results",
                "Run additional analysis",
                "Export report"
            ]
        }

    def _provide_generic_response(self, query: str) -> Dict[str, Any]:
        """Provide generic response for unmatched queries.

        Args:
            query: User query string

        Returns:
            Generic response dictionary
        """
        # Analyze query for keywords to suggest actions
        suggestions = self._suggest_actions(query)

        return {
            "message": f"I understand you want to: {query}",
            "suggested_actions": suggestions,
            "help_hint": "Type 'help' to see what I can do, or upload a BOQ file to start analysis."
        }

    def _is_help_request(self, query: str) -> bool:
        """Check if query is a help request."""
        help_keywords = ["help", "what can you do", "capabilities", "features"]
        return any(keyword in query for keyword in help_keywords)

    def _is_explanation_request(self, query: str) -> bool:
        """Check if query requests explanation."""
        explain_keywords = ["explain", "why", "how", "what does", "what is"]
        return any(keyword in query for keyword in explain_keywords)

    def _is_greeting(self, query: str) -> bool:
        """Check if query is a greeting."""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        return any(greeting in query for greeting in greetings)

    def _is_status_request(self, query: str) -> bool:
        """Check if query requests status."""
        status_keywords = ["status", "what have", "progress", "summary"]
        return any(keyword in query for keyword in status_keywords)

    def _suggest_actions(self, query: str) -> List[str]:
        """Suggest possible actions based on query keywords.

        Args:
            query: User query string

        Returns:
            List of suggested actions
        """
        suggestions = []
        query_lower = query.lower()

        if "carbon" in query_lower or "emission" in query_lower:
            suggestions.append("Calculate carbon footprint for BOQ")

        if "material" in query_lower or "alternative" in query_lower:
            suggestions.append("Find alternative materials with lower carbon")

        if "trees" in query_lower or "edge" in query_lower or "compliance" in query_lower:
            suggestions.append("Check TREES or EDGE compliance")

        if "tgo" in query_lower or "database" in query_lower:
            suggestions.append("Query TGO material database")

        if "compare" in query_lower or "scenario" in query_lower:
            suggestions.append("Create scenario comparison")

        if not suggestions:
            # Default suggestions
            suggestions = [
                "Upload BOQ file for carbon analysis",
                "Ask about specific materials",
                "Request TREES/EDGE compliance check"
            ]

        return suggestions

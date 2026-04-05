"""Cost Analyst Agent for cost-carbon tradeoff analysis.

This agent analyzes the cost implications of carbon reduction strategies
and material alternatives.
"""

import logging
from typing import Dict, Any, List
from decimal import Decimal
from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class CostAnalystAgent(Agent):
    """Agent for cost analysis and cost-carbon tradeoff optimization.

    This agent:
    1. Analyzes cost impact of material alternatives
    2. Performs cost-carbon tradeoff analysis
    3. Identifies cost-effective carbon reduction opportunities

    Capabilities:
        - analyze:cost
        - optimize:cost
    """

    def __init__(self, cost_database=None):
        """Initialize Cost Analyst Agent.

        Args:
            cost_database: Optional cost database client for Phase 5.
                          If None, uses placeholder estimates.
        """
        super().__init__(
            name="cost_analyst",
            capabilities={"analyze:cost", "optimize:cost"}
        )
        self.cost_db = cost_database

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute cost analysis.

        Args:
            state: Current agent state

        Returns:
            Dictionary with:
                - cost_analysis: Cost breakdown and analysis
                - cost_carbon_tradeoff: List of tradeoff analysis results
                - cost_effective_alternatives: Alternatives with best cost/carbon ratio

        Example:
            >>> state = {
            ...     "user_query": "Analyze cost impact",
            ...     "task_results": {
            ...         "material_alternatives": [...]
            ...     }
            ... }
            >>> result = await agent.execute(state)
            >>> "cost_analysis" in result
            True
        """
        logger.info(f"Cost Analyst Agent executing: {state['user_query']}")

        task_results = state.get("task_results", {})
        alternatives = task_results.get("material_alternatives", [])
        base_materials = task_results.get("material_breakdown", [])

        if not alternatives and not base_materials:
            logger.warning("No alternatives or materials provided for cost analysis")
            return {
                "cost_analysis": {},
                "cost_carbon_tradeoff": [],
                "cost_effective_alternatives": []
            }

        # Analyze cost impact
        cost_analysis = self._analyze_costs(base_materials)

        # Analyze cost-carbon tradeoffs for alternatives
        tradeoff_analysis = self._analyze_tradeoffs(alternatives)

        # Identify cost-effective alternatives
        cost_effective = self._find_cost_effective_alternatives(tradeoff_analysis)

        logger.info(
            f"Cost analysis complete: "
            f"{len(tradeoff_analysis)} alternatives analyzed, "
            f"{len(cost_effective)} cost-effective options found"
        )

        return {
            "cost_analysis": cost_analysis,
            "cost_carbon_tradeoff": tradeoff_analysis,
            "cost_effective_alternatives": cost_effective
        }

    def _analyze_costs(self, materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze base costs for materials.

        Args:
            materials: List of material dictionaries

        Returns:
            Cost analysis summary
        """
        if not materials:
            return {}

        # Placeholder: Use 8.5% cost increase estimate from AlternativeRecommendationEngine
        # TODO: Integrate with actual cost database in Phase 5

        total_estimated_cost = Decimal("0")

        for material in materials:
            quantity = Decimal(str(material.get("quantity", 0)))
            # Rough estimate: 1000 THB per m³ for concrete, 50 THB per kg for steel
            unit_cost = self._estimate_unit_cost(material)
            material_cost = quantity * unit_cost
            total_estimated_cost += material_cost

        return {
            "total_estimated_cost_thb": float(total_estimated_cost),
            "currency": "THB",
            "estimation_method": "placeholder",
            "note": "Cost estimates are placeholders. Full cost database integration in Phase 5."
        }

    def _estimate_unit_cost(self, material: Dict[str, Any]) -> Decimal:
        """Estimate unit cost for a material (placeholder).

        Args:
            material: Material dictionary

        Returns:
            Estimated unit cost in THB
        """
        material_type = material.get("material_type", "").lower()
        material_name = material.get("name", "").lower()

        # Rough estimates (THB)
        if "concrete" in material_type or "concrete" in material_name:
            return Decimal("1000")  # THB per m³
        elif "steel" in material_type or "steel" in material_name:
            return Decimal("50")  # THB per kg
        elif "glass" in material_type or "glass" in material_name:
            return Decimal("800")  # THB per m²
        elif "wood" in material_type or "wood" in material_name:
            return Decimal("600")  # THB per m³
        else:
            return Decimal("500")  # Default estimate

    def _analyze_tradeoffs(
        self,
        alternatives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze cost-carbon tradeoffs for alternatives.

        Args:
            alternatives: List of material alternatives

        Returns:
            List of tradeoff analysis results
        """
        tradeoff_analysis = []

        for alt in alternatives:
            carbon_reduction = Decimal(str(alt.get("carbon_reduction_kgco2e", 0)))
            cost_impact_pct = Decimal(str(alt.get("cost_impact_percentage", 8.5)))

            # Calculate cost per kgCO2e reduced
            if carbon_reduction > 0:
                # Rough calculation (needs actual cost data)
                cost_per_kgco2e = abs(cost_impact_pct) / carbon_reduction
            else:
                cost_per_kgco2e = Decimal("0")

            tradeoff_analysis.append({
                "material_id": alt.get("material_id"),
                "material_name": alt.get("name"),
                "carbon_reduction_kgco2e": float(carbon_reduction),
                "cost_impact_percentage": float(cost_impact_pct),
                "cost_per_kgco2e_reduced": float(cost_per_kgco2e),
                "cost_effectiveness_score": self._calculate_cost_effectiveness(
                    carbon_reduction,
                    cost_impact_pct
                ),
                "recommendation": self._generate_cost_recommendation(
                    cost_impact_pct,
                    carbon_reduction
                )
            })

        # Sort by cost effectiveness (best first)
        tradeoff_analysis.sort(
            key=lambda x: x["cost_effectiveness_score"],
            reverse=True
        )

        return tradeoff_analysis

    def _calculate_cost_effectiveness(
        self,
        carbon_reduction: Decimal,
        cost_impact_pct: Decimal
    ) -> float:
        """Calculate cost effectiveness score.

        Higher score = better cost effectiveness
        Formula: carbon_reduction / (1 + abs(cost_impact_pct) / 100)

        Args:
            carbon_reduction: Carbon reduction in kgCO2e
            cost_impact_pct: Cost impact percentage

        Returns:
            Cost effectiveness score
        """
        if carbon_reduction <= 0:
            return 0.0

        # Penalize higher cost impacts
        cost_penalty = 1 + abs(cost_impact_pct) / Decimal("100")

        score = float(carbon_reduction / cost_penalty)
        return score

    def _generate_cost_recommendation(
        self,
        cost_impact_pct: Decimal,
        carbon_reduction: Decimal
    ) -> str:
        """Generate cost-based recommendation.

        Args:
            cost_impact_pct: Cost impact percentage
            carbon_reduction: Carbon reduction in kgCO2e

        Returns:
            Recommendation string
        """
        if cost_impact_pct < 0:
            return "Cost savings with carbon reduction - highly recommended"
        elif cost_impact_pct < 5:
            return "Minimal cost increase (<5%) for carbon reduction - recommended"
        elif cost_impact_pct < 15:
            return "Moderate cost increase (5-15%) - evaluate project budget"
        else:
            return "Significant cost increase (>15%) - consider if carbon reduction is priority"

    def _find_cost_effective_alternatives(
        self,
        tradeoff_analysis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find most cost-effective alternatives.

        Args:
            tradeoff_analysis: List of tradeoff analyses

        Returns:
            Top 3 cost-effective alternatives
        """
        # Filter for alternatives with positive carbon reduction and reasonable cost
        cost_effective = [
            alt for alt in tradeoff_analysis
            if alt["carbon_reduction_kgco2e"] > 0
            and alt["cost_impact_percentage"] < 20  # Less than 20% cost increase
        ]

        # Return top 3
        return cost_effective[:3]


def cost_analyst_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node function for Cost Analyst agent.

    Args:
        state: Current AgentState

    Returns:
        Dictionary with cost analysis results
    """
    agent = CostAnalystAgent()
    import asyncio
    return asyncio.run(agent.execute(state))

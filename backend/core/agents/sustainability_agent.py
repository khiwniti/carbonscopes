"""Sustainability Agent for carbon optimization strategies.

This agent performs Pareto analysis to identify high-impact materials
and generates optimization strategies for carbon reduction.
"""

import logging
from typing import Dict, Any, List
from decimal import Decimal
from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class SustainabilityAgent(Agent):
    """Agent for carbon optimization and sustainability strategies.

    This agent:
    1. Performs Pareto analysis (80/20 rule) to identify high-impact materials
    2. Generates optimization strategies for top carbon contributors
    3. Estimates carbon reduction potential

    Capabilities:
        - optimize:carbon
        - recommend:strategies
    """

    def __init__(self, alternatives_engine=None):
        """Initialize Sustainability Agent.

        Args:
            alternatives_engine: Optional AlternativeRecommendationEngine
                               from Phase 3 Plan 02
        """
        super().__init__(
            name="sustainability",
            capabilities={"optimize:carbon", "recommend:strategies"}
        )
        self.alternatives_engine = alternatives_engine

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute sustainability analysis and strategy generation.

        Args:
            state: Current agent state containing material breakdown

        Returns:
            Dictionary with:
                - high_impact_materials: List of materials contributing 80% of carbon
                - optimization_strategies: List of recommended strategies
                - estimated_reduction: Estimated carbon reduction potential

        Example:
            >>> state = {
            ...     "user_query": "Generate carbon optimization strategies",
            ...     "task_results": {
            ...         "material_breakdown": [...],
            ...         "total_carbon": 10000.0
            ...     }
            ... }
            >>> result = await agent.execute(state)
            >>> len(result["high_impact_materials"]) <= 5
            True
        """
        logger.info(f"Sustainability Agent executing: {state['user_query']}")

        task_results = state.get("task_results", {})
        material_breakdown = task_results.get("material_breakdown", [])
        total_carbon = task_results.get("total_carbon", Decimal("0"))

        if not material_breakdown:
            logger.warning("No material breakdown provided")
            return {
                "high_impact_materials": [],
                "optimization_strategies": [],
                "estimated_reduction": Decimal("0")
            }

        # Perform Pareto analysis
        high_impact = self.identify_high_impact_materials(
            material_breakdown,
            total_carbon
        )

        # Generate optimization strategies
        strategies = await self._generate_strategies(high_impact, state)

        # Estimate reduction potential
        estimated_reduction = self._estimate_reduction(strategies)

        logger.info(
            f"Identified {len(high_impact)} high-impact materials, "
            f"generated {len(strategies)} strategies, "
            f"estimated reduction: {estimated_reduction} kgCO2e"
        )

        return {
            "high_impact_materials": high_impact,
            "optimization_strategies": strategies,
            "estimated_reduction": estimated_reduction
        }

    def identify_high_impact_materials(
        self,
        materials: List[Dict[str, Any]],
        total_carbon: Decimal
    ) -> List[Dict[str, Any]]:
        """Identify materials contributing to 80% of carbon (Pareto analysis).

        This implements the 80/20 rule: typically 20% of materials contribute
        to 80% of total embodied carbon.

        Args:
            materials: List of material dicts with carbon values
            total_carbon: Total carbon footprint

        Returns:
            List of high-impact materials sorted by carbon contribution
        """
        if not materials or total_carbon == 0:
            return []

        # Sort by carbon contribution (descending)
        sorted_materials = sorted(
            materials,
            key=lambda m: Decimal(str(m.get("total_carbon", 0))),
            reverse=True
        )

        # Find materials contributing to 80% of carbon
        target_carbon = total_carbon * Decimal("0.80")
        cumulative_carbon = Decimal("0")
        high_impact = []

        for material in sorted_materials:
            material_carbon = Decimal(str(material.get("total_carbon", 0)))
            cumulative_carbon += material_carbon

            # Add carbon percentage
            carbon_percentage = float(
                (material_carbon / total_carbon * 100) if total_carbon > 0 else 0
            )

            high_impact.append({
                **material,
                "carbon_percentage": carbon_percentage,
                "cumulative_percentage": float(
                    (cumulative_carbon / total_carbon * 100) if total_carbon > 0 else 0
                )
            })

            # Stop when we reach 80% threshold
            if cumulative_carbon >= target_carbon:
                break

        logger.info(
            f"Pareto analysis: {len(high_impact)} materials "
            f"contribute {cumulative_carbon} kgCO2e "
            f"({float(cumulative_carbon / total_carbon * 100):.1f}%)"
        )

        return high_impact

    async def _generate_strategies(
        self,
        high_impact_materials: List[Dict[str, Any]],
        state: AgentState
    ) -> List[Dict[str, Any]]:
        """Generate optimization strategies for high-impact materials.

        Strategies include:
        1. Material swaps (use alternatives engine if available)
        2. Design changes (structural optimization)
        3. Quantity reductions

        Args:
            high_impact_materials: List of high-impact materials
            state: Current agent state

        Returns:
            List of strategy dictionaries
        """
        strategies = []

        for material in high_impact_materials:
            material_id = material.get("material_id")
            material_name = material.get("name", material.get("description", "Unknown"))
            carbon = Decimal(str(material.get("total_carbon", 0)))
            quantity = Decimal(str(material.get("quantity", 0)))

            # Strategy 1: Material swap (if alternatives engine available)
            if self.alternatives_engine:
                # TODO: Use alternatives engine to find lower-carbon alternatives
                # alternatives = await self.alternatives_engine.recommend_alternatives(...)
                pass

            # Mock strategy: Material swap
            strategies.append({
                "type": "material_swap",
                "material_id": material_id,
                "material_name": material_name,
                "current_carbon": float(carbon),
                "recommendation": f"Consider using recycled or lower-carbon alternative for {material_name}",
                "estimated_reduction_kgco2e": float(carbon * Decimal("0.15")),  # 15% reduction estimate
                "estimated_reduction_percentage": 15.0,
                "implementation_difficulty": "medium"
            })

            # Strategy 2: Design optimization (for structural materials)
            if "concrete" in material_name.lower() or "steel" in material_name.lower():
                strategies.append({
                    "type": "design_optimization",
                    "material_id": material_id,
                    "material_name": material_name,
                    "current_carbon": float(carbon),
                    "recommendation": f"Review structural design to optimize {material_name} usage",
                    "estimated_reduction_kgco2e": float(carbon * Decimal("0.10")),  # 10% reduction estimate
                    "estimated_reduction_percentage": 10.0,
                    "implementation_difficulty": "high"
                })

            # Strategy 3: Quantity reduction (for non-critical materials)
            if quantity > 0:
                strategies.append({
                    "type": "quantity_reduction",
                    "material_id": material_id,
                    "material_name": material_name,
                    "current_carbon": float(carbon),
                    "current_quantity": float(quantity),
                    "recommendation": f"Evaluate opportunities to reduce {material_name} quantity",
                    "estimated_reduction_kgco2e": float(carbon * Decimal("0.05")),  # 5% reduction estimate
                    "estimated_reduction_percentage": 5.0,
                    "implementation_difficulty": "low"
                })

        return strategies

    def _estimate_reduction(self, strategies: List[Dict[str, Any]]) -> Decimal:
        """Estimate total carbon reduction from all strategies.

        Args:
            strategies: List of strategy dictionaries

        Returns:
            Total estimated carbon reduction in kgCO2e
        """
        total_reduction = Decimal("0")

        for strategy in strategies:
            reduction = Decimal(str(strategy.get("estimated_reduction_kgco2e", 0)))
            total_reduction += reduction

        return total_reduction


def sustainability_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node function for Sustainability agent.

    Args:
        state: Current AgentState

    Returns:
        Dictionary with sustainability analysis results
    """
    agent = SustainabilityAgent()
    import asyncio
    return asyncio.run(agent.execute(state))

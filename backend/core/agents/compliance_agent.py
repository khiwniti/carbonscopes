"""Compliance Agent for TREES/EDGE certification checking.

This agent validates compliance with TREES NC 1.1 and EDGE V3 certification
requirements using SPARQL queries on the knowledge graph.
"""

import logging
from typing import Dict, Any
from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class ComplianceAgent(Agent):
    """Agent for certification compliance validation.

    This agent:
    1. Checks TREES NC 1.1 compliance (MR1, MR3 criteria)
    2. Validates EDGE V3 certification requirements
    3. Provides compliance status and gap analysis

    Capabilities:
        - validate:compliance
        - check:trees
        - check:edge
    """

    def __init__(self, knowledge_graph=None):
        """Initialize Compliance Agent.

        Args:
            knowledge_graph: Optional GraphDBClient for SPARQL queries.
                           If None, operates in mock mode.
        """
        super().__init__(
            name="compliance",
            capabilities={"validate:compliance", "check:trees", "check:edge"}
        )
        self.kg = knowledge_graph

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute compliance checking.

        Args:
            state: Current agent state

        Returns:
            Dictionary with:
                - trees_mr1_compliance: TREES MR1 compliance status
                - trees_mr3_compliance: TREES MR3 compliance status
                - edge_certification_level: EDGE certification level
                - compliance_summary: Overall compliance summary
                - gap_analysis: List of gaps and recommendations

        Example:
            >>> state = {
            ...     "user_query": "Check TREES compliance",
            ...     "task_results": {
            ...         "material_breakdown": [...]
            ...     }
            ... }
            >>> result = await agent.execute(state)
            >>> "trees_mr1_compliance" in result
            True
        """
        logger.info(f"Compliance Agent executing: {state['user_query']}")

        query = state.get("user_query", "").lower()
        task_results = state.get("task_results", {})

        # Check which compliance standard to validate
        check_trees = "trees" in query
        check_edge = "edge" in query

        # If no specific standard mentioned, check both
        if not check_trees and not check_edge:
            check_trees = True
            check_edge = True

        result = {}

        # TREES compliance checking
        if check_trees:
            trees_result = await self._check_trees_compliance(task_results)
            result.update(trees_result)

        # EDGE compliance checking
        if check_edge:
            edge_result = await self._check_edge_compliance(task_results)
            result.update(edge_result)

        # Generate compliance summary
        result["compliance_summary"] = self._generate_summary(result)

        # Generate gap analysis
        result["gap_analysis"] = self._generate_gap_analysis(result)

        logger.info(f"Compliance check complete: {result['compliance_summary']}")

        return result

    async def _check_trees_compliance(
        self,
        task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check TREES NC 1.1 compliance.

        TREES MR1: Sustainable Procurement of Construction Materials
        TREES MR3: Recycled Content Materials

        Args:
            task_results: Task results with material data

        Returns:
            TREES compliance results
        """
        materials = task_results.get("material_breakdown", [])

        if self.kg:
            # Use SPARQL queries for real compliance checking
            # TODO: Integrate with knowledge graph SPARQL queries
            pass

        # Mock compliance checking
        # In reality, this would query the knowledge graph for:
        # 1. MR1: Materials with environmental product declarations (EPDs)
        # 2. MR3: Recycled content percentage

        recycled_materials = [
            m for m in materials
            if "recycled" in m.get("name", "").lower()
        ]

        total_materials = len(materials)
        recycled_count = len(recycled_materials)
        recycled_percentage = (
            (recycled_count / total_materials * 100) if total_materials > 0 else 0.0
        )

        # TREES MR1: At least 50% of materials should have EPDs (mock)
        mr1_compliant = len(materials) > 0  # Placeholder
        mr1_score = 3 if mr1_compliant else 0  # 3 points for MR1 compliance

        # TREES MR3: Recycled content ≥15% by value (mock)
        mr3_compliant = recycled_percentage >= 15.0
        mr3_score = 3 if mr3_compliant else 0  # 3 points for MR3 compliance

        return {
            "trees_mr1_compliance": mr1_compliant,
            "trees_mr1_score": mr1_score,
            "trees_mr1_details": {
                "requirement": "At least 50% of materials with EPDs",
                "status": "compliant" if mr1_compliant else "non-compliant",
                "notes": "Mock compliance check - requires EPD database integration"
            },
            "trees_mr3_compliance": mr3_compliant,
            "trees_mr3_score": mr3_score,
            "trees_mr3_details": {
                "requirement": "Recycled content ≥15% by value",
                "recycled_percentage": recycled_percentage,
                "recycled_count": recycled_count,
                "total_count": total_materials,
                "status": "compliant" if mr3_compliant else "non-compliant"
            },
            "trees_total_score": mr1_score + mr3_score,
            "trees_certification_level": self._determine_trees_level(
                mr1_score + mr3_score
            )
        }

    async def _check_edge_compliance(
        self,
        task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check EDGE V3 certification compliance.

        EDGE requires 20% embodied carbon reduction vs baseline.

        Args:
            task_results: Task results with carbon data

        Returns:
            EDGE compliance results
        """
        total_carbon = task_results.get("total_carbon", 0)
        baseline_carbon = task_results.get("baseline_carbon")

        # If no baseline provided, estimate it (typically 1.2x current)
        if baseline_carbon is None:
            baseline_carbon = float(total_carbon) * 1.2

        # Calculate reduction percentage
        if baseline_carbon > 0:
            reduction_percentage = (
                (baseline_carbon - float(total_carbon)) / baseline_carbon * 100
            )
        else:
            reduction_percentage = 0.0

        # EDGE requires 20% reduction
        edge_compliant = reduction_percentage >= 20.0

        return {
            "edge_certification_level": "EDGE Certified" if edge_compliant else "Not Certified",
            "edge_compliance": edge_compliant,
            "edge_details": {
                "requirement": "20% embodied carbon reduction vs baseline",
                "current_carbon_kgco2e": float(total_carbon),
                "baseline_carbon_kgco2e": baseline_carbon,
                "reduction_kgco2e": baseline_carbon - float(total_carbon),
                "reduction_percentage": reduction_percentage,
                "target_percentage": 20.0,
                "gap_to_target": max(0, 20.0 - reduction_percentage),
                "status": "compliant" if edge_compliant else "non-compliant"
            }
        }

    def _determine_trees_level(self, total_score: int) -> str:
        """Determine TREES certification level based on score.

        Args:
            total_score: Total TREES points

        Returns:
            Certification level string
        """
        # TREES NC 1.1 scoring:
        # Certified: 50-69 points
        # Silver: 70-84 points
        # Gold: 85-94 points
        # Platinum: 95+ points

        if total_score >= 95:
            return "Platinum"
        elif total_score >= 85:
            return "Gold"
        elif total_score >= 70:
            return "Silver"
        elif total_score >= 50:
            return "Certified"
        else:
            return "Not Certified"

    def _generate_summary(self, compliance_results: Dict[str, Any]) -> str:
        """Generate compliance summary.

        Args:
            compliance_results: Compliance check results

        Returns:
            Summary string
        """
        summaries = []

        if "trees_certification_level" in compliance_results:
            level = compliance_results["trees_certification_level"]
            score = compliance_results.get("trees_total_score", 0)
            summaries.append(f"TREES: {level} ({score} points)")

        if "edge_certification_level" in compliance_results:
            level = compliance_results["edge_certification_level"]
            summaries.append(f"EDGE: {level}")

        return " | ".join(summaries) if summaries else "No compliance checks performed"

    def _generate_gap_analysis(
        self,
        compliance_results: Dict[str, Any]
    ) -> list[Dict[str, Any]]:
        """Generate gap analysis with recommendations.

        Args:
            compliance_results: Compliance check results

        Returns:
            List of gaps and recommendations
        """
        gaps = []

        # TREES MR1 gap
        if not compliance_results.get("trees_mr1_compliance", True):
            gaps.append({
                "standard": "TREES NC 1.1 MR1",
                "gap": "Insufficient materials with EPDs",
                "recommendation": "Obtain EPDs for at least 50% of materials by value",
                "priority": "high"
            })

        # TREES MR3 gap
        if not compliance_results.get("trees_mr3_compliance", True):
            details = compliance_results.get("trees_mr3_details", {})
            current = details.get("recycled_percentage", 0)
            gaps.append({
                "standard": "TREES NC 1.1 MR3",
                "gap": f"Recycled content only {current:.1f}% (requires ≥15%)",
                "recommendation": "Increase recycled content materials to reach 15% by value",
                "priority": "medium"
            })

        # EDGE gap
        if not compliance_results.get("edge_compliance", True):
            details = compliance_results.get("edge_details", {})
            gap_pct = details.get("gap_to_target", 0)
            gaps.append({
                "standard": "EDGE V3",
                "gap": f"Need {gap_pct:.1f}% more carbon reduction to reach 20% target",
                "recommendation": "Implement carbon reduction strategies to close gap",
                "priority": "high"
            })

        return gaps


def compliance_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node function for Compliance agent.

    Args:
        state: Current AgentState

    Returns:
        Dictionary with compliance check results
    """
    agent = ComplianceAgent()
    import asyncio
    return asyncio.run(agent.execute(state))

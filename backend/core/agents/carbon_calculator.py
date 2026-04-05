"""Carbon Calculator Agent for calculating carbon footprints.

This agent wraps Phase 2 CarbonCalculationPipeline to provide carbon
footprint calculations through the LangGraph multi-agent system.
"""

from typing import Dict, Any
from .base import Agent
from .state import AgentState
import logging

logger = logging.getLogger(__name__)


class CarbonCalculatorAgent(Agent):
    """Agent for calculating carbon footprints from BOQ data.

    Capabilities:
        - calculate:carbon: Calculate total embodied carbon from BOQ

    This agent integrates with Phase 2 carbon calculation pipeline
    to provide carbon footprint analysis.
    """

    def __init__(self, carbon_pipeline=None):
        """Initialize Carbon Calculator Agent.

        Args:
            carbon_pipeline: Optional CarbonCalculationPipeline instance.
                           If None, operates in mock mode for testing.
        """
        super().__init__(
            name="carbon_calculator",
            capabilities={"calculate:carbon"}
        )
        self.carbon_pipeline = carbon_pipeline

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute carbon footprint calculation.

        Args:
            state: Current AgentState with BOQ data in task_results

        Returns:
            Dictionary with:
                - total_carbon: Total embodied carbon in kgCO2e
                - by_category: Carbon breakdown by material category
                - by_material: Carbon breakdown by individual materials
                - unit: Unit of measurement (kgCO2e)
                - boq_id: BOQ identifier (if available)

        Example:
            {
                "total_carbon": 125430.5,
                "by_category": {
                    "concrete": 85200.3,
                    "steel": 35100.2,
                    "timber": 5130.0
                },
                "by_material": [
                    {"material": "Concrete C30", "carbon": 45000.0},
                    {"material": "Steel Rebar", "carbon": 35100.2}
                ],
                "unit": "kgCO2e",
                "boq_id": "boq_123"
            }
        """
        task_results = state.get("task_results", {})

        # Extract BOQ ID or materials from previous task results
        boq_id = task_results.get("boq_id")
        boq_materials = task_results.get("boq_materials", [])

        if not boq_id and not boq_materials:
            return {
                "error": "No BOQ ID or materials provided for carbon calculation",
                "total_carbon": 0.0,
                "by_category": {},
                "by_material": [],
                "unit": "kgCO2e"
            }

        self.logger.info(
            f"Calculating carbon for BOQ: {boq_id or 'from materials'}"
        )

        try:
            # If carbon pipeline is available, use Phase 2 logic
            if self.carbon_pipeline is not None and boq_id:
                result = await self._calculate_with_pipeline(boq_id)
            elif boq_materials:
                result = await self._calculate_from_materials(boq_materials)
            else:
                result = self._get_mock_calculation()

            self.logger.info(
                f"Carbon calculation complete: {result['total_carbon']:.1f} kgCO2e"
            )

            return result

        except Exception as e:
            self.logger.error(f"Carbon calculation failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "total_carbon": 0.0,
                "by_category": {},
                "by_material": [],
                "unit": "kgCO2e"
            }

    async def _calculate_with_pipeline(self, boq_id: str) -> Dict[str, Any]:
        """Calculate carbon using Phase 2 pipeline.

        Args:
            boq_id: BOQ identifier

        Returns:
            Carbon calculation results
        """
        try:
            # Use Phase 2 CarbonCalculationPipeline
            result = await self.carbon_pipeline.calculate_carbon(boq_id)

            return {
                "total_carbon": float(result.total_kgco2e),
                "by_category": result.by_category or {},
                "by_material": result.by_material or [],
                "unit": "kgCO2e",
                "boq_id": boq_id,
                "audit_id": result.audit_id if hasattr(result, 'audit_id') else None
            }

        except Exception as e:
            self.logger.error(f"Pipeline calculation failed: {e}", exc_info=True)
            raise

    async def _calculate_from_materials(
        self, materials: list
    ) -> Dict[str, Any]:
        """Calculate carbon from material list.

        Args:
            materials: List of material dictionaries with emission factors

        Returns:
            Carbon calculation results
        """
        total_carbon = 0.0
        by_category = {}
        by_material = []

        for mat in materials:
            # Extract material data
            quantity = float(mat.get("quantity", 0.0))
            emission_factor = float(mat.get("emission_factor", 0.0))
            category = mat.get("category", "unknown")
            label = mat.get("label") or mat.get("description_en") or "Unknown Material"

            # Calculate carbon for this material
            material_carbon = quantity * emission_factor

            # Aggregate by category
            if category not in by_category:
                by_category[category] = 0.0
            by_category[category] += material_carbon

            # Add to material breakdown
            by_material.append({
                "material": label,
                "carbon": round(material_carbon, 2),
                "quantity": quantity,
                "emission_factor": emission_factor
            })

            total_carbon += material_carbon

        return {
            "total_carbon": round(total_carbon, 2),
            "by_category": {k: round(v, 2) for k, v in by_category.items()},
            "by_material": sorted(
                by_material,
                key=lambda x: x["carbon"],
                reverse=True
            )[:10],  # Top 10 contributors
            "unit": "kgCO2e",
            "material_count": len(materials)
        }

    def _get_mock_calculation(self) -> Dict[str, Any]:
        """Generate mock calculation for testing.

        Returns:
            Mock carbon calculation results
        """
        return {
            "total_carbon": 125430.5,
            "by_category": {
                "concrete": 85200.3,
                "steel": 35100.2,
                "timber": 5130.0
            },
            "by_material": [
                {
                    "material": "Concrete C30",
                    "carbon": 45000.0,
                    "quantity": 150.0,
                    "emission_factor": 300.0
                },
                {
                    "material": "Recycled Concrete",
                    "carbon": 40200.3,
                    "quantity": 180.0,
                    "emission_factor": 223.3
                },
                {
                    "material": "Steel Rebar",
                    "carbon": 35100.2,
                    "quantity": 15.5,
                    "emission_factor": 2264.5
                },
                {
                    "material": "Hardwood Timber",
                    "carbon": 5130.0,
                    "quantity": 25.0,
                    "emission_factor": 205.2
                }
            ],
            "unit": "kgCO2e",
            "source": "mock"
        }

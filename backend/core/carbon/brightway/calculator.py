"""Carbon calculator using Brightway2.

Implements deterministic material carbon calculations and project aggregation.
"""

from decimal import Decimal
from typing import List, Dict

# Assuming we've already loaded a Brightway2 Database with TGO material activities.
# We'll use a simple placeholder for db access; real implementation would query the BW DB.


class CarbonCalculator:
    """Calculate embodied carbon using Brightway2 database."""

    def __init__(self, db_name: str = "TGO-Thailand-2026"):
        import brightway2 as bw

        self.db = bw.Database(db_name)
        if not self.db:
            raise RuntimeError(f"Brightway2 database '{db_name}' not found or empty")

    def _get_activity(self, material_id: str):
        # Find activity by code or name (simplified lookup)
        for act in self.db:
            if act.get("code") == material_id or act.get("name") == material_id:
                return act
        raise KeyError(f"Material '{material_id}' not found in Brightway2 database")

    def calculate_material_carbon(
        self, material_id: str, quantity: Decimal, unit: str
    ) -> Dict:
        """Calculate carbon for a single material.

        Returns dict with total carbon, emission factor, formula, and lifecycle stages.
        """
        activity = self._get_activity(material_id)
        # emission_factor stored as a float/decimal in activity exchanges
        ef = Decimal(str(activity["exchanges"][0]["amount"]))
        total_carbon = quantity * ef
        return {
            "total_carbon": total_carbon,
            "emission_factor": ef,
            "formula": f"{quantity} {unit} × {ef} kgCO2e/{unit}",
            "lifecycle_stages": ["A1", "A2", "A3"],
        }

    def calculate_project_carbon(self, materials: List[Dict]) -> Dict:
        """Calculate total carbon for a project.

        materials: list of dicts with keys: material_id, quantity, unit (as string)
        """
        total = Decimal("0")
        breakdown = []
        for m in materials:
            res = self.calculate_material_carbon(
                m["material_id"], Decimal(str(m["quantity"])), m["unit"]
            )
            breakdown.append(res)
            total += res["total_carbon"]
        return {
            "total_carbon": total,
            "material_breakdown": breakdown,
            "calculation_metadata": {
                "database_version": self.db.name,
                "calculation_method": "ISO 14040/14044",
                "deterministic": True,
            },
        }

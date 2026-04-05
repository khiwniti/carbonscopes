"""TGO Database Agent for querying emission factors.

This agent queries the TGO (Thai Green Objects) database for material
emission factors and environmental data.
"""

from typing import Dict, Any, List, Optional
from .base import Agent
from .state import AgentState
import logging
import re

logger = logging.getLogger(__name__)


class TGODatabaseAgent(Agent):
    """Agent for querying TGO database for emission factors.

    Capabilities:
        - query:tgo: Query TGO database for material data

    This agent provides access to the TGO material database for
    emission factors, material properties, and environmental data.
    """

    def __init__(self, tgo_client=None):
        """Initialize TGO Database Agent.

        Args:
            tgo_client: Optional TGOClient instance for database queries.
                       If None, operates in mock mode for testing.
        """
        super().__init__(
            name="tgo_database",
            capabilities={"query:tgo"}
        )
        self.tgo_client = tgo_client

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Query TGO database for emission factors.

        Args:
            state: Current AgentState with user query

        Returns:
            Dictionary with:
                - emission_factors: List of emission factor results
                - material_count: Number of materials found
                - source: Data source identifier
                - query_term: Search term used

        Example:
            {
                "emission_factors": [
                    {
                        "material_id": "tgo:concrete_c30",
                        "label": "Concrete C30",
                        "emission_factor": 300.5,
                        "unit": "kgCO2e/m³",
                        "category": "concrete"
                    }
                ],
                "material_count": 5,
                "source": "TGO Database",
                "query_term": "concrete"
            }
        """
        query = state["user_query"]
        task_results = state.get("task_results", {})

        self.logger.info(f"Querying TGO database for: {query}")

        # Extract material name from query or task results
        material_name = self._extract_material_name(query, task_results)

        if not material_name:
            return {
                "error": "Could not identify material for TGO query",
                "emission_factors": [],
                "material_count": 0,
                "source": "TGO Database"
            }

        try:
            # Query TGO database
            if self.tgo_client is not None:
                emission_factors = await self._query_database(material_name)
            else:
                # Mock mode for testing
                emission_factors = self._get_mock_emission_factors(material_name)

            self.logger.info(
                f"Found {len(emission_factors)} materials in TGO database"
            )

            return {
                "emission_factors": emission_factors,
                "material_count": len(emission_factors),
                "source": "TGO Database",
                "query_term": material_name
            }

        except Exception as e:
            self.logger.error(f"TGO database query failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "emission_factors": [],
                "material_count": 0,
                "source": "TGO Database"
            }

    async def _query_database(self, material_name: str) -> List[Dict[str, Any]]:
        """Query TGO database using client.

        Args:
            material_name: Material name or search term

        Returns:
            List of emission factor results
        """
        try:
            # Use TGOClient to search materials
            results = await self.tgo_client.search_materials(material_name)

            emission_factors = []
            for result in results:
                emission_factors.append({
                    "material_id": result.get("material_id"),
                    "label": result.get("label"),
                    "emission_factor": float(result.get("emission_factor", 0.0)),
                    "unit": result.get("unit", "kgCO2e/unit"),
                    "category": result.get("category", "unknown"),
                    "source": "TGO Database"
                })

            return emission_factors

        except Exception as e:
            self.logger.error(f"Database query failed: {e}", exc_info=True)
            return []

    def _extract_material_name(
        self, query: str, task_results: Dict[str, Any]
    ) -> Optional[str]:
        """Extract material name from query or task results.

        Args:
            query: User query string
            task_results: Previous agent execution results

        Returns:
            Material name if found, None otherwise
        """
        # Check if material_id is in task results
        if "material_id" in task_results:
            material_id = task_results["material_id"]
            # Extract material name from ID (e.g., "tgo:concrete_c30" -> "concrete")
            match = re.search(r'[a-z]+', material_id.lower())
            if match:
                return match.group(0)

        # Check for quoted material names in query
        quoted = re.findall(r'"([^"]+)"', query)
        if quoted:
            return quoted[0]

        # Simple keyword extraction
        query_lower = query.lower()

        # Common construction materials
        materials = [
            "concrete", "steel", "rebar", "cement", "brick",
            "timber", "wood", "glass", "aluminum", "aluminium",
            "gypsum", "asphalt", "gravel", "sand", "aggregate",
            "insulation", "paint", "tile", "ceramic"
        ]

        for material in materials:
            if material in query_lower:
                return material

        return None

    def _get_mock_emission_factors(self, material_name: str) -> List[Dict[str, Any]]:
        """Generate mock emission factors for testing.

        Args:
            material_name: Material search term

        Returns:
            List of mock emission factor results
        """
        # Mock data based on material type
        mock_data = {
            "concrete": [
                {
                    "material_id": "tgo:concrete_c30",
                    "label": "Concrete C30",
                    "emission_factor": 300.5,
                    "unit": "kgCO2e/m³",
                    "category": "concrete"
                },
                {
                    "material_id": "tgo:concrete_recycled",
                    "label": "Recycled Concrete",
                    "emission_factor": 195.2,
                    "unit": "kgCO2e/m³",
                    "category": "concrete"
                },
                {
                    "material_id": "tgo:concrete_green",
                    "label": "Green Concrete (GGBS)",
                    "emission_factor": 185.3,
                    "unit": "kgCO2e/m³",
                    "category": "concrete"
                }
            ],
            "steel": [
                {
                    "material_id": "tgo:steel_structural",
                    "label": "Structural Steel",
                    "emission_factor": 2500.0,
                    "unit": "kgCO2e/tonne",
                    "category": "steel"
                },
                {
                    "material_id": "tgo:steel_recycled",
                    "label": "Recycled Steel",
                    "emission_factor": 700.0,
                    "unit": "kgCO2e/tonne",
                    "category": "steel"
                }
            ],
            "timber": [
                {
                    "material_id": "tgo:timber_hardwood",
                    "label": "Hardwood Timber",
                    "emission_factor": 205.2,
                    "unit": "kgCO2e/m³",
                    "category": "timber"
                },
                {
                    "material_id": "tgo:timber_certified",
                    "label": "FSC Certified Timber",
                    "emission_factor": -35.0,  # Negative = carbon storage
                    "unit": "kgCO2e/m³",
                    "category": "timber"
                }
            ]
        }

        # Find matching mock data
        for key, data in mock_data.items():
            if key in material_name.lower():
                return [{"source": "TGO Database (mock)", **item} for item in data]

        # Default generic response
        return [
            {
                "material_id": f"tgo:{material_name}_generic",
                "label": f"{material_name.title()} (Generic)",
                "emission_factor": 250.0,
                "unit": "kgCO2e/unit",
                "category": "generic",
                "source": "TGO Database (mock)"
            }
        ]

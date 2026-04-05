"""Material Analyst Agent for material matching and optimization.

This agent wraps Phase 2 material matching logic to find alternatives,
recommendations, and carbon optimization opportunities for BOQ materials.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from decimal import Decimal

from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class MaterialAnalystAgent(Agent):
    """Specialist agent for material matching and carbon optimization.

    This agent:
    1. Matches BOQ materials to TGO database entries
    2. Finds alternative materials with lower carbon footprint
    3. Provides confidence-scored recommendations
    4. Ranks alternatives by carbon reduction potential

    Capabilities:
        - match:materials: Match BOQ materials to TGO database
        - query:tgo: Query TGO material database
        - optimize:carbon: Find lower-carbon alternatives

    Example:
        >>> agent = MaterialAnalystAgent()
        >>> state = {
        ...     "user_query": "Find alternatives for concrete",
        ...     "task_results": {"boq_materials": [...]},
        ...     ...
        ... }
        >>> result = await agent.execute(state)
        >>> print(result["alternatives"])
    """

    def __init__(self, graphdb_client=None):
        """Initialize Material Analyst Agent.

        Args:
            graphdb_client: Optional GraphDBClient instance for TGO queries.
                          If None, will operate in mock mode for testing.
        """
        super().__init__(
            name="material_analyst",
            capabilities={"match:materials", "query:tgo", "optimize:carbon"}
        )
        self.graphdb_client = graphdb_client
        self._material_matcher = None

    @property
    def material_matcher(self):
        """Lazy-load material matcher to avoid import issues."""
        if self._material_matcher is None and self.graphdb_client is not None:
            try:
                from suna.backend.boq.material_matching import match_boq_materials
                self._material_matcher = match_boq_materials
            except ImportError as e:
                logger.warning(f"Could not import material_matching: {e}")
                self._material_matcher = None
        return self._material_matcher

    def _sanitize_sparql_input(self, user_input: str) -> str:
        """Sanitize user input to prevent SPARQL injection attacks.

        SECURITY: This method removes characters that could break SPARQL syntax
        or inject malicious queries. Only alphanumeric, spaces, hyphens, underscores,
        and colons are allowed.

        Args:
            user_input: Raw user input string

        Returns:
            Sanitized string safe for SPARQL queries
        """
        if not user_input:
            return ""

        # Limit length to prevent DoS
        sanitized = user_input[:100]

        # Remove quotes that could break string literals
        sanitized = re.sub(r'["\']', '', sanitized)

        # Remove backslashes that could escape quotes
        sanitized = re.sub(r'\\', '', sanitized)

        # Replace newlines/tabs with spaces
        sanitized = re.sub(r'[\r\n\t]', ' ', sanitized)

        # Remove SPARQL syntax characters that could alter query logic
        sanitized = re.sub(r'[{}#;]', '', sanitized)

        # Only allow alphanumeric, spaces, hyphens, underscores, colons
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in ' -_:')

        return sanitized.strip()

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute material analysis based on user query and state.

        This method:
        1. Extracts material identifiers from user query or task_results
        2. Finds material alternatives using Phase 2 matching logic
        3. Ranks alternatives by confidence and carbon reduction
        4. Returns structured recommendations

        Args:
            state: Current AgentState with user_query and task_results

        Returns:
            Dictionary containing:
                - alternatives: List of alternative materials with confidence scores
                - match_count: Number of alternatives found
                - confidence: Overall confidence in recommendations
                - carbon_reduction_potential: Estimated carbon savings percentage
                - analysis_summary: Human-readable summary

        Example result:
            {
                "alternatives": [
                    {
                        "material_id": "tgo:concrete_recycled",
                        "label": "Recycled Concrete",
                        "confidence": 0.92,
                        "emission_factor": 180.5,
                        "carbon_reduction": 35.2
                    }
                ],
                "match_count": 3,
                "confidence": 0.92,
                "carbon_reduction_potential": 28.5,
                "analysis_summary": "Found 3 lower-carbon alternatives"
            }
        """
        user_query = state.get("user_query", "")
        task_results = state.get("task_results", {}) or {}

        self.logger.info(f"Executing material analysis for query: {user_query}")

        # Extract material context from query or previous results
        material_id = self._extract_material_id(user_query)
        boq_materials = task_results.get("boq_materials", [])

        # If we have BOQ materials from previous agents, match them
        if boq_materials:
            alternatives = await self._match_boq_materials(boq_materials)
        elif material_id:
            # If we extracted a material ID from query, find alternatives
            alternatives = await self._find_alternatives(material_id)
        else:
            # No material context - return empty result
            self.logger.warning("No material context found in query or task_results")
            alternatives = []

        # Calculate overall metrics
        match_count = len(alternatives)
        avg_confidence = (
            sum(alt.get("confidence", 0.0) for alt in alternatives) / match_count
            if match_count > 0
            else 0.0
        )
        carbon_reduction = self._calculate_carbon_reduction(alternatives)

        # Generate summary
        summary = self._generate_summary(alternatives, carbon_reduction)

        result = {
            "alternatives": alternatives[:10],  # Top 10 alternatives
            "match_count": match_count,
            "confidence": round(avg_confidence, 2),
            "carbon_reduction_potential": round(carbon_reduction, 2),
            "analysis_summary": summary,
        }

        self.logger.info(
            f"Material analysis complete: {match_count} alternatives, "
            f"{carbon_reduction:.1f}% carbon reduction potential"
        )

        return result

    async def _find_alternatives(self, material_id: str) -> List[Dict[str, Any]]:
        """Find alternative materials for a given material ID.

        Args:
            material_id: Material identifier to find alternatives for

        Returns:
            List of alternative materials with confidence scores
        """
        # If graphdb_client is available, query TGO for alternatives
        if self.graphdb_client is not None:
            try:
                alternatives = await self._query_tgo_alternatives(material_id)
                return self._rank_by_carbon_reduction(alternatives)
            except Exception as e:
                self.logger.error(f"TGO query failed: {e}", exc_info=True)
                return self._get_mock_alternatives(material_id)
        else:
            # Mock mode for testing
            return self._get_mock_alternatives(material_id)

    async def _match_boq_materials(
        self, boq_materials: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Match BOQ materials using Phase 2 material matching logic.

        Args:
            boq_materials: List of BOQ material dictionaries

        Returns:
            List of matched materials with alternatives
        """
        if self.material_matcher is None or self.graphdb_client is None:
            # Mock mode
            return self._get_mock_alternatives("generic_material")

        try:
            # Import BOQMaterial model
            from suna.backend.boq.models import BOQMaterial

            # Convert dictionaries to BOQMaterial objects if needed
            materials = []
            for mat in boq_materials[:5]:  # Limit to 5 for performance
                if isinstance(mat, dict):
                    # Create BOQMaterial from dict
                    materials.append(
                        BOQMaterial(
                            line_number=mat.get("line_number", 0),
                            description_th=mat.get("description_th", ""),
                            description_en=mat.get("description_en"),
                            quantity=Decimal(str(mat.get("quantity", 1.0))),
                            unit=mat.get("unit", ""),
                            unit_raw=mat.get("unit_raw", mat.get("unit", "")),
                        )
                    )
                else:
                    materials.append(mat)

            # Use Phase 2 matching logic
            matches = self.material_matcher(
                materials, self.graphdb_client, language="th"
            )

            # Convert matches to alternatives format
            alternatives = []
            for match in matches:
                if match.tgo_match and match.confidence > 0.5:
                    alt = {
                        "material_id": match.tgo_match.get("material_id"),
                        "label": match.tgo_match.get("label"),
                        "confidence": match.confidence,
                        "emission_factor": match.tgo_match.get("emission_factor"),
                        "classification": match.classification,
                    }
                    alternatives.append(alt)

                    # Add alternatives from match
                    for idx, match_alt in enumerate(match.alternatives[:3]):
                        alternatives.append(
                            {
                                "material_id": match_alt.get("material_id"),
                                "label": match_alt.get("label"),
                                "confidence": match_alt.get("confidence", 0.0),
                                "emission_factor": match_alt.get("emission_factor"),
                                "classification": "alternative",
                            }
                        )

            return alternatives

        except Exception as e:
            self.logger.error(f"BOQ material matching failed: {e}", exc_info=True)
            return self._get_mock_alternatives("generic_material")

    async def _query_tgo_alternatives(
        self, material_id: str
    ) -> List[Dict[str, Any]]:
        """Query TGO database for material alternatives.

        Args:
            material_id: Material ID to find alternatives for

        Returns:
            List of alternative materials from TGO
        """
        # SECURITY FIX: Sanitize material_id to prevent SPARQL injection
        safe_material_id = self._sanitize_sparql_input(material_id)

        if not safe_material_id:
            self.logger.warning("Empty material_id after sanitization")
            return []

        # SPARQL query to find similar materials with lower emission factors
        query = f"""
        PREFIX tgo: <http://carbonbim.org/tgo/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?material ?label ?emissionFactor
        WHERE {{
            ?material a tgo:Material ;
                     rdfs:label ?label ;
                     tgo:emissionFactor ?emissionFactor .
            FILTER(CONTAINS(LCASE(STR(?material)), LCASE("{safe_material_id}")))
        }}
        ORDER BY ?emissionFactor
        LIMIT 10
        """

        try:
            results = self.graphdb_client.query(query)
            alternatives = []

            for binding in results.get("results", {}).get("bindings", []):
                alternatives.append(
                    {
                        "material_id": binding.get("material", {}).get("value"),
                        "label": binding.get("label", {}).get("value"),
                        "emission_factor": float(
                            binding.get("emissionFactor", {}).get("value", 0.0)
                        ),
                        "confidence": 0.85,  # Default confidence for DB matches
                        "source": "tgo_database",
                    }
                )

            return alternatives

        except Exception as e:
            self.logger.error(f"SPARQL query failed: {e}", exc_info=True)
            return []

    def _extract_material_id(self, query: str) -> Optional[str]:
        """Extract material identifier from user query.

        Uses simple keyword extraction to identify material references.

        Args:
            query: User query string

        Returns:
            Material identifier if found, None otherwise

        Examples:
            >>> agent._extract_material_id("Find alternatives for concrete")
            "concrete"
            >>> agent._extract_material_id("What about steel reinforcement?")
            "steel"
        """
        # Handle None or empty query
        if not query:
            return None

        # Try to extract material IDs first (e.g., tgo:material_123)
        material_id_match = re.search(r"(tgo:[a-zA-Z0-9_]+)", query)
        if material_id_match:
            return material_id_match.group(1)

        # Try to extract quoted material names
        quoted = re.findall(r'"([^"]+)"', query)
        if quoted:
            return quoted[0]

        # Lowercase for matching
        query_lower = query.lower()

        # Common construction materials
        materials = [
            "concrete",
            "steel",
            "rebar",
            "cement",
            "brick",
            "timber",
            "wood",
            "glass",
            "aluminum",
            "aluminium",
            "gypsum",
            "asphalt",
            "gravel",
            "sand",
            "aggregate",
        ]

        # Look for material keywords
        for material in materials:
            if material in query_lower:
                return material

        return None

    def _rank_by_carbon_reduction(
        self, alternatives: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank alternatives by carbon reduction potential.

        Args:
            alternatives: List of alternative materials

        Returns:
            Sorted list with carbon reduction scores added
        """
        if not alternatives:
            return []

        # Calculate baseline (highest emission factor)
        baseline = max(
            alt.get("emission_factor", 0.0) for alt in alternatives if alt.get("emission_factor")
        ) or 1.0

        # Add carbon reduction percentage
        for alt in alternatives:
            emission = alt.get("emission_factor", 0.0)
            if baseline > 0:
                reduction = ((baseline - emission) / baseline) * 100
                alt["carbon_reduction"] = max(0.0, reduction)
            else:
                alt["carbon_reduction"] = 0.0

        # Sort by carbon reduction (descending) and confidence (descending)
        return sorted(
            alternatives,
            key=lambda x: (x.get("carbon_reduction", 0.0), x.get("confidence", 0.0)),
            reverse=True,
        )

    def _calculate_carbon_reduction(
        self, alternatives: List[Dict[str, Any]]
    ) -> float:
        """Calculate average carbon reduction potential.

        Args:
            alternatives: List of alternatives with carbon_reduction scores

        Returns:
            Average carbon reduction percentage
        """
        if not alternatives:
            return 0.0

        reductions = [
            alt.get("carbon_reduction", 0.0)
            for alt in alternatives
            if alt.get("carbon_reduction") is not None
        ]

        return sum(reductions) / len(reductions) if reductions else 0.0

    def _generate_summary(
        self, alternatives: List[Dict[str, Any]], carbon_reduction: float
    ) -> str:
        """Generate human-readable analysis summary.

        Args:
            alternatives: List of alternatives found
            carbon_reduction: Average carbon reduction percentage

        Returns:
            Summary string
        """
        if not alternatives:
            return "No alternative materials found"

        count = len(alternatives)
        high_confidence = sum(1 for alt in alternatives if alt.get("confidence", 0.0) > 0.8)

        if carbon_reduction > 20:
            impact = "significant"
        elif carbon_reduction > 10:
            impact = "moderate"
        else:
            impact = "minor"

        return (
            f"Found {count} alternative materials with {impact} carbon reduction "
            f"potential ({carbon_reduction:.1f}% average). "
            f"{high_confidence} high-confidence matches."
        )

    def _get_mock_alternatives(self, material_id: str) -> List[Dict[str, Any]]:
        """Generate mock alternatives for testing.

        Args:
            material_id: Material identifier

        Returns:
            List of mock alternatives
        """
        # Mock data for testing
        mock_alternatives = [
            {
                "material_id": f"tgo:{material_id}_recycled",
                "label": f"Recycled {material_id.title()}",
                "confidence": 0.92,
                "emission_factor": 180.5,
                "carbon_reduction": 35.2,
                "source": "mock",
            },
            {
                "material_id": f"tgo:{material_id}_low_carbon",
                "label": f"Low-Carbon {material_id.title()}",
                "confidence": 0.88,
                "emission_factor": 210.3,
                "carbon_reduction": 24.6,
                "source": "mock",
            },
            {
                "material_id": f"tgo:{material_id}_standard",
                "label": f"Standard {material_id.title()}",
                "confidence": 0.95,
                "emission_factor": 278.9,
                "carbon_reduction": 0.0,
                "source": "mock",
            },
        ]

        return mock_alternatives

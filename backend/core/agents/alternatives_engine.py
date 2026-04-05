"""Material Alternative Recommendation Engine.

This module implements multi-criteria material alternative recommendations
for carbon reduction opportunities. Uses knowledge graph queries to find
lower-carbon alternatives and ranks them by carbon reduction, cost impact,
availability, and compatibility.
"""

import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MaterialAlternative:
    """Represents a lower-carbon material alternative.

    Attributes:
        material_id: Unique identifier (e.g., "tgo:concrete_recycled")
        name: Human-readable name (bilingual name_en/name_th)
        emission_factor: Emission factor in kgCO2e per unit
        carbon_reduction_kgco2e: Absolute carbon savings in kgCO2e
        carbon_reduction_percentage: Percentage carbon reduction
        cost_impact_percentage: Estimated cost change percentage
        availability: Availability level ("high", "medium", "low")
        compatibility_score: Compatibility with building type (0.0-1.0)
        confidence: Confidence in recommendation quality (0.0-1.0)
        ranking_score: Overall multi-criteria ranking score (0.0-1.0)
    """

    material_id: str
    name: str
    emission_factor: Decimal
    carbon_reduction_kgco2e: Decimal
    carbon_reduction_percentage: float
    cost_impact_percentage: Decimal
    availability: str
    compatibility_score: float
    confidence: float
    ranking_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert Decimal to float for JSON
        result['emission_factor'] = float(self.emission_factor)
        result['carbon_reduction_kgco2e'] = float(self.carbon_reduction_kgco2e)
        result['cost_impact_percentage'] = float(self.cost_impact_percentage)
        return result

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"{self.name} ({self.material_id}): "
            f"{self.carbon_reduction_percentage:.1f}% carbon reduction, "
            f"score={self.ranking_score:.2f}"
        )


class AlternativeRecommendationEngine:
    """Engine for recommending lower-carbon material alternatives.

    This engine:
    1. Queries knowledge graph for same-category materials with lower emissions
    2. Scores candidates using multi-criteria optimization
    3. Ranks alternatives by weighted score (carbon, cost, availability, compatibility)
    4. Returns top 5 recommendations

    Multi-criteria weights (balanced strategy):
        - carbon_reduction: 40%
        - cost_impact: 30%
        - availability: 20%
        - compatibility: 10%
    """

    # Default ranking weights (balanced strategy)
    DEFAULT_WEIGHTS = {
        "carbon_reduction": 0.40,
        "cost_impact": 0.30,
        "availability": 0.20,
        "compatibility": 0.10,
    }

    # Predefined ranking strategies
    RANKING_STRATEGIES = {
        "carbon_first": {
            "carbon_reduction": 0.60,
            "cost_impact": 0.20,
            "availability": 0.15,
            "compatibility": 0.05,
        },
        "cost_constrained": {
            "carbon_reduction": 0.30,
            "cost_impact": 0.50,
            "availability": 0.15,
            "compatibility": 0.05,
        },
        "balanced": {
            "carbon_reduction": 0.40,
            "cost_impact": 0.30,
            "availability": 0.20,
            "compatibility": 0.10,
        },
    }

    def __init__(self, graphdb, tgo_database):
        """Initialize recommendation engine.

        Args:
            graphdb: GraphDBClient instance for SPARQL queries
            tgo_database: TGODatabaseAgent instance for material data
        """
        self.graphdb = graphdb
        self.tgo = tgo_database

    async def recommend_alternatives(
        self,
        material_id: str,
        quantity: Decimal,
        building_type: str,
        user_priorities: Optional[Dict[str, float]] = None,
    ) -> List[MaterialAlternative]:
        """Recommend lower-carbon alternatives with multi-criteria ranking.

        Args:
            material_id: Original material ID (e.g., "tgo:concrete_c30")
            quantity: Material quantity for carbon calculation
            building_type: Building type for compatibility scoring
            user_priorities: Optional custom weights for ranking criteria

        Returns:
            List of MaterialAlternative objects, sorted by ranking_score (highest first)
        """
        logger.info(
            f"Finding alternatives for {material_id}, "
            f"quantity={quantity}, building_type={building_type}"
        )

        # Get original material properties
        original_material = await self.tgo.get_material(material_id)
        if not original_material:
            logger.warning(f"Original material {material_id} not found")
            return []

        original_emission_factor = original_material["emission_factor"]

        # Find candidate alternatives
        candidates = await self._find_candidates(
            material_id, original_emission_factor
        )

        if not candidates:
            logger.info(f"No alternatives found for {material_id}")
            return []

        # Score and rank candidates
        weights = user_priorities or self.DEFAULT_WEIGHTS
        alternatives = []

        for candidate in candidates:
            alternative = await self._score_candidate(
                candidate=candidate,
                original_emission_factor=original_emission_factor,
                quantity=quantity,
                building_type=building_type,
                weights=weights,
            )
            if alternative:
                alternatives.append(alternative)

        # Sort by ranking score (highest first)
        alternatives.sort(key=lambda x: x.ranking_score, reverse=True)

        # Return top 5
        top_alternatives = alternatives[:5]

        logger.info(
            f"Found {len(top_alternatives)} alternatives for {material_id}"
        )

        return top_alternatives

    async def _find_candidates(
        self, material_id: str, original_emission_factor: Decimal
    ) -> List[Dict[str, Any]]:
        """Find candidate materials with lower emission factors.

        Uses SPARQL query to find materials in same category with lower emissions.

        Args:
            material_id: Original material ID
            original_emission_factor: Original emission factor for filtering

        Returns:
            List of candidate material dictionaries
        """
        # SPARQL query to find same-category materials with lower emission factors
        # Following pattern from RESEARCH.md lines 1213-1238
        sparql = f"""
        PREFIX tgo: <http://example.org/tgo#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?material_id ?label ?emission_factor ?category
        WHERE {{
            <{material_id}> tgo:category ?original_category .
            ?material_id tgo:category ?original_category ;
                        rdfs:label ?label ;
                        tgo:hasEmissionFactor ?emission_factor ;
                        tgo:category ?category .
            FILTER(?emission_factor < {float(original_emission_factor)})
            FILTER(?material_id != <{material_id}>)
        }}
        ORDER BY ?emission_factor
        LIMIT 20
        """

        try:
            results = await self.graphdb.query(sparql)
            candidates = []

            for result in results:
                candidates.append({
                    "material_id": result["material_id"]["value"],
                    "label": result["label"]["value"],
                    "emission_factor": Decimal(result["emission_factor"]["value"]),
                    "category": result["category"]["value"],
                })

            logger.debug(f"Found {len(candidates)} candidate alternatives")
            return candidates

        except Exception as e:
            logger.error(f"Error finding candidates: {e}", exc_info=True)
            return []

    async def _score_candidate(
        self,
        candidate: Dict[str, Any],
        original_emission_factor: Decimal,
        quantity: Decimal,
        building_type: str,
        weights: Dict[str, float],
    ) -> Optional[MaterialAlternative]:
        """Score a candidate material using multi-criteria optimization.

        Args:
            candidate: Candidate material dictionary
            original_emission_factor: Original material emission factor
            quantity: Material quantity
            building_type: Building type for compatibility
            weights: Ranking weights

        Returns:
            MaterialAlternative if scoring succeeds, None otherwise
        """
        try:
            material_id = candidate["material_id"]
            emission_factor = candidate["emission_factor"]

            # Calculate carbon reduction
            carbon_reduction_kgco2e = (
                (original_emission_factor - emission_factor) * quantity
            )
            carbon_reduction_percentage = (
                float((original_emission_factor - emission_factor) / original_emission_factor) * 100
            )

            # Get additional material properties
            availability = await self._check_availability(material_id)
            cost_impact = await self._estimate_cost_impact(material_id)
            compatibility = await self._check_compatibility(material_id, building_type)

            # Calculate individual criterion scores (0.0-1.0)
            carbon_score = self._calculate_carbon_score(
                carbon_reduction_kgco2e, quantity
            )
            cost_score = self._calculate_cost_score(cost_impact)
            availability_score = self._calculate_availability_score(availability)
            compatibility_score = compatibility

            # Confidence score (exact category match = high confidence)
            confidence = 1.0 if candidate.get("category") else 0.8

            # Calculate weighted ranking score
            ranking_score = (
                weights.get("carbon_reduction", 0.4) * carbon_score +
                weights.get("cost_impact", 0.3) * cost_score +
                weights.get("availability", 0.2) * availability_score +
                weights.get("compatibility", 0.1) * compatibility_score
            )

            return MaterialAlternative(
                material_id=material_id,
                name=candidate["label"],
                emission_factor=emission_factor,
                carbon_reduction_kgco2e=carbon_reduction_kgco2e,
                carbon_reduction_percentage=carbon_reduction_percentage,
                cost_impact_percentage=cost_impact,
                availability=availability,
                compatibility_score=compatibility_score,
                confidence=confidence,
                ranking_score=ranking_score,
            )

        except Exception as e:
            logger.error(f"Error scoring candidate: {e}", exc_info=True)
            return None

    def _calculate_carbon_score(
        self, carbon_reduction_kgco2e: Decimal, quantity: Decimal
    ) -> float:
        """Calculate carbon reduction score (0.0-1.0).

        Higher reduction = higher score.
        Normalized by quantity to handle different scales.

        Args:
            carbon_reduction_kgco2e: Absolute carbon reduction
            quantity: Material quantity

        Returns:
            Carbon score between 0.0 and 1.0
        """
        # Normalize by quantity: reduction per unit
        reduction_per_unit = float(carbon_reduction_kgco2e / quantity) if quantity > 0 else 0

        # Assume max reasonable reduction is 300 kgCO2e per unit
        # (e.g., replacing high-carbon concrete)
        max_reduction = 300.0
        score = min(reduction_per_unit / max_reduction, 1.0)

        return max(0.0, score)

    def _calculate_cost_score(self, cost_impact_percentage: Decimal) -> float:
        """Calculate cost impact score (0.0-1.0).

        Lower cost increase = higher score.
        Cost decrease = bonus score.

        Args:
            cost_impact_percentage: Cost change percentage

        Returns:
            Cost score between 0.0 and 1.0
        """
        cost_impact = float(cost_impact_percentage)

        # Cost decrease: bonus score (up to 1.0)
        if cost_impact <= 0:
            return min(1.0, 1.0 + abs(cost_impact) / 20.0)

        # Cost increase: penalty (0.0-1.0)
        # Assume max acceptable increase is 50%
        score = 1.0 - (cost_impact / 50.0)
        return max(0.0, min(1.0, score))

    def _calculate_availability_score(self, availability: str) -> float:
        """Calculate availability score (0.0-1.0).

        Args:
            availability: "high", "medium", or "low"

        Returns:
            Availability score
        """
        availability_map = {
            "high": 1.0,
            "medium": 0.6,
            "low": 0.3,
        }
        return availability_map.get(availability, 0.5)

    async def _estimate_cost_impact(self, material_id: str) -> Decimal:
        """Estimate cost impact of using alternative material.

        Placeholder implementation - Phase 5 will integrate actual cost data.

        Args:
            material_id: Material identifier

        Returns:
            Estimated cost change percentage
        """
        # TODO: Phase 5 - integrate actual cost database
        # For now, return placeholder estimate
        # Assume low-carbon alternatives typically cost 5-15% more
        return Decimal("8.5")

    async def _check_availability(self, material_id: str) -> str:
        """Check material availability in market.

        Args:
            material_id: Material identifier

        Returns:
            Availability level: "high", "medium", or "low"
        """
        try:
            material = await self.tgo.get_material(material_id)
            if material and "availability" in material:
                return material["availability"]
        except Exception as e:
            logger.debug(f"Could not check availability for {material_id}: {e}")

        # Fallback: assume "high" if in TGO database
        return "high"

    async def _check_compatibility(
        self, material_id: str, building_type: str
    ) -> float:
        """Check material compatibility with building type.

        Args:
            material_id: Material identifier
            building_type: Building type (residential, commercial, infrastructure)

        Returns:
            Compatibility score between 0.0 and 1.0
        """
        # TODO: Future enhancement - query knowledge graph for building type compatibility
        # For now, use simple heuristic

        # Same category materials are highly compatible
        # This is a placeholder - actual implementation would query knowledge graph
        return 0.95

    async def get_alternative_details(
        self, material_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific alternative material.

        Args:
            material_id: Material identifier

        Returns:
            Material details dictionary or None if not found
        """
        try:
            material = await self.tgo.get_material(material_id)
            return material
        except Exception as e:
            logger.error(f"Error getting material details: {e}", exc_info=True)
            return None

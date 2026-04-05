"""
TREES NC 1.1 (Thai Rating of Energy and Environmental Sustainability for New Construction)
Certification Module.

This module implements the TREES NC 1.1 certification scoring calculator with focus
on Materials & Resources (MR) category credits:
- MR1: Recycled Materials (2 credits)
- MR3: Sustainable Materials (2 credits)
- MR4: Low-Emitting Materials (2 credits)

Certification Thresholds:
- Gold: 50+ points
- Platinum: 70+ points

References:
- TREES NC Version 1.1: https://tgbi.or.th/wp-content/uploads/2024/12/2017_03_TREES-NC-Eng.pdf
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from core.knowledge_graph import GraphDBClient, QueryError

logger = logging.getLogger(__name__)


class TREESError(Exception):
    """Base exception for TREES certification errors."""
    pass


class TREESCertification:
    """
    TREES NC 1.1 Certification Calculator.

    This class provides methods for calculating TREES certification scores,
    analyzing pathways to Gold/Platinum certification, and generating gap analysis.

    Attributes:
        client: GraphDBClient instance for querying TREES criteria
        version: TREES version (default: "1.1")
    """

    # TREES Certification Thresholds
    GOLD_THRESHOLD = 50
    PLATINUM_THRESHOLD = 70

    # MR Category Maximum Points
    MR_CATEGORY_MAX = 10
    MR1_MAX = 2  # Recycled Materials
    MR3_MAX = 2  # Sustainable Materials
    MR4_MAX = 2  # Low-Emitting Materials

    # TREES Namespaces
    TREES_NAMESPACE = "http://tgbi.or.th/trees/ontology#"
    TGO_NAMESPACE = "http://tgo.or.th/ontology#"

    def __init__(self, client: GraphDBClient, version: str = "1.1"):
        """
        Initialize TREES certification calculator.

        Args:
            client: GraphDBClient instance
            version: TREES version (default: "1.1")
        """
        self.client = client
        self.version = version
        self.criteria_cache = {}

    def calculate_mr_credits(self, materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Materials & Resources (MR) category credits.

        Analyzes materials for:
        - MR1: Use of recycled materials (≥30% target)
        - MR3: Use of sustainable/green-labeled materials (≥30% target)
        - MR4: Use of low-emitting materials

        Args:
            materials: List of material dictionaries containing:
                - material_id: Material URI
                - quantity: Material quantity (Decimal)
                - unit: Unit of measurement
                - value: Material value in THB (optional)
                - has_green_label: Boolean (optional)
                - recycled_content: Percentage (0-1, optional)

        Returns:
            Dictionary containing:
                - mr1_score: MR1 credit score (0-2)
                - mr3_score: MR3 credit score (0-2)
                - mr4_score: MR4 credit score (0-2)
                - total_mr_score: Total MR category score (0-10)
                - recycled_percentage: % of recycled materials by value
                - green_labeled_percentage: % of green-labeled materials by value
                - low_emission_percentage: % of low-emission materials
                - details: Detailed breakdown by criterion

        Raises:
            TREESError: If calculation fails
        """
        try:
            total_value = Decimal("0")
            recycled_value = Decimal("0")
            green_labeled_value = Decimal("0")
            low_emission_value = Decimal("0")

            material_details = []

            for material in materials:
                mat_value = Decimal(str(material.get("value", material.get("quantity", 0))))
                total_value += mat_value

                # Query material properties from GraphDB if not provided
                material_props = self._get_material_properties(material.get("material_id"))

                # MR1: Recycled content
                recycled_content = Decimal(str(material.get("recycled_content",
                                                           material_props.get("recycled_content", 0))))
                if recycled_content > 0:
                    recycled_value += mat_value * recycled_content

                # MR3: Green labels (TGO Carbon Label, LEED, etc.)
                has_green_label = material.get("has_green_label",
                                              material_props.get("has_green_label", False))
                if has_green_label:
                    green_labeled_value += mat_value

                # MR4: Low-emitting materials (using TGO emission factor threshold)
                emission_factor = material_props.get("emission_factor", Decimal("999"))
                category_threshold = self._get_low_emission_threshold(
                    material_props.get("category", "")
                )
                if emission_factor <= category_threshold:
                    low_emission_value += mat_value

                material_details.append({
                    "material_id": material.get("material_id"),
                    "label": material_props.get("label_en", "Unknown"),
                    "value": float(mat_value),
                    "recycled_content": float(recycled_content),
                    "has_green_label": has_green_label,
                    "is_low_emission": emission_factor <= category_threshold,
                    "emission_factor": float(emission_factor)
                })

            # Calculate percentages
            recycled_pct = (recycled_value / total_value) if total_value > 0 else Decimal("0")
            green_labeled_pct = (green_labeled_value / total_value) if total_value > 0 else Decimal("0")
            low_emission_pct = (low_emission_value / total_value) if total_value > 0 else Decimal("0")

            # Calculate credit scores
            mr1_score = self._calculate_mr1_score(recycled_pct)
            mr3_score = self._calculate_mr3_score(green_labeled_pct)
            mr4_score = self._calculate_mr4_score(low_emission_pct)

            total_mr_score = mr1_score + mr3_score + mr4_score

            logger.info(
                f"TREES MR Credits: MR1={mr1_score:.1f}, MR3={mr3_score:.1f}, "
                f"MR4={mr4_score:.1f}, Total={total_mr_score:.1f}"
            )

            return {
                "mr1_score": float(mr1_score),
                "mr3_score": float(mr3_score),
                "mr4_score": float(mr4_score),
                "total_mr_score": float(total_mr_score),
                "max_mr_score": self.MR_CATEGORY_MAX,
                "recycled_percentage": float(recycled_pct * 100),
                "green_labeled_percentage": float(green_labeled_pct * 100),
                "low_emission_percentage": float(low_emission_pct * 100),
                "total_material_value": float(total_value),
                "material_count": len(materials),
                "details": material_details,
                "calculation_date": datetime.now().isoformat()
            }

        except Exception as e:
            raise TREESError(f"Failed to calculate MR credits: {str(e)}") from e

    def _calculate_mr1_score(self, recycled_pct: Decimal) -> Decimal:
        """Calculate MR1 score based on recycled content percentage."""
        # TREES NC 1.1: 30% recycled content = 2 points (linear scaling)
        target = Decimal("0.30")
        if recycled_pct >= target:
            return Decimal(str(self.MR1_MAX))
        return (recycled_pct / target) * Decimal(str(self.MR1_MAX))

    def _calculate_mr3_score(self, green_labeled_pct: Decimal) -> Decimal:
        """Calculate MR3 score based on green-labeled materials percentage."""
        # TREES NC 1.1: 30% green-labeled = 2 points (linear scaling)
        target = Decimal("0.30")
        if green_labeled_pct >= target:
            return Decimal(str(self.MR3_MAX))
        return (green_labeled_pct / target) * Decimal(str(self.MR3_MAX))

    def _calculate_mr4_score(self, low_emission_pct: Decimal) -> Decimal:
        """Calculate MR4 score based on low-emitting materials percentage."""
        # TREES NC 1.1: Low-emitting materials (paints, adhesives, sealants, flooring)
        # 50% low-emission = 2 points (linear scaling)
        target = Decimal("0.50")
        if low_emission_pct >= target:
            return Decimal(str(self.MR4_MAX))
        return (low_emission_pct / target) * Decimal(str(self.MR4_MAX))

    def check_gold_pathway(self, current_score: float) -> Dict[str, Any]:
        """
        Analyze pathway to TREES Gold certification (50+ points).

        Args:
            current_score: Current total TREES score

        Returns:
            Dictionary containing:
                - achievable: Whether Gold is achievable
                - current_score: Current score
                - target_score: Gold threshold (50)
                - gap: Points needed for Gold
                - recommendations: List of actions to close gap
                - estimated_effort: Effort level (LOW/MEDIUM/HIGH)
        """
        gap = self.GOLD_THRESHOLD - current_score

        if gap <= 0:
            return {
                "achievable": True,
                "current_score": current_score,
                "target_score": self.GOLD_THRESHOLD,
                "gap": 0,
                "status": "ACHIEVED",
                "recommendations": ["Maintain current practices to retain Gold certification"],
                "estimated_effort": "NONE"
            }

        # Generate recommendations based on gap
        recommendations = []
        effort = "LOW"

        if gap <= 5:
            effort = "LOW"
            recommendations = [
                "Increase recycled materials to 30% of total value (MR1: +2 points)",
                "Specify green-labeled materials (TGO, LEED) for 30% of materials (MR3: +2 points)",
                "Use low-emission paints, adhesives, and finishes (MR4: +2 points)"
            ]
        elif gap <= 15:
            effort = "MEDIUM"
            recommendations = [
                "Focus on high-value MR credits (MR1-MR4: up to 10 points)",
                "Implement energy efficiency measures (EN category: up to 25 points)",
                "Improve water efficiency (WA category: up to 18 points)",
                "Enhance waste management practices (WM category: up to 5 points)"
            ]
        else:
            effort = "HIGH"
            recommendations = [
                "Comprehensive redesign may be required",
                "Engage TREES-certified consultant for full assessment",
                "Consider all credit categories: MR, EN, WA, WM, IEQ, MG, IN",
                f"Target {gap:.0f} points across multiple categories"
            ]

        return {
            "achievable": gap <= 20,  # Achievable if within 20 points
            "current_score": current_score,
            "target_score": self.GOLD_THRESHOLD,
            "gap": max(0, gap),
            "status": "IN_PROGRESS" if gap > 0 else "ACHIEVED",
            "recommendations": recommendations,
            "estimated_effort": effort,
            "analysis_date": datetime.now().isoformat()
        }

    def check_platinum_pathway(self, current_score: float) -> Dict[str, Any]:
        """
        Analyze pathway to TREES Platinum certification (70+ points).

        Args:
            current_score: Current total TREES score

        Returns:
            Dictionary containing:
                - achievable: Whether Platinum is achievable
                - current_score: Current score
                - target_score: Platinum threshold (70)
                - gap: Points needed for Platinum
                - recommendations: List of actions to close gap
                - estimated_effort: Effort level (MEDIUM/HIGH/VERY_HIGH)
        """
        gap = self.PLATINUM_THRESHOLD - current_score

        if gap <= 0:
            return {
                "achievable": True,
                "current_score": current_score,
                "target_score": self.PLATINUM_THRESHOLD,
                "gap": 0,
                "status": "ACHIEVED",
                "recommendations": ["Maintain current practices to retain Platinum certification"],
                "estimated_effort": "NONE"
            }

        # Generate recommendations based on gap
        recommendations = []
        effort = "MEDIUM"

        if gap <= 10:
            effort = "MEDIUM"
            recommendations = [
                "Maximize MR category credits (up to 10 points total)",
                "Achieve high performance in energy category (EN: target 20+ points)",
                "Implement advanced water conservation (WA: target 15+ points)",
                "Pursue innovation credits (IN: up to 4 points)"
            ]
        elif gap <= 20:
            effort = "HIGH"
            recommendations = [
                "Comprehensive optimization across all categories required",
                "Target maximum points in MR (10), EN (25), WA (18)",
                "Implement exemplary IEQ measures (15 points)",
                "Strong management practices (MG: 5 points)",
                "Pursue all available innovation credits (IN: 4 points)"
            ]
        else:
            effort = "VERY_HIGH"
            recommendations = [
                "Platinum certification requires major project redesign",
                "Engage TREES Platinum-experienced consultant",
                "Consider net-zero energy/water features",
                f"Need {gap:.0f} additional points - may require fundamental design changes",
                "Evaluate project constraints and budget for feasibility"
            ]

        return {
            "achievable": gap <= 15,  # Platinum more challenging
            "current_score": current_score,
            "target_score": self.PLATINUM_THRESHOLD,
            "gap": max(0, gap),
            "status": "IN_PROGRESS" if gap > 0 else "ACHIEVED",
            "recommendations": recommendations,
            "estimated_effort": effort,
            "analysis_date": datetime.now().isoformat()
        }

    def generate_certification_report(
        self,
        mr_credits: Dict[str, Any],
        other_category_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive TREES certification status report.

        Args:
            mr_credits: MR credits calculation result from calculate_mr_credits()
            other_category_scores: Optional scores for other categories:
                - EN: Energy (max 25)
                - WA: Water (max 18)
                - WM: Waste Management (max 5)
                - IEQ: Indoor Environmental Quality (max 15)
                - MG: Management (max 5)
                - IN: Innovation (max 4)

        Returns:
            Comprehensive certification report with status, gaps, and recommendations
        """
        # Calculate total score
        total_score = mr_credits["total_mr_score"]

        category_breakdown = {
            "MR": {
                "score": mr_credits["total_mr_score"],
                "max": self.MR_CATEGORY_MAX,
                "percentage": (mr_credits["total_mr_score"] / self.MR_CATEGORY_MAX) * 100
            }
        }

        # Add other categories if provided
        if other_category_scores:
            category_max = {
                "EN": 25, "WA": 18, "WM": 5, "IEQ": 15, "MG": 5, "IN": 4
            }
            for category, score in other_category_scores.items():
                if category in category_max:
                    total_score += score
                    max_score = category_max[category]
                    category_breakdown[category] = {
                        "score": score,
                        "max": max_score,
                        "percentage": (score / max_score) * 100 if max_score > 0 else 0
                    }

        # Determine certification level
        if total_score >= self.PLATINUM_THRESHOLD:
            certification_level = "PLATINUM"
        elif total_score >= self.GOLD_THRESHOLD:
            certification_level = "GOLD"
        else:
            certification_level = "NOT_CERTIFIED"

        # Get pathway analysis
        gold_pathway = self.check_gold_pathway(total_score)
        platinum_pathway = self.check_platinum_pathway(total_score)

        return {
            "certification_level": certification_level,
            "total_score": total_score,
            "max_possible_score": 82,  # Total across all categories
            "percentage": (total_score / 82) * 100,
            "category_breakdown": category_breakdown,
            "mr_details": mr_credits,
            "gold_pathway": gold_pathway,
            "platinum_pathway": platinum_pathway,
            "version": f"TREES NC {self.version}",
            "report_date": datetime.now().isoformat()
        }

    def _get_material_properties(self, material_id: Optional[str]) -> Dict[str, Any]:
        """
        Query material properties from GraphDB.

        Args:
            material_id: Material URI

        Returns:
            Dictionary of material properties
        """
        if not material_id:
            return {}

        # Check cache first
        if material_id in self.criteria_cache:
            return self.criteria_cache[material_id]

        try:
            query = f"""
            PREFIX tgo: <{self.TGO_NAMESPACE}>
            PREFIX trees: <{self.TREES_NAMESPACE}>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?labelEN ?category ?emissionFactor ?hasGreenLabel ?recycledContent
            WHERE {{
                <{material_id}> rdfs:label ?labelEN .
                OPTIONAL {{ <{material_id}> tgo:category ?category }}
                OPTIONAL {{ <{material_id}> tgo:hasEmissionFactor ?emissionFactor }}
                OPTIONAL {{ <{material_id}> trees:hasGreenLabel ?hasGreenLabel }}
                OPTIONAL {{ <{material_id}> trees:recycledContent ?recycledContent }}
                FILTER(lang(?labelEN) = "en" || lang(?labelEN) = "")
            }}
            LIMIT 1
            """

            results = self.client.query(query)
            bindings = results.get("results", {}).get("bindings", [])

            if not bindings:
                return {}

            binding = bindings[0]
            props = {
                "label_en": binding.get("labelEN", {}).get("value"),
                "category": binding.get("category", {}).get("value"),
                "emission_factor": Decimal(binding["emissionFactor"]["value"])
                    if "emissionFactor" in binding else Decimal("999"),
                "has_green_label": binding.get("hasGreenLabel", {}).get("value", "false") == "true",
                "recycled_content": Decimal(binding.get("recycledContent", {}).get("value", "0"))
            }

            # Cache the result
            self.criteria_cache[material_id] = props
            return props

        except QueryError as e:
            logger.warning(f"Failed to query material properties for {material_id}: {e}")
            return {}

    def _get_low_emission_threshold(self, category: str) -> Decimal:
        """
        Get low-emission threshold for material category.

        Based on TREES NC 1.1 low-emission material criteria.

        Args:
            category: Material category

        Returns:
            Emission factor threshold (kgCO2e/unit)
        """
        # Define category-specific thresholds based on TREES criteria
        # These are example values - adjust based on TREES NC 1.1 specifications
        thresholds = {
            "Concrete": Decimal("400"),
            "Steel": Decimal("2000"),
            "Aluminum": Decimal("8000"),
            "Glass": Decimal("600"),
            "Wood": Decimal("100"),
            "Insulation": Decimal("50"),
            "Paint": Decimal("5"),
            "Adhesive": Decimal("3"),
            "Sealant": Decimal("3"),
            "Flooring": Decimal("20")
        }

        return thresholds.get(category, Decimal("999"))  # High default threshold

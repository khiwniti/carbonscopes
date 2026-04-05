"""
Material matching integration for BOQ analysis.

Bridges BOQ parser output with TGO material matching engine.
"""

import logging
from typing import List, Dict, Any, Optional

from .models import BOQMaterial
from core.knowledge_graph.graphdb_client import GraphDBClient

logger = logging.getLogger(__name__)

# Lazy import to avoid dependency issues at module load time
MaterialMatcher = None
MaterialMatchError = None

def _ensure_matcher_imported():
    """Lazy import of MaterialMatcher to avoid loading rapidfuzz at module import time."""
    global MaterialMatcher, MaterialMatchError
    if MaterialMatcher is None:
        try:
            from lca.material_matcher import MaterialMatcher as MM, MaterialMatchError as MME
            MaterialMatcher = MM
            MaterialMatchError = MME
        except ImportError as e:
            logger.error(f"Failed to import MaterialMatcher: {e}")
            raise ImportError(
                "MaterialMatcher requires 'rapidfuzz' package. "
                "Install it with: pip install rapidfuzz"
            ) from e


class BOQMaterialMatch:
    """Matched material with BOQ context and confidence scoring."""

    def __init__(
        self,
        boq_material: BOQMaterial,
        tgo_match: Optional[Dict[str, Any]],
        confidence: float,
        classification: str,
        alternatives: List[Dict[str, Any]] = None
    ):
        self.boq_material = boq_material
        self.tgo_match = tgo_match
        self.confidence = confidence
        self.classification = classification  # auto_match, review_required, rejected
        self.alternatives = alternatives or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "boq_line_number": self.boq_material.line_number,
            "description_th": self.boq_material.description_th,
            "description_en": self.boq_material.description_en,
            "quantity": str(self.boq_material.quantity),
            "unit": self.boq_material.unit,
            "tgo_match": {
                "material_id": self.tgo_match.get("material_id") if self.tgo_match else None,
                "label": self.tgo_match.get("label") if self.tgo_match else None,
                "confidence": self.confidence,
                "classification": self.classification,
                "emission_factor": str(self.tgo_match.get("emission_factor")) if self.tgo_match else None,
                "unit": self.tgo_match.get("unit") if self.tgo_match else None,
            },
            "alternatives": [
                {
                    "material_id": alt.get("material_id"),
                    "label": alt.get("label"),
                    "confidence": alt.get("confidence"),
                    "emission_factor": str(alt.get("emission_factor")),
                }
                for alt in self.alternatives[:3]  # Top 3 alternatives
            ]
        }


def match_boq_materials(
    materials: List[BOQMaterial],
    graphdb_client: GraphDBClient,
    language: str = "th"
) -> List[BOQMaterialMatch]:
    """
    Match BOQ materials to TGO database.

    Args:
        materials: List of parsed BOQ materials
        graphdb_client: GraphDB client instance
        language: Language for matching ("th" or "en")

    Returns:
        List of BOQMaterialMatch with confidence scores and alternatives

    Example:
        >>> matches = match_boq_materials(parsed_boq.materials, graphdb_client)
        >>> for match in matches:
        ...     if match.classification == "auto_match":
        ...         print(f"Auto-matched: {match.boq_material.description_th}")
        ...     elif match.classification == "review_required":
        ...         print(f"Review needed: {match.boq_material.description_th}")
    """
    _ensure_matcher_imported()
    matcher = MaterialMatcher(graphdb_client)
    matches = []

    for boq_material in materials:
        try:
            # Get material description
            description = (
                boq_material.description_th if language == "th"
                else boq_material.description_en or boq_material.description_th
            )

            # Find matches
            search_results = matcher.find_material(
                description,
                language=language,
                category=None  # Auto-detect from description
            )

            if not search_results:
                # No match found
                matches.append(BOQMaterialMatch(
                    boq_material=boq_material,
                    tgo_match=None,
                    confidence=0.0,
                    classification="rejected",
                    alternatives=[]
                ))
                logger.warning(f"No TGO match for: {description}")
                continue

            # Get best match
            best_match = search_results[0]
            confidence = best_match.get('confidence', 0.0)
            classification = matcher.classify_confidence(confidence)

            # Get alternatives (next 3 best matches)
            alternatives = search_results[1:4] if len(search_results) > 1 else []

            matches.append(BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match=best_match,
                confidence=confidence,
                classification=classification,
                alternatives=alternatives
            ))

            logger.debug(
                f"Matched '{description}' to '{best_match.get('label')}' "
                f"(confidence: {confidence:.2f}, {classification})"
            )

        except MaterialMatchError as e:
            logger.error(f"Matching error for {boq_material.description_th}: {e}")
            matches.append(BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match=None,
                confidence=0.0,
                classification="rejected",
                alternatives=[]
            ))

    return matches


def calculate_match_statistics(matches: List[BOQMaterialMatch]) -> Dict[str, Any]:
    """
    Calculate matching statistics for reporting.

    Args:
        matches: List of BOQ material matches

    Returns:
        Statistics dictionary with counts and percentages
    """
    total = len(matches)
    auto_matched = sum(1 for m in matches if m.classification == "auto_match")
    review_required = sum(1 for m in matches if m.classification == "review_required")
    rejected = sum(1 for m in matches if m.classification == "rejected")

    return {
        "total_materials": total,
        "auto_matched": auto_matched,
        "review_required": review_required,
        "rejected": rejected,
        "auto_match_rate": round(auto_matched / total * 100, 2) if total > 0 else 0,
        "success_rate": round((auto_matched + review_required) / total * 100, 2) if total > 0 else 0,
    }

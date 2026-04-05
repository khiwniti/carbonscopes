"""
Material Name Matching for LCA Calculator.

This module provides fuzzy matching capabilities for material names,
supporting both English and Thai language matching against the TGO database.

Example:
    >>> matcher = MaterialMatcher(graphdb_client)
    >>> results = matcher.find_material("คอนกรีต C30", language="th")
    >>> print(results[0]['material_id'])
"""

import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal

from rapidfuzz import fuzz, process
from boq.thai_text_utils import (
    normalize_thai_text,
    extract_material_category_hint,
    expand_thai_abbreviations
)
from core.knowledge_graph.graphdb_client import GraphDBClient, GraphDBError
from core.knowledge_graph.sparql_queries import search_materials, get_emission_factor

logger = logging.getLogger(__name__)


class MaterialMatchError(Exception):
    """Raised when material matching fails."""
    pass


class MaterialMatcher:
    """
    Match material names to TGO database entries.

    Supports:
    - Exact matching
    - Fuzzy matching (Thai and English)
    - Category-based filtering
    - Confidence scoring
    """

    def __init__(self, graphdb_client: GraphDBClient, min_confidence: float = 0.6):
        """
        Initialize the material matcher.

        Args:
            graphdb_client: GraphDB client instance
            min_confidence: Minimum confidence score for fuzzy matches (0.0-1.0)
        """
        self.client = graphdb_client
        self.min_confidence = min_confidence
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized MaterialMatcher with min_confidence={min_confidence}")

    def find_material(
        self,
        material_name: str,
        language: str = "en",
        category: Optional[str] = None,
        exact_match: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find materials matching the given name.

        Enhanced with:
        - Thai abbreviation expansion
        - Category-based filtering (auto-detected if not provided)
        - RapidFuzz multi-algorithm matching

        Args:
            material_name: Material name to search for
            language: Language of the name ("en" or "th")
            category: Optional category filter (e.g., "Concrete", "Steel")
            exact_match: If True, only return exact matches

        Returns:
            List of matched materials with confidence scores, sorted by confidence

        Example:
            >>> results = matcher.find_material("Concrete C30", language="en")
            >>> print(results[0])
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'label': 'Ready-mixed Concrete C30',
                'confidence': 0.95,
                'emission_factor': Decimal('445.6'),
                'unit': 'kgCO2e/m³',
                'category': 'Concrete'
            }
        """
        try:
            # Expand Thai abbreviations
            material_name_expanded = expand_thai_abbreviations(material_name)

            # Auto-detect category if not provided
            if category is None and language == "th":
                category = extract_material_category_hint(material_name_expanded)
                if category != 'unknown':
                    logger.debug(f"Auto-detected category: {category}")

            # Check cache
            cache_key = f"{material_name}:{language}:{category}:{exact_match}"
            if cache_key in self._cache:
                logger.debug(f"Cache hit for: {cache_key}")
                return self._cache[cache_key]

            # Search in GraphDB with category filter
            search_results = search_materials(
                self.client,
                material_name_expanded,
                language=language,
                limit=50,
                category_filter=category
            )

            if not search_results:
                logger.warning(f"No materials found for: {material_name}")
                # Cache empty results too
                self._cache[cache_key] = []
                return []

            # Calculate confidence scores using RapidFuzz
            matched_materials = []
            for result in search_results:
                label = result.get('label', '')
                confidence = self._calculate_confidence(material_name_expanded, label)

                # Skip low confidence matches
                if confidence < self.min_confidence and not exact_match:
                    continue

                # For exact match, only include perfect matches
                if exact_match and confidence < 0.99:
                    continue

                matched_materials.append({
                    'material_id': result['material_id'],
                    'label': label,
                    'confidence': confidence,
                    'emission_factor': result['emission_factor'],
                    'unit': result['unit'],
                    'category': result.get('category'),
                    'effective_date': result.get('effective_date')
                })

            # Sort by confidence (highest first)
            matched_materials.sort(key=lambda x: x['confidence'], reverse=True)

            # Cache results
            self._cache[cache_key] = matched_materials

            logger.info(
                f"Found {len(matched_materials)} matches for '{material_name}' "
                f"(language: {language}, category: {category})"
            )

            return matched_materials

        except GraphDBError as e:
            logger.error(f"GraphDB error while searching for '{material_name}': {e}")
            raise MaterialMatchError(f"Failed to search materials: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in find_material: {e}")
            raise MaterialMatchError(f"Material matching failed: {str(e)}")

    def match_material(
        self,
        material_name: str,
        language: str = "en",
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Match a single material (best match).

        Args:
            material_name: Material name to match
            language: Language of the name ("en" or "th")
            category: Optional category filter

        Returns:
            Best matching material or None if no match found

        Example:
            >>> match = matcher.match_material("Steel Rebar", language="en")
            >>> if match:
            ...     print(f"Matched: {match['label']} (confidence: {match['confidence']})")
        """
        results = self.find_material(material_name, language=language, category=category)

        if not results:
            return None

        # Return best match (highest confidence)
        best_match = results[0]
        logger.debug(
            f"Best match for '{material_name}': {best_match['label']} "
            f"(confidence: {best_match['confidence']:.2f})"
        )
        return best_match

    def match_materials_batch(
        self,
        material_names: List[str],
        language: str = "en",
        category: Optional[str] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Match multiple materials in batch.

        Args:
            material_names: List of material names to match
            language: Language of the names ("en" or "th")
            category: Optional category filter

        Returns:
            Dictionary mapping material names to their best matches

        Example:
            >>> names = ["Concrete C30", "Steel Rebar", "Glass"]
            >>> matches = matcher.match_materials_batch(names)
            >>> for name, match in matches.items():
            ...     if match:
            ...         print(f"{name} -> {match['label']}")
        """
        results = {}
        for name in material_names:
            try:
                match = self.match_material(name, language=language, category=category)
                results[name] = match
            except Exception as e:
                logger.error(f"Error matching '{name}': {str(e)}")
                results[name] = None

        matched_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"Batch matched {matched_count}/{len(material_names)} materials")

        return results

    def get_alternatives(
        self,
        material_name: str,
        language: str = "en",
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get alternative materials (for suggestions when exact match not found).

        Args:
            material_name: Material name to find alternatives for
            language: Language of the name
            category: Optional category filter
            limit: Maximum number of alternatives

        Returns:
            List of alternative materials sorted by relevance

        Example:
            >>> alternatives = matcher.get_alternatives("Unknown Material", category="Concrete")
            >>> for alt in alternatives:
            ...     print(f"Alternative: {alt['label']}")
        """
        results = self.find_material(
            material_name,
            language=language,
            category=category,
            exact_match=False
        )

        # Return top N alternatives
        alternatives = results[:limit]

        logger.debug(f"Found {len(alternatives)} alternatives for '{material_name}'")
        return alternatives

    def _calculate_confidence(self, query: str, target: str) -> float:
        """
        Calculate confidence score for material match using RapidFuzz.

        Uses multi-algorithm scoring:
        - token_set_ratio (50%): Word-order independent matching
        - partial_ratio (30%): Substring matching
        - jaro_winkler (20%): Character-level similarity

        Args:
            query: User's material description
            target: TGO database material name

        Returns:
            Confidence score 0.0-1.0
        """
        # Normalize both texts
        query_norm = normalize_thai_text(query)
        target_norm = normalize_thai_text(target)

        # Exact match
        if query_norm == target_norm:
            return 1.0

        # Substring match (high confidence)
        if query_norm in target_norm or target_norm in query_norm:
            return 0.95

        # Multi-algorithm fuzzy matching
        token_set_score = fuzz.token_set_ratio(query_norm, target_norm) / 100.0
        partial_score = fuzz.partial_ratio(query_norm, target_norm) / 100.0
        jaro_score = fuzz.jaro_winkler_similarity(query_norm, target_norm)

        # Weighted average
        confidence = (
            token_set_score * 0.5 +
            partial_score * 0.3 +
            jaro_score * 0.2
        )

        return round(confidence, 3)

    def classify_confidence(self, confidence: float) -> str:
        """
        Classify confidence level for UI display.

        Args:
            confidence: Confidence score 0.0-1.0

        Returns:
            Classification string: "auto_match", "review_required", or "rejected"

        Thresholds:
        - ≥0.90: Auto-match (high confidence)
        - 0.70-0.89: Flag for manual review
        - <0.70: Reject (too low confidence)
        """
        if confidence >= 0.90:
            return "auto_match"
        elif confidence >= 0.70:
            return "review_required"
        else:
            return "rejected"

    def validate_material(
        self,
        material_id: str,
        include_metadata: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a material ID and retrieve its data.

        Args:
            material_id: Material URI to validate
            include_metadata: If True, includes full metadata

        Returns:
            Material data or None if not found

        Example:
            >>> material = matcher.validate_material(
            ...     "http://tgo.or.th/materials/concrete-c30"
            ... )
            >>> if material:
            ...     print(f"Valid material: {material['label_en']}")
        """
        try:
            result = get_emission_factor(
                self.client,
                material_id,
                include_metadata=include_metadata
            )
            logger.debug(f"Validated material: {material_id}")
            return result

        except Exception as e:
            logger.warning(f"Material validation failed for {material_id}: {str(e)}")
            return None

    def get_match_report(
        self,
        material_name: str,
        language: str = "en",
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed match report for debugging/analysis.

        Args:
            material_name: Material name to match
            language: Language of the name
            category: Optional category filter

        Returns:
            Detailed match report with statistics

        Example:
            >>> report = matcher.get_match_report("Concrete")
            >>> print(f"Found {report['match_count']} matches")
            >>> print(f"Best match: {report['best_match']['label']}")
        """
        matches = self.find_material(material_name, language=language, category=category)

        if not matches:
            return {
                'query': material_name,
                'language': language,
                'category': category,
                'match_count': 0,
                'best_match': None,
                'avg_confidence': 0.0,
                'alternatives': []
            }

        best_match = matches[0]
        avg_confidence = sum(m['confidence'] for m in matches) / len(matches)

        return {
            'query': material_name,
            'language': language,
            'category': category,
            'match_count': len(matches),
            'best_match': best_match,
            'avg_confidence': avg_confidence,
            'confidence_range': {
                'min': min(m['confidence'] for m in matches),
                'max': max(m['confidence'] for m in matches),
            },
            'alternatives': matches[1:6] if len(matches) > 1 else []
        }

    def clear_cache(self) -> None:
        """Clear the match cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared match cache ({cache_size} entries)")

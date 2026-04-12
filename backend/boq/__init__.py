"""
BOQ (Bill of Quantities) Parser Module.

This module provides parsing capabilities for Thai construction BOQ Excel files,
supporting complex formatting including merged cells, bilingual headers, and mixed units.

Main Components:
- parser: BOQ Excel file parsing
- unit_normalizer: Thai unit to SI unit conversion
- models: Pydantic data models for BOQ data
- cache: Multi-layer Redis caching for BOQ analysis (Plan 02-04)
- material_matching: TGO material matching for BOQ materials
- carbon_pipeline: End-to-end carbon calculation pipeline (coming in Plan 02-03)
- audit_trail: Calculation audit trail models (coming in Plan 02-03)

Example Usage:
    >>> from carbonscope.backend.boq import parse_boq
    >>> result = parse_boq("/path/to/boq.xlsx")
    >>> print(f"Parsed {len(result.materials)} materials")
    >>> print(f"Success rate: {result.metadata['success_rate']}%")

    >>> from carbonscope.backend.boq import get_cache_manager
    >>> cache = get_cache_manager()
    >>> stats = cache.get_cache_stats()
    >>> print(f"Cache hit rate: {stats['hit_rate']}%")
"""

from .parser import parse_boq, detect_header_row
from .unit_normalizer import normalize_unit, get_unit_category, THAI_UNIT_MAPPINGS
from .models import BOQMaterial, BOQParseResult, BOQError
from .cache import BOQCacheManager, get_cache_manager

# Note: Import these directly when needed to avoid circular dependencies
# from .material_matching import match_boq_materials, calculate_match_statistics, BOQMaterialMatch
# from .carbon_pipeline import CarbonCalculationPipeline
# from .audit_trail import CalculationAudit, MaterialCalculationAudit

__all__ = [
    'parse_boq',
    'detect_header_row',
    'normalize_unit',
    'get_unit_category',
    'THAI_UNIT_MAPPINGS',
    'BOQMaterial',
    'BOQParseResult',
    'BOQError',
    'BOQCacheManager',
    'get_cache_manager',
    # 'match_boq_materials',
    # 'calculate_match_statistics',
    # 'BOQMaterialMatch',
    # 'CarbonCalculationPipeline',
    # 'CalculationAudit',
    # 'MaterialCalculationAudit',
]

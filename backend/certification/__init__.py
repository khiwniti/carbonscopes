"""
Certification module for TREES NC 1.1 and EDGE V3 compliance.

This module provides:
- TREES NC 1.1 certification scoring and pathway analysis
- EDGE V3 baseline calculation and reduction tracking
- Gap analysis for certification compliance
- Certification report generation

Example:
    >>> from certification import TREESCertification, EDGECertification
    >>> trees = TREESCertification(graphdb_client)
    >>> score = trees.calculate_mr_credits(materials)
    >>> pathway = trees.check_gold_pathway(score)
"""

from .trees import TREESCertification, TREESError
from .edge import EDGECertification, EDGEError

__all__ = [
    "TREESCertification",
    "TREESError",
    "EDGECertification",
    "EDGEError",
]

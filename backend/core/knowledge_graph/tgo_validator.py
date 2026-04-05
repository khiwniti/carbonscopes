"""Simple validation utilities for TGO material data.

Ensures:
- Required fields present
- Emission factor > 0
- Unicode labels are NFC normalized
"""

import unicodedata
from typing import Dict, List

REQUIRED_FIELDS = [
    "id",
    "name_en",
    "name_th",
    "emission_factor",
    "unit",
    "category",
    "effective_date",
    "source_document",
]


def is_normalized(text: str) -> bool:
    """Check if a string is NFC normalized."""
    return unicodedata.is_normalized("NFC", text)


def validate_material(material: Dict) -> List[str]:
    """Validate a single material dictionary.
    Returns a list of error messages (empty if valid).
    """
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in material:
            errors.append(f"Missing required field: {field}")
    # Emission factor positivity
    try:
        val = float(material.get("emission_factor", 0))
        if val <= 0:
            errors.append("Emission factor must be positive")
    except Exception:
        errors.append("Emission factor not a number")
    # Unicode normalization for labels
    for lang_field in ["name_en", "name_th"]:
        txt = material.get(lang_field, "")
        if not is_normalized(txt):
            errors.append(f"{lang_field} not NFC normalized")
    return errors


def validate_materials(materials: List[Dict]) -> List[str]:
    """Validate a list of materials, returning aggregated errors with indices."""
    agg: List[str] = []
    for i, m in enumerate(materials):
        errs = validate_material(m)
        for e in errs:
            agg.append(f"Material {i}: {e}")
    return agg

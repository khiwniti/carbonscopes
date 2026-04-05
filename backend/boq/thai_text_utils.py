"""
Thai text processing utilities for material matching.

Handles abbreviation expansion and text normalization for Thai construction materials.
"""

import re
from typing import Dict


# Thai construction material abbreviations
THAI_ABBREVIATIONS: Dict[str, str] = {
    # Material abbreviations
    'คสล.': 'คอนกรีต',
    'รง.': 'ระยะเวลา',

    # Unit abbreviations (for text normalization)
    'ตร.ม.': 'ตารางเมตร',
    'ลบ.ม.': 'ลูกบาศก์เมตร',
    'ม.': 'เมตร',
    'กก.': 'กิโลกรัม',

    # Common construction terms
    'ก.ม.': 'กิโลเมตร',
    'ซ.ม.': 'เซนติเมตร',
    'มม.': 'มิลลิเมตร',
}


def expand_thai_abbreviations(text: str) -> str:
    """
    Expand Thai abbreviations in material descriptions.

    Args:
        text: Material description text (Thai or mixed Thai/English)

    Returns:
        Text with abbreviations expanded

    Example:
        >>> expand_thai_abbreviations("คสล. C30 100 ตร.ม.")
        'คอนกรีต C30 100 ตารางเมตร'
    """
    result = text

    # Replace each abbreviation
    for abbr, full in THAI_ABBREVIATIONS.items():
        # Use word boundary matching to avoid partial replacements
        result = result.replace(abbr, full)

    return result


def normalize_thai_text(text: str) -> str:
    """
    Normalize Thai text for matching.

    - Expand abbreviations
    - Normalize whitespace
    - Convert to lowercase (English parts only)
    - Remove special characters

    Args:
        text: Material description text

    Returns:
        Normalized text
    """
    # Expand abbreviations
    result = expand_thai_abbreviations(text)

    # Normalize whitespace
    result = re.sub(r'\s+', ' ', result).strip()

    # Lowercase English characters (preserve Thai)
    # Thai characters don't have case, so only affect ASCII
    result = ''.join(
        c.lower() if c.isascii() and c.isalpha() else c
        for c in result
    )

    return result


def extract_material_category_hint(text: str) -> str:
    """
    Extract category hint from material description.

    Looks for keywords indicating material category (Concrete, Steel, Glass, etc.)
    to enable category-based filtering in matching.

    Args:
        text: Material description text

    Returns:
        Category hint string (lowercase) or "unknown"

    Example:
        >>> extract_material_category_hint("คอนกรีตผสมเสร็จ C30")
        'concrete'
        >>> extract_material_category_hint("เหล็กเสริม SD40")
        'steel'
    """
    text_lower = text.lower()

    # Thai keywords
    if 'คอนกรีต' in text_lower or 'คสล' in text_lower or 'concrete' in text_lower:
        return 'concrete'
    if 'เหล็ก' in text_lower or 'steel' in text_lower:
        return 'steel'
    if 'กระจก' in text_lower or 'glass' in text_lower:
        return 'glass'
    if 'ไม้' in text_lower or 'wood' in text_lower or 'timber' in text_lower:
        return 'wood'
    if 'อลูมิเนียม' in text_lower or 'aluminum' in text_lower or 'aluminium' in text_lower:
        return 'aluminum'
    if 'ฉนวน' in text_lower or 'insulation' in text_lower:
        return 'insulation'

    return 'unknown'

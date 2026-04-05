"""
Thai Unit Normalization.

Converts Thai construction units to SI standards for carbon calculation.
All conversion factors use Decimal for deterministic calculations.
"""

from decimal import Decimal
from typing import Tuple


# Thai → (SI unit, conversion factor)
THAI_UNIT_MAPPINGS = {
    # Volume
    'ลบ.ม.': ('m³', Decimal('1.0')),
    'cubic meter': ('m³', Decimal('1.0')),
    'ลบ.เมตร': ('m³', Decimal('1.0')),

    # Area
    'ตร.ม.': ('m²', Decimal('1.0')),
    'square meter': ('m²', Decimal('1.0')),
    'ตร.เมตร': ('m²', Decimal('1.0')),

    # Weight
    'กก.': ('kg', Decimal('1.0')),
    'kilogram': ('kg', Decimal('1.0')),
    'ตัน': ('kg', Decimal('1000.0')),
    'ton': ('kg', Decimal('1000.0')),
    'tonne': ('kg', Decimal('1000.0')),

    # Length
    'ม.': ('m', Decimal('1.0')),
    'เมตร': ('m', Decimal('1.0')),
    'meter': ('m', Decimal('1.0')),

    # Count
    'เส้น': ('unit', Decimal('1.0')),
    'piece': ('unit', Decimal('1.0')),
    'ชุด': ('unit', Decimal('1.0')),
    'set': ('unit', Decimal('1.0')),
}


def normalize_unit(raw_unit: str) -> Tuple[str, Decimal]:
    """
    Normalize Thai or English unit to SI standard.

    Args:
        raw_unit: Original unit string (Thai or English)

    Returns:
        Tuple of (normalized_unit, conversion_factor)

    Raises:
        ValueError: If unit is unrecognized

    Examples:
        >>> normalize_unit('ลบ.ม.')
        ('m³', Decimal('1.0'))
        >>> normalize_unit('ตัน')
        ('kg', Decimal('1000.0'))
    """
    # Clean input: strip whitespace, lowercase
    cleaned = raw_unit.strip().lower()

    # Try exact match first
    if cleaned in THAI_UNIT_MAPPINGS:
        return THAI_UNIT_MAPPINGS[cleaned]

    # Try case-insensitive match
    for key, value in THAI_UNIT_MAPPINGS.items():
        if key.lower() == cleaned:
            return value

    # Unrecognized unit
    raise ValueError(f"Unrecognized unit: {raw_unit}")


def get_unit_category(unit: str) -> str:
    """
    Get category for unit (volume, area, weight, length, count).

    Args:
        unit: Normalized unit string (m³, kg, etc.)

    Returns:
        Category name or 'unknown'

    Examples:
        >>> get_unit_category('m³')
        'volume'
        >>> get_unit_category('kg')
        'weight'
    """
    unit_categories = {
        'm³': 'volume',
        'm²': 'area',
        'kg': 'weight',
        'm': 'length',
        'unit': 'count',
    }
    return unit_categories.get(unit, 'unknown')

"""Validation utilities for Brightway2 carbon calculations.

Provides functions to compare automated results against manual assessments.
"""

from decimal import Decimal


def percent_error(automated: Decimal, manual: Decimal) -> Decimal:
    """Calculate percentage error between automated and manual results.
    Returns absolute percentage error.
    """
    if manual == 0:
        raise ValueError("Manual total carbon cannot be zero for error calculation")
    return abs((automated - manual) / manual) * Decimal("100")

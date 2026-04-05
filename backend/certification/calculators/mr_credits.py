"""
TREES Materials & Resources (MR) Credits Calculator.

Helper functions for calculating individual MR credits:
- MR1: Recycled Materials
- MR3: Sustainable Materials
- MR4: Low-Emitting Materials
"""

from decimal import Decimal
from typing import Dict, Any, List


def calculate_recycled_content_score(
    materials: List[Dict[str, Any]],
    target_percentage: Decimal = Decimal("0.30"),
    max_points: Decimal = Decimal("2.0")
) -> Dict[str, Any]:
    """
    Calculate MR1 credit score for recycled content.

    TREES NC 1.1 MR1: Use of recycled materials (≥30% target = 2 points)

    Args:
        materials: List of materials with recycled_content and value
        target_percentage: Target recycled percentage (default 30%)
        max_points: Maximum points available (default 2.0)

    Returns:
        Dictionary with score and breakdown
    """
    total_value = Decimal("0")
    recycled_value = Decimal("0")

    for mat in materials:
        value = Decimal(str(mat.get("value", 0)))
        recycled_pct = Decimal(str(mat.get("recycled_content", 0)))

        total_value += value
        recycled_value += value * recycled_pct

    recycled_percentage = (recycled_value / total_value) if total_value > 0 else Decimal("0")

    # Linear scoring: 30% = 2 points
    score = min(max_points, (recycled_percentage / target_percentage) * max_points)

    return {
        "score": float(score),
        "recycled_percentage": float(recycled_percentage * 100),
        "target_percentage": float(target_percentage * 100),
        "total_value": float(total_value),
        "recycled_value": float(recycled_value),
        "meets_target": recycled_percentage >= target_percentage
    }


def calculate_green_label_score(
    materials: List[Dict[str, Any]],
    target_percentage: Decimal = Decimal("0.30"),
    max_points: Decimal = Decimal("2.0")
) -> Dict[str, Any]:
    """
    Calculate MR3 credit score for green-labeled materials.

    TREES NC 1.1 MR3: Use of sustainable/green-labeled materials (≥30% target = 2 points)

    Args:
        materials: List of materials with has_green_label and value
        target_percentage: Target green-labeled percentage (default 30%)
        max_points: Maximum points available (default 2.0)

    Returns:
        Dictionary with score and breakdown
    """
    total_value = Decimal("0")
    green_labeled_value = Decimal("0")

    for mat in materials:
        value = Decimal(str(mat.get("value", 0)))
        has_green_label = mat.get("has_green_label", False)

        total_value += value
        if has_green_label:
            green_labeled_value += value

    green_percentage = (green_labeled_value / total_value) if total_value > 0 else Decimal("0")

    # Linear scoring: 30% = 2 points
    score = min(max_points, (green_percentage / target_percentage) * max_points)

    return {
        "score": float(score),
        "green_labeled_percentage": float(green_percentage * 100),
        "target_percentage": float(target_percentage * 100),
        "total_value": float(total_value),
        "green_labeled_value": float(green_labeled_value),
        "meets_target": green_percentage >= target_percentage
    }


def calculate_low_emission_score(
    materials: List[Dict[str, Any]],
    target_percentage: Decimal = Decimal("0.50"),
    max_points: Decimal = Decimal("2.0")
) -> Dict[str, Any]:
    """
    Calculate MR4 credit score for low-emitting materials.

    TREES NC 1.1 MR4: Use of low-emitting materials (≥50% target = 2 points)

    Args:
        materials: List of materials with is_low_emission and value
        target_percentage: Target low-emission percentage (default 50%)
        max_points: Maximum points available (default 2.0)

    Returns:
        Dictionary with score and breakdown
    """
    total_value = Decimal("0")
    low_emission_value = Decimal("0")

    for mat in materials:
        value = Decimal(str(mat.get("value", 0)))
        is_low_emission = mat.get("is_low_emission", False)

        total_value += value
        if is_low_emission:
            low_emission_value += value

    low_emission_percentage = (low_emission_value / total_value) if total_value > 0 else Decimal("0")

    # Linear scoring: 50% = 2 points
    score = min(max_points, (low_emission_percentage / target_percentage) * max_points)

    return {
        "score": float(score),
        "low_emission_percentage": float(low_emission_percentage * 100),
        "target_percentage": float(target_percentage * 100),
        "total_value": float(total_value),
        "low_emission_value": float(low_emission_value),
        "meets_target": low_emission_percentage >= target_percentage
    }

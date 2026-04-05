"""
EDGE Reduction Calculator.

Helper functions for EDGE V3 reduction calculations and projections.
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple


def calculate_reduction_percentage(
    actual: Decimal,
    baseline: Decimal
) -> Decimal:
    """
    Calculate percentage reduction from baseline.

    Args:
        actual: Actual value
        baseline: Baseline value

    Returns:
        Percentage reduction (0-100)
    """
    if baseline <= 0:
        return Decimal("0")

    reduction = baseline - actual
    percentage = (reduction / baseline) * Decimal("100")

    return max(Decimal("0"), percentage)  # Ensure non-negative


def calculate_target_carbon(
    baseline: Decimal,
    target_reduction_percentage: Decimal
) -> Decimal:
    """
    Calculate target carbon value for given reduction percentage.

    Args:
        baseline: Baseline carbon footprint
        target_reduction_percentage: Target reduction (0-100)

    Returns:
        Target carbon value
    """
    reduction_factor = target_reduction_percentage / Decimal("100")
    target = baseline * (Decimal("1") - reduction_factor)

    return target


def calculate_required_savings(
    actual: Decimal,
    baseline: Decimal,
    target_reduction_percentage: Decimal
) -> Dict[str, Any]:
    """
    Calculate additional savings required to meet target.

    Args:
        actual: Current actual carbon
        baseline: Baseline carbon
        target_reduction_percentage: Target reduction percentage

    Returns:
        Dictionary with required savings breakdown
    """
    target_carbon = calculate_target_carbon(baseline, target_reduction_percentage)
    current_reduction = calculate_reduction_percentage(actual, baseline)

    gap_carbon = actual - target_carbon
    gap_percentage = target_reduction_percentage - current_reduction

    return {
        "current_reduction_percentage": float(current_reduction),
        "target_reduction_percentage": float(target_reduction_percentage),
        "gap_percentage": float(max(Decimal("0"), gap_percentage)),
        "target_carbon": float(target_carbon),
        "current_carbon": float(actual),
        "additional_savings_required": float(max(Decimal("0"), gap_carbon)),
        "meets_target": gap_carbon <= 0
    }


def project_reduction_impact(
    current_carbon: Decimal,
    baseline: Decimal,
    material_swaps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Project impact of material swaps on reduction percentage.

    Args:
        current_carbon: Current carbon footprint
        baseline: Baseline carbon
        material_swaps: List of proposed swaps with:
            - material_name: Name of material
            - current_carbon: Current material carbon
            - new_carbon: Proposed material carbon
            - quantity: Material quantity

    Returns:
        Projection of new reduction percentage
    """
    total_savings = Decimal("0")

    swap_details = []
    for swap in material_swaps:
        current = Decimal(str(swap.get("current_carbon", 0)))
        new = Decimal(str(swap.get("new_carbon", 0)))
        savings = current - new

        total_savings += savings

        swap_details.append({
            "material_name": swap.get("material_name"),
            "current_carbon": float(current),
            "new_carbon": float(new),
            "savings": float(savings),
            "reduction_percentage": float((savings / current * 100) if current > 0 else 0)
        })

    projected_carbon = current_carbon - total_savings
    projected_reduction = calculate_reduction_percentage(projected_carbon, baseline)

    return {
        "current_carbon": float(current_carbon),
        "projected_carbon": float(projected_carbon),
        "total_savings": float(total_savings),
        "current_reduction_percentage": float(calculate_reduction_percentage(current_carbon, baseline)),
        "projected_reduction_percentage": float(projected_reduction),
        "improvement": float(projected_reduction - calculate_reduction_percentage(current_carbon, baseline)),
        "swap_details": swap_details
    }


def calculate_breakeven_analysis(
    baseline: Decimal,
    target_reduction: Decimal,
    category_contributions: Dict[str, Decimal]
) -> List[Dict[str, Any]]:
    """
    Analyze which categories need reduction to meet target.

    Args:
        baseline: Baseline carbon
        target_reduction: Target reduction percentage
        category_contributions: Current carbon by category

    Returns:
        List of category recommendations
    """
    target_carbon = calculate_target_carbon(baseline, target_reduction)
    current_carbon = sum(category_contributions.values())
    required_savings = current_carbon - target_carbon

    recommendations = []

    # Calculate each category's potential
    for category, carbon in sorted(category_contributions.items(), key=lambda x: x[1], reverse=True):
        percentage_of_total = (carbon / current_carbon * Decimal("100")) if current_carbon > 0 else Decimal("0")

        # Estimate realistic reduction potential (20-40% depending on category)
        reduction_potential = {
            "Concrete": Decimal("0.30"),  # 30% potential with alternatives
            "Steel": Decimal("0.20"),     # 20% with recycled content
            "Aluminum": Decimal("0.40"),  # 40% with recycled aluminum
            "Glass": Decimal("0.15"),     # 15% limited alternatives
            "Wood": Decimal("0.10")       # 10% already low-carbon
        }.get(category, Decimal("0.20"))  # Default 20%

        potential_savings = carbon * reduction_potential

        recommendations.append({
            "category": category,
            "current_carbon": float(carbon),
            "percentage_of_total": float(percentage_of_total),
            "reduction_potential": float(reduction_potential * 100),
            "potential_savings": float(potential_savings),
            "priority": "HIGH" if percentage_of_total > 30 else "MEDIUM" if percentage_of_total > 15 else "LOW"
        })

    return recommendations

#!/usr/bin/env python3
"""
Example usage of TREES and EDGE certification modules.

This script demonstrates:
1. TREES NC 1.1 MR credits calculation
2. Gold/Platinum pathway analysis
3. EDGE V3 baseline and reduction calculation
4. EDGE compliance checking
5. Comprehensive certification reports

Usage:
    python example_usage.py
"""

from decimal import Decimal
from core.knowledge_graph import GraphDBClient
from certification import TREESCertification, EDGECertification


def example_trees_certification():
    """Example: TREES NC 1.1 certification analysis."""
    print("=" * 80)
    print("TREES NC 1.1 CERTIFICATION EXAMPLE")
    print("=" * 80)

    # Initialize GraphDB client (replace with actual endpoint)
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

    # Initialize TREES certification calculator
    trees = TREESCertification(client)

    # Example project materials
    materials = [
        {
            "material_id": "http://tgo.or.th/materials/concrete-c30",
            "quantity": 500,
            "value": 150000,  # THB
            "recycled_content": 0.35,  # 35% recycled
            "has_green_label": True  # TGO Carbon Label
        },
        {
            "material_id": "http://tgo.or.th/materials/steel-rebar",
            "quantity": 50,
            "value": 75000,
            "recycled_content": 0.60,  # 60% recycled steel
            "has_green_label": True
        },
        {
            "material_id": "http://tgo.or.th/materials/aluminum-frame",
            "quantity": 20,
            "value": 50000,
            "recycled_content": 0.20,
            "has_green_label": False
        },
        {
            "material_id": "http://tgo.or.th/materials/glass-float",
            "quantity": 100,
            "value": 40000,
            "recycled_content": 0.15,
            "has_green_label": False
        }
    ]

    print("\n1. Calculate MR (Materials & Resources) Credits")
    print("-" * 80)
    mr_credits = trees.calculate_mr_credits(materials)

    print(f"MR1 Score (Recycled Materials): {mr_credits['mr1_score']:.2f} / 2.0")
    print(f"  Recycled Content: {mr_credits['recycled_percentage']:.1f}% (target: 30%)")
    print(f"\nMR3 Score (Green-Labeled Materials): {mr_credits['mr3_score']:.2f} / 2.0")
    print(f"  Green-Labeled: {mr_credits['green_labeled_percentage']:.1f}% (target: 30%)")
    print(f"\nMR4 Score (Low-Emitting Materials): {mr_credits['mr4_score']:.2f} / 2.0")
    print(f"  Low-Emission: {mr_credits['low_emission_percentage']:.1f}% (target: 50%)")
    print(f"\nTotal MR Score: {mr_credits['total_mr_score']:.1f} / {mr_credits['max_mr_score']}")

    # Example: Add other category scores
    other_category_scores = {
        "EN": 18.5,  # Energy
        "WA": 14.0,  # Water
        "WM": 3.5,   # Waste Management
        "IEQ": 11.0, # Indoor Environmental Quality
        "MG": 4.0    # Management
    }

    print("\n2. Generate Comprehensive Certification Report")
    print("-" * 80)
    report = trees.generate_certification_report(mr_credits, other_category_scores)

    print(f"Certification Level: {report['certification_level']}")
    print(f"Total Score: {report['total_score']:.1f} / {report['max_possible_score']}")
    print(f"Achievement: {report['percentage']:.1f}%")

    print("\nCategory Breakdown:")
    for category, data in report['category_breakdown'].items():
        print(f"  {category}: {data['score']:.1f} / {data['max']} ({data['percentage']:.1f}%)")

    print("\n3. Gold Pathway Analysis")
    print("-" * 80)
    gold_pathway = report['gold_pathway']
    print(f"Status: {gold_pathway['status']}")
    print(f"Current Score: {gold_pathway['current_score']:.1f}")
    print(f"Gold Target: {gold_pathway['target_score']}")
    print(f"Gap: {gold_pathway['gap']:.1f} points")
    print(f"Effort Level: {gold_pathway['estimated_effort']}")
    print("\nRecommendations:")
    for rec in gold_pathway['recommendations']:
        print(f"  - {rec}")

    print("\n4. Platinum Pathway Analysis")
    print("-" * 80)
    platinum_pathway = report['platinum_pathway']
    print(f"Status: {platinum_pathway['status']}")
    print(f"Platinum Target: {platinum_pathway['target_score']}")
    print(f"Gap: {platinum_pathway['gap']:.1f} points")
    print(f"Effort Level: {platinum_pathway['estimated_effort']}")
    print("\nRecommendations:")
    for rec in platinum_pathway['recommendations'][:3]:  # Show first 3
        print(f"  - {rec}")


def example_edge_certification():
    """Example: EDGE V3 certification analysis."""
    print("\n\n" + "=" * 80)
    print("EDGE V3 CERTIFICATION EXAMPLE")
    print("=" * 80)

    # Initialize GraphDB client
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

    # Initialize EDGE certification calculator
    edge = EDGECertification(client)

    print("\n1. Calculate Baseline Carbon Footprint")
    print("-" * 80)
    baseline = edge.calculate_baseline(
        project_type="residential",
        floor_area=Decimal("2500")  # 2,500 m²
    )

    print(f"Project Type: {baseline['project_type']}")
    print(f"Floor Area: {baseline['floor_area']:.1f} m²")
    print(f"Baseline Total: {baseline['baseline_total']:,.2f} kgCO2e")
    print(f"Baseline per m²: {baseline['baseline_per_sqm']:.2f} kgCO2e/m²")
    print(f"Methodology: {baseline['methodology']}")

    print("\n2. Calculate Reduction from Baseline")
    print("-" * 80)

    # Example: Project with optimized materials achieves lower carbon
    actual_carbon = Decimal("560000")  # 560,000 kgCO2e

    reduction = edge.calculate_reduction(
        actual_carbon=actual_carbon,
        baseline_carbon=Decimal(str(baseline['baseline_total']))
    )

    print(f"Baseline Carbon: {reduction['baseline_carbon']:,.2f} kgCO2e")
    print(f"Actual Carbon: {reduction['actual_carbon']:,.2f} kgCO2e")
    print(f"Absolute Reduction: {reduction['reduction_absolute']:,.2f} kgCO2e")
    print(f"Reduction Percentage: {reduction['reduction_percentage']:.1f}%")
    print(f"Target: {reduction['target_percentage']:.0f}%")
    print(f"Meets EDGE Threshold: {'YES' if reduction['meets_edge_threshold'] else 'NO'}")

    if reduction['gap_percentage'] > 0:
        print(f"Gap to Target: {reduction['gap_percentage']:.1f}%")

    print("\n3. Check EDGE Compliance")
    print("-" * 80)

    compliance = edge.check_edge_compliance(
        reduction_percentage=Decimal(str(reduction['reduction_percentage'])),
        energy_reduction=Decimal("35"),  # 35% energy reduction
        water_reduction=Decimal("25")    # 25% water reduction
    )

    print(f"EDGE Certified: {'YES' if compliance['edge_certified'] else 'NO'}")
    print(f"EDGE Advanced: {'YES' if compliance['edge_advanced'] else 'NO'}")

    print("\nEmbodied Carbon Status:")
    ec_status = compliance['embodied_carbon_status']
    print(f"  Compliant: {ec_status['compliant']}")
    print(f"  Reduction: {ec_status['reduction_percentage']:.1f}%")
    print(f"  Target: {ec_status['target_percentage']:.0f}%")
    if ec_status['gap'] > 0:
        print(f"  Gap: {ec_status['gap']:.1f}%")

    if compliance['energy_status']:
        print("\nEnergy Status:")
        en_status = compliance['energy_status']
        print(f"  Compliant: {en_status['compliant']}")
        print(f"  Reduction: {en_status['reduction_percentage']:.1f}%")
        print(f"  Target: {en_status['target_percentage']:.0f}%")

    if compliance['water_status']:
        print("\nWater Status:")
        wa_status = compliance['water_status']
        print(f"  Compliant: {wa_status['compliant']}")
        print(f"  Reduction: {wa_status['reduction_percentage']:.1f}%")
        print(f"  Target: {wa_status['target_percentage']:.0f}%")

    print("\nRecommendations:")
    for rec in compliance['recommendations']:
        print(f"  - {rec}")

    print("\n4. Generate EDGE Report")
    print("-" * 80)

    report = edge.generate_edge_report(baseline, reduction, compliance)

    cert_status = report['certification_status']
    print(f"Certification Status: {cert_status['certification_level']}")
    print(f"EDGE Certified: {cert_status['edge_certified']}")
    print(f"EDGE Advanced: {cert_status['edge_advanced']}")

    print("\n5. Track Progress Over Time")
    print("-" * 80)

    # Example: Track improvements across design phases
    measurements = [
        {
            "date": "2026-01-01",
            "actual_carbon": 650000,  # Initial design: 650,000 kgCO2e
            "energy_reduction": 25,
            "water_reduction": 18
        },
        {
            "date": "2026-02-01",
            "actual_carbon": 600000,  # Optimized: 600,000 kgCO2e
            "energy_reduction": 30,
            "water_reduction": 22
        },
        {
            "date": "2026-03-01",
            "actual_carbon": 560000,  # Final design: 560,000 kgCO2e
            "energy_reduction": 35,
            "water_reduction": 25
        }
    ]

    progress = edge.track_progress(baseline, measurements)

    print(f"Trend: {progress['trend']}")
    print("\nProgress Timeline:")
    for entry in progress['progress_timeline']:
        print(f"  {entry['date']}: {entry['actual_carbon']:,.0f} kgCO2e "
              f"({entry['reduction_percentage']:.1f}% reduction) - "
              f"{'CERTIFIED' if entry['edge_certified'] else 'NOT CERTIFIED'}")


def main():
    """Run all examples."""
    try:
        # Run TREES certification example
        example_trees_certification()

        # Run EDGE certification example
        example_edge_certification()

        print("\n" + "=" * 80)
        print("EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure GraphDB is running at http://localhost:7200")
        print("and the carbonbim-thailand repository exists with TGO data loaded.")


if __name__ == "__main__":
    main()

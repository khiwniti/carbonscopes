"""
Example Usage of LCA Carbon Calculator.

This script demonstrates how to use the carbon calculator for various scenarios:
1. Single material calculation
2. Project carbon footprint
3. EDGE certification assessment
4. Thai language material matching

Run with:
    python carbonscope/backend/lca/example_usage.py
"""

import logging
from decimal import Decimal

from carbonscope.backend.core.knowledge_graph import GraphDBClient
from carbonscope.backend.lca import CarbonCalculator, UnitConverter, MaterialMatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_single_material():
    """Example 1: Calculate carbon for a single material."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Material Calculation")
    print("="*80)

    # Initialize GraphDB client
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    calculator = CarbonCalculator(client)

    # Calculate carbon for concrete
    carbon = calculator.calculate_material_carbon(
        material_name="Ready-mix Concrete C30",
        quantity=150.5,
        unit="m³",
        category="Concrete"
    )

    print(f"\nMaterial: Ready-mix Concrete C30")
    print(f"Quantity: 150.5 m³")
    print(f"Carbon Emissions: {carbon:,.2f} kgCO2e")
    print(f"Carbon Emissions: {float(carbon)/1000:,.2f} tCO2e")


def example_2_unit_conversion():
    """Example 2: Unit conversion capabilities."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Unit Conversion")
    print("="*80)

    converter = UnitConverter()

    # Volume conversions
    print("\nVolume Conversions:")
    m3_to_liters = converter.convert(1, "m³", "liters")
    print(f"  1 m³ = {m3_to_liters} liters")

    # Mass conversions
    print("\nMass Conversions:")
    ton_to_kg = converter.convert(2.5, "ton", "kg")
    print(f"  2.5 tons = {ton_to_kg} kg")

    # Volume to mass (density-based)
    print("\nDensity-based Conversions:")
    concrete_kg = converter.convert_volume_to_mass(10, "m³", "Concrete", "kg")
    print(f"  10 m³ concrete = {concrete_kg} kg (density: 2400 kg/m³)")

    steel_kg = converter.convert_volume_to_mass(1, "m³", "Steel", "kg")
    print(f"  1 m³ steel = {steel_kg} kg (density: 7850 kg/m³)")


def example_3_project_calculation():
    """Example 3: Full project carbon calculation."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Project Carbon Calculation")
    print("="*80)

    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    calculator = CarbonCalculator(client)

    # Define Bill of Quantities (BOQ)
    boq = [
        {
            "material_name": "Ready-mix Concrete C30",
            "quantity": 150.5,
            "unit": "m³",
            "category": "Concrete"
        },
        {
            "material_name": "Steel Rebar SD40",
            "quantity": 12.3,
            "unit": "ton",
            "category": "Steel"
        },
        {
            "material_name": "Glass Panel",
            "quantity": 500,
            "unit": "m²",
            "category": "Glass"
        },
        {
            "material_name": "Aluminum Window Frame",
            "quantity": 2.5,
            "unit": "ton",
            "category": "Aluminum"
        }
    ]

    # Calculate project carbon
    result = calculator.calculate_project_carbon(boq)

    print(f"\nProject ID: {result['project_id']}")
    print(f"Calculation Date: {result['calculation_date']}")
    print(f"\nTotal Carbon: {result['total_carbon_kgco2e']:,.2f} kgCO2e")
    print(f"Total Carbon: {result['total_carbon_tonco2e']:,.2f} tCO2e")

    print("\nBreakdown by Category:")
    for category, data in result['breakdown_by_category'].items():
        print(f"  {category}:")
        print(f"    Carbon: {data['carbon']:,.2f} kgCO2e")
        print(f"    Percentage: {data['percentage']:.1f}%")

    print("\nData Quality:")
    quality = result['data_quality']
    print(f"  Matched materials: {quality['matched_materials']}")
    print(f"  Unmatched materials: {quality['unmatched_materials']}")
    print(f"  Confidence score: {quality['confidence_score']:.2%}")


def example_4_edge_certification():
    """Example 4: EDGE certification assessment."""
    print("\n" + "="*80)
    print("EXAMPLE 4: EDGE Certification Assessment")
    print("="*80)

    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    calculator = CarbonCalculator(client)

    # Project using low-carbon materials
    project_boq = [
        {
            "material_name": "Concrete C30 with 30% Fly Ash",
            "quantity": 1200,
            "unit": "m³",
            "category": "Concrete"
        },
        {
            "material_name": "Steel Rebar 50% Recycled",
            "quantity": 150,
            "unit": "ton",
            "category": "Steel"
        }
    ]

    # Generate comprehensive report
    report = calculator.generate_carbon_report(
        boq_data=project_boq,
        project_area=5000,  # 5000 m²
        language="en"
    )

    print(f"\nProject Area: {report['project_area_m2']:,.0f} m²")
    print(f"Carbon Intensity: {report['carbon_intensity_kgco2e_per_m2']:,.2f} kgCO2e/m²")

    print("\nProject Carbon:")
    print(f"  Total: {report['project_carbon']['total_tonco2e']:,.2f} tCO2e")

    print("\nBaseline Carbon:")
    print(f"  Total: {report['baseline_carbon']['total_tonco2e']:,.2f} tCO2e")

    print("\nCarbon Savings:")
    savings = report['carbon_savings']
    print(f"  Absolute: {savings['absolute_savings_tonco2e']:,.2f} tCO2e")
    print(f"  Percentage: {savings['percentage_reduction']:.1f}%")
    print(f"  Per m²: {savings['savings_per_sqm']:,.2f} kgCO2e/m²")

    print("\nEDGE Certification:")
    edge = report['edge_certification']
    print(f"  Level: {edge['level']}")
    print(f"  Compliant: {'✓ YES' if edge['compliant'] else '✗ NO'}")
    print(f"  Reduction: {edge['reduction_percentage']:.1f}%")
    print(f"  Required for Certified: ≥{edge['required_for_certified']:.0f}%")
    print(f"  Required for Advanced: ≥{edge['required_for_advanced']:.0f}%")


def example_5_thai_language():
    """Example 5: Thai language material matching."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Thai Language Material Matching")
    print("="*80)

    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    calculator = CarbonCalculator(client)
    matcher = MaterialMatcher(client)

    # BOQ with Thai material names
    boq_thai = [
        {
            "material_name": "คอนกรีตผสมเสร็จ C30",
            "quantity": 100,
            "unit": "m³",
            "category": "Concrete"
        },
        {
            "material_name": "เหล็กเสริมคอนกรีต SD40",
            "quantity": 10,
            "unit": "ตัน",
            "category": "Steel"
        }
    ]

    # Match Thai materials
    print("\nMaterial Matching (Thai):")
    for entry in boq_thai:
        matches = matcher.find_material(
            entry['material_name'],
            language="th",
            category=entry['category']
        )

        if matches:
            best_match = matches[0]
            print(f"\n  Query: {entry['material_name']}")
            print(f"  Match: {best_match['label']}")
            print(f"  Confidence: {best_match['confidence']:.2%}")
            print(f"  Emission Factor: {best_match['emission_factor']} {best_match['unit']}")

    # Calculate project carbon
    result = calculator.calculate_project_carbon(boq_thai, language="th")
    print(f"\nTotal Project Carbon: {result['total_carbon_tonco2e']:,.2f} tCO2e")


def example_6_material_alternatives():
    """Example 6: Finding material alternatives."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Material Alternatives")
    print("="*80)

    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    matcher = MaterialMatcher(client)

    # Search for concrete alternatives
    query = "Concrete"
    alternatives = matcher.get_alternatives(
        query,
        category="Concrete",
        limit=5
    )

    print(f"\nAlternatives for '{query}':")
    for i, alt in enumerate(alternatives, 1):
        print(f"\n{i}. {alt['label']}")
        print(f"   Confidence: {alt['confidence']:.2%}")
        print(f"   Emission Factor: {alt['emission_factor']} {alt['unit']}")
        print(f"   Category: {alt['category']}")


def example_7_comparison_scenarios():
    """Example 7: Compare different material scenarios."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Material Scenario Comparison")
    print("="*80)

    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    calculator = CarbonCalculator(client)

    # Scenario 1: Conventional materials
    scenario_conventional = [
        {"material_name": "Concrete C30 Portland", "quantity": 1000, "unit": "m³", "category": "Concrete"},
        {"material_name": "Steel Rebar Virgin", "quantity": 100, "unit": "ton", "category": "Steel"}
    ]

    # Scenario 2: Low-carbon materials
    scenario_lowcarbon = [
        {"material_name": "Concrete C30 with Fly Ash", "quantity": 1000, "unit": "m³", "category": "Concrete"},
        {"material_name": "Steel Rebar Recycled", "quantity": 100, "unit": "ton", "category": "Steel"}
    ]

    print("\nScenario 1: Conventional Materials")
    result_conv = calculator.calculate_project_carbon(scenario_conventional)
    print(f"  Total Carbon: {result_conv['total_carbon_tonco2e']:,.2f} tCO2e")

    print("\nScenario 2: Low-Carbon Materials")
    result_low = calculator.calculate_project_carbon(scenario_lowcarbon)
    print(f"  Total Carbon: {result_low['total_carbon_tonco2e']:,.2f} tCO2e")

    # Calculate savings
    savings = calculator.calculate_carbon_savings(
        result_low['total_carbon_kgco2e'],
        result_conv['total_carbon_kgco2e']
    )

    print("\nComparison:")
    print(f"  Absolute Savings: {savings['absolute_savings_tonco2e']:,.2f} tCO2e")
    print(f"  Percentage Reduction: {savings['percentage_reduction']:.1f}%")
    print(f"  EDGE Level: {savings['edge_level']}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("LCA CARBON CALCULATOR - EXAMPLE USAGE")
    print("="*80)

    try:
        # Check GraphDB connection
        print("\nChecking GraphDB connection...")
        client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
        client.test_connection()
        triple_count = client.get_triple_count()
        print(f"✓ GraphDB connected! Triples: {triple_count:,}")

        # Run examples
        example_1_single_material()
        example_2_unit_conversion()
        example_3_project_calculation()
        example_4_edge_certification()
        example_5_thai_language()
        example_6_material_alternatives()
        example_7_comparison_scenarios()

        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80 + "\n")

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure GraphDB is running on http://localhost:7200")
        print("2. Verify TGO data is loaded in 'carbonbim-thailand' repository")
        print("3. Check network connectivity")


if __name__ == "__main__":
    main()

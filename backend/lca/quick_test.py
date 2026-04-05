"""
Quick Test Script for LCA Calculator.

This script performs a quick validation of the calculator without requiring
a live GraphDB connection. It tests core functionality using mocked data.

Run with: python suna/backend/lca/quick_test.py
"""

from decimal import Decimal
from suna.backend.lca import UnitConverter, CarbonCalculationError

def test_unit_converter():
    """Test unit converter functionality."""
    print("="*80)
    print("TESTING UNIT CONVERTER")
    print("="*80)

    converter = UnitConverter()

    # Test 1: Volume conversion
    result = converter.convert(1, "m³", "liters")
    assert result == Decimal("1000"), f"Expected 1000, got {result}"
    print("✓ Volume conversion: 1 m³ = 1000 liters")

    # Test 2: Mass conversion
    result = converter.convert(2, "ton", "kg")
    assert result == Decimal("2000"), f"Expected 2000, got {result}"
    print("✓ Mass conversion: 2 tons = 2000 kg")

    # Test 3: Density-based conversion (concrete)
    result = converter.convert_volume_to_mass(1, "m³", "Concrete", "kg")
    assert result == Decimal("2400"), f"Expected 2400, got {result}"
    print("✓ Density conversion: 1 m³ concrete = 2400 kg")

    # Test 4: Density-based conversion (steel)
    result = converter.convert_volume_to_mass(1, "m³", "Steel", "kg")
    assert result == Decimal("7850"), f"Expected 7850, got {result}"
    print("✓ Density conversion: 1 m³ steel = 7850 kg")

    # Test 5: Area conversion
    result = converter.convert(1, "m²", "cm²")
    assert result == Decimal("10000"), f"Expected 10000, got {result}"
    print("✓ Area conversion: 1 m² = 10000 cm²")

    print("\n✅ All unit converter tests passed!")

def test_calculator_logic():
    """Test calculator logic (without GraphDB)."""
    print("\n" + "="*80)
    print("TESTING CALCULATOR LOGIC")
    print("="*80)

    # Test EDGE certification levels
    from suna.backend.lca.carbon_calculator import CarbonCalculator
    from unittest.mock import Mock

    mock_client = Mock()
    calculator = CarbonCalculator(mock_client)

    # Test 1: EDGE Certified (20% reduction)
    savings = calculator.calculate_carbon_savings(2000000, 2500000)
    assert savings['percentage_reduction'] == 20.0
    assert savings['edge_level'] == "EDGE Certified"
    assert savings['edge_compliant'] is True
    print("✓ EDGE Certified: 20% reduction detected")

    # Test 2: EDGE Advanced (40% reduction)
    savings = calculator.calculate_carbon_savings(1500000, 2500000)
    assert savings['percentage_reduction'] == 40.0
    assert savings['edge_level'] == "EDGE Advanced"
    print("✓ EDGE Advanced: 40% reduction detected")

    # Test 3: Zero Carbon (100% reduction)
    savings = calculator.calculate_carbon_savings(0, 2500000)
    assert savings['percentage_reduction'] == 100.0
    assert savings['edge_level'] == "Zero Carbon"
    print("✓ Zero Carbon: 100% reduction detected")

    # Test 4: Not Certified (15% reduction)
    savings = calculator.calculate_carbon_savings(2125000, 2500000)
    assert savings['percentage_reduction'] == 15.0
    assert savings['edge_level'] == "Not Certified"
    assert savings['edge_compliant'] is False
    print("✓ Not Certified: 15% reduction detected")

    # Test 5: Carbon intensity
    intensity = calculator.calculate_carbon_intensity(1900000, 5000, "m²")
    assert intensity == Decimal("380")
    print("✓ Carbon intensity: 1,900,000 kgCO2e / 5,000 m² = 380 kgCO2e/m²")

    # Test 6: Baseline calculation
    project_data = [
        {'quantity': 100, 'category': 'Concrete'},
        {'quantity': 10, 'category': 'Steel'}
    ]
    baseline_factors = {
        'Concrete': 445.6,
        'Steel': 3000.0
    }
    baseline = calculator.calculate_baseline_carbon(project_data, baseline_factors)
    expected = Decimal('74560')  # (100 * 445.6) + (10 * 3000)
    assert baseline == expected
    print(f"✓ Baseline calculation: {baseline} kgCO2e")

    print("\n✅ All calculator logic tests passed!")

def main():
    """Run all quick tests."""
    print("\n" + "="*80)
    print("LCA CALCULATOR - QUICK VALIDATION TEST")
    print("="*80 + "\n")

    try:
        test_unit_converter()
        test_calculator_logic()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - LCA CALCULATOR IS WORKING CORRECTLY")
        print("="*80 + "\n")

        print("Next Steps:")
        print("1. Run full test suite: pytest suna/backend/lca/tests/test_carbon_calculator.py -v")
        print("2. Test with GraphDB: python suna/backend/lca/example_usage.py")
        print("3. Review documentation: suna/backend/lca/README_CALCULATOR.md")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

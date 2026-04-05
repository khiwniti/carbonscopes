"""
Test Suite for Carbon Calculator.

Tests cover:
- Single material calculations
- Multi-material project calculations
- Unit conversion accuracy
- Material matching (exact and fuzzy)
- EDGE certification level determination
- Error handling

Run with: pytest suna/backend/lca/tests/test_carbon_calculator.py -v
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch

from suna.backend.lca.carbon_calculator import CarbonCalculator, CarbonCalculationError
from suna.backend.lca.unit_converter import UnitConverter, UnitConversionError
from suna.backend.lca.material_matcher import MaterialMatcher, MaterialMatchError


class TestUnitConverter:
    """Test unit conversion functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.converter = UnitConverter()

    def test_volume_conversion_m3_to_liters(self):
        """Test volume conversion: m³ to liters."""
        result = self.converter.convert(1, "m³", "liters")
        assert result == Decimal("1000")

    def test_mass_conversion_ton_to_kg(self):
        """Test mass conversion: ton to kg."""
        result = self.converter.convert(2, "ton", "kg")
        assert result == Decimal("2000")

    def test_area_conversion_m2_to_cm2(self):
        """Test area conversion: m² to cm²."""
        result = self.converter.convert(1, "m²", "cm²")
        assert result == Decimal("10000")

    def test_length_conversion_m_to_cm(self):
        """Test length conversion: m to cm."""
        result = self.converter.convert(5, "m", "cm")
        assert result == Decimal("500")

    def test_volume_to_mass_concrete(self):
        """Test volume to mass conversion for concrete."""
        # 1 m³ of concrete = 2400 kg
        result = self.converter.convert_volume_to_mass(1, "m³", "Concrete", "kg")
        assert result == Decimal("2400")

    def test_volume_to_mass_steel(self):
        """Test volume to mass conversion for steel."""
        # 1 m³ of steel = 7850 kg
        result = self.converter.convert_volume_to_mass(1, "m³", "Steel", "kg")
        assert result == Decimal("7850")

    def test_mass_to_volume_concrete(self):
        """Test mass to volume conversion for concrete."""
        # 2400 kg of concrete = 1 m³
        result = self.converter.convert_mass_to_volume(2400, "kg", "Concrete", "m³")
        assert result == Decimal("1")

    def test_same_unit_no_conversion(self):
        """Test that same unit returns original value."""
        result = self.converter.convert(100, "kg", "kg")
        assert result == Decimal("100")

    def test_unknown_material_density(self):
        """Test error handling for unknown material."""
        with pytest.raises(UnitConversionError):
            self.converter.convert_volume_to_mass(1, "m³", "UnknownMaterial", "kg")

    def test_normalize_unit_volume(self):
        """Test unit normalization for volume."""
        normalized, base_unit = self.converter.normalize_unit(1000, "liters")
        assert normalized == Decimal("1")
        assert base_unit == "m³"

    def test_normalize_unit_mass(self):
        """Test unit normalization for mass."""
        normalized, base_unit = self.converter.normalize_unit(2, "ton")
        assert normalized == Decimal("2000")
        assert base_unit == "kg"

    def test_get_unit_type(self):
        """Test unit type detection."""
        assert self.converter.get_unit_type("m³") == "volume"
        assert self.converter.get_unit_type("kg") == "mass"
        assert self.converter.get_unit_type("m²") == "area"
        assert self.converter.get_unit_type("m") == "length"

    def test_add_custom_material_density(self):
        """Test adding custom material density."""
        self.converter.add_material_density("CustomMaterial", 1500.0)
        density = self.converter.get_material_density("CustomMaterial")
        assert density == Decimal("1500.0")


class TestMaterialMatcher:
    """Test material name matching functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_client = Mock()
        self.matcher = MaterialMatcher(self.mock_client, min_confidence=0.6)

    @patch('suna.backend.lca.material_matcher.search_materials')
    def test_exact_match(self, mock_search):
        """Test exact material name matching."""
        mock_search.return_value = [
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'label': 'Concrete C30',
                'category': 'Concrete',
                'emission_factor': Decimal('445.6'),
                'unit': 'kgCO2e/m³',
                'effective_date': '2026-01-01'
            }
        ]

        results = self.matcher.find_material("Concrete C30", language="en")

        assert len(results) > 0
        assert results[0]['material_id'] == 'http://tgo.or.th/materials/concrete-c30'
        assert results[0]['confidence'] == 1.0  # Exact match

    @patch('suna.backend.lca.material_matcher.search_materials')
    def test_fuzzy_match(self, mock_search):
        """Test fuzzy material name matching."""
        mock_search.return_value = [
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'label': 'Ready-mixed Concrete C30',
                'category': 'Concrete',
                'emission_factor': Decimal('445.6'),
                'unit': 'kgCO2e/m³',
                'effective_date': '2026-01-01'
            }
        ]

        results = self.matcher.find_material("Concrete C30", language="en")

        assert len(results) > 0
        assert results[0]['confidence'] > 0.6  # Should match with good confidence

    @patch('suna.backend.lca.material_matcher.search_materials')
    def test_no_match_below_confidence(self, mock_search):
        """Test that low confidence matches are filtered out."""
        mock_search.return_value = [
            {
                'material_id': 'http://tgo.or.th/materials/steel',
                'label': 'Steel Rebar',  # Very different from query
                'category': 'Steel',
                'emission_factor': Decimal('3000'),
                'unit': 'kgCO2e/ton',
                'effective_date': '2026-01-01'
            }
        ]

        results = self.matcher.find_material("Glass Panel", language="en")

        # Should filter out low confidence matches
        assert all(r['confidence'] >= 0.6 for r in results)

    @patch('suna.backend.lca.material_matcher.search_materials')
    def test_match_material_best_match(self, mock_search):
        """Test getting best match only."""
        mock_search.return_value = [
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'label': 'Concrete C30',
                'category': 'Concrete',
                'emission_factor': Decimal('445.6'),
                'unit': 'kgCO2e/m³',
                'effective_date': '2026-01-01'
            },
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c25',
                'label': 'Concrete C25',
                'category': 'Concrete',
                'emission_factor': Decimal('420.0'),
                'unit': 'kgCO2e/m³',
                'effective_date': '2026-01-01'
            }
        ]

        match = self.matcher.match_material("Concrete C30", language="en")

        assert match is not None
        assert match['label'] == 'Concrete C30'  # Best match

    def test_normalize_string(self):
        """Test string normalization for matching."""
        normalized = self.matcher._normalize_string("  Concrete  C30,  Ready-Mix  ")
        assert normalized == "concrete c30 ready mix"

    def test_calculate_confidence_exact(self):
        """Test confidence calculation for exact match."""
        confidence = self.matcher._calculate_confidence("Concrete C30", "Concrete C30")
        assert confidence == 1.0

    def test_calculate_confidence_substring(self):
        """Test confidence calculation for substring match."""
        confidence = self.matcher._calculate_confidence("C30", "Concrete C30")
        assert confidence == 0.95  # Substring match

    def test_cache_functionality(self):
        """Test that results are cached."""
        with patch('suna.backend.lca.material_matcher.search_materials') as mock_search:
            mock_search.return_value = [
                {
                    'material_id': 'http://tgo.or.th/materials/test',
                    'label': 'Test Material',
                    'category': 'Test',
                    'emission_factor': Decimal('100'),
                    'unit': 'kgCO2e/unit',
                    'effective_date': '2026-01-01'
                }
            ]

            # First call - should hit GraphDB
            result1 = self.matcher.find_material("Test", language="en")
            first_count = mock_search.call_count

            # Second call with same parameters - should use cache
            result2 = self.matcher.find_material("Test", language="en")
            second_count = mock_search.call_count

            # Should not make additional calls (cache hit)
            assert second_count == first_count
            assert result1 == result2  # Same results

    def test_clear_cache(self):
        """Test cache clearing."""
        with patch('suna.backend.lca.material_matcher.search_materials') as mock_search:
            mock_search.return_value = []

            self.matcher.find_material("Test", language="en")
            self.matcher.clear_cache()
            self.matcher.find_material("Test", language="en")

            assert mock_search.call_count == 2  # Cache was cleared


class TestCarbonCalculator:
    """Test carbon calculator functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_client = Mock()
        self.calculator = CarbonCalculator(self.mock_client, min_match_confidence=0.7)

    @patch('suna.backend.lca.carbon_calculator.get_emission_factor')
    def test_calculate_material_carbon_simple(self, mock_get_ef):
        """Test simple material carbon calculation."""
        mock_get_ef.return_value = {
            'material_id': 'http://tgo.or.th/materials/concrete-c30',
            'emission_factor': Decimal('445.6'),
            'unit': 'kgCO2e/m³',
            'label_en': 'Concrete C30',
            'category': 'Concrete'
        }

        carbon = self.calculator.calculate_material_carbon(
            material_name="Concrete C30",
            quantity=100,
            unit="m³",
            material_id='http://tgo.or.th/materials/concrete-c30'
        )

        # 100 m³ × 445.6 kgCO2e/m³ = 44560 kgCO2e
        assert carbon == Decimal('44560')

    @patch('suna.backend.lca.carbon_calculator.get_emission_factor')
    def test_calculate_material_carbon_with_unit_conversion(self, mock_get_ef):
        """Test material carbon calculation with unit conversion."""
        mock_get_ef.return_value = {
            'material_id': 'http://tgo.or.th/materials/steel-rebar',
            'emission_factor': Decimal('3000'),
            'unit': 'kgCO2e/ton',
            'label_en': 'Steel Rebar',
            'category': 'Steel'
        }

        carbon = self.calculator.calculate_material_carbon(
            material_name="Steel Rebar",
            quantity=2000,  # 2000 kg = 2 ton
            unit="kg",
            material_id='http://tgo.or.th/materials/steel-rebar',
            category='Steel'
        )

        # 2 ton × 3000 kgCO2e/ton = 6000 kgCO2e
        assert carbon == Decimal('6000')

    def test_calculate_baseline_carbon(self):
        """Test baseline carbon calculation."""
        project_data = [
            {'quantity': 100, 'category': 'Concrete'},
            {'quantity': 10, 'category': 'Steel'}
        ]

        baseline_factors = {
            'Concrete': 445.6,  # kgCO2e/m³
            'Steel': 3000.0     # kgCO2e/ton
        }

        baseline = self.calculator.calculate_baseline_carbon(
            project_data,
            baseline_factors=baseline_factors
        )

        # (100 × 445.6) + (10 × 3000) = 44560 + 30000 = 74560
        assert baseline == Decimal('74560')

    def test_calculate_carbon_savings_edge_certified(self):
        """Test carbon savings calculation for EDGE Certified level."""
        savings = self.calculator.calculate_carbon_savings(
            project_carbon=2000000,  # 2,000 ton
            baseline_carbon=2500000  # 2,500 ton
        )

        # (2,500,000 - 2,000,000) / 2,500,000 = 20%
        assert savings['percentage_reduction'] == 20.0
        assert savings['edge_level'] == "EDGE Certified"
        assert savings['edge_compliant'] is True

    def test_calculate_carbon_savings_edge_advanced(self):
        """Test carbon savings calculation for EDGE Advanced level."""
        savings = self.calculator.calculate_carbon_savings(
            project_carbon=1500000,  # 1,500 ton
            baseline_carbon=2500000  # 2,500 ton
        )

        # (2,500,000 - 1,500,000) / 2,500,000 = 40%
        assert savings['percentage_reduction'] == 40.0
        assert savings['edge_level'] == "EDGE Advanced"
        assert savings['edge_compliant'] is True

    def test_calculate_carbon_savings_zero_carbon(self):
        """Test carbon savings calculation for Zero Carbon level."""
        savings = self.calculator.calculate_carbon_savings(
            project_carbon=0,  # Net zero
            baseline_carbon=2500000
        )

        # (2,500,000 - 0) / 2,500,000 = 100%
        assert savings['percentage_reduction'] == 100.0
        assert savings['edge_level'] == "Zero Carbon"
        assert savings['edge_compliant'] is True

    def test_calculate_carbon_savings_not_certified(self):
        """Test carbon savings calculation for non-certified project."""
        savings = self.calculator.calculate_carbon_savings(
            project_carbon=2100000,  # Only 16% reduction
            baseline_carbon=2500000
        )

        # (2,500,000 - 2,100,000) / 2,500,000 = 16%
        assert savings['percentage_reduction'] == 16.0
        assert savings['edge_level'] == "Not Certified"
        assert savings['edge_compliant'] is False

    def test_calculate_carbon_intensity(self):
        """Test carbon intensity calculation."""
        intensity = self.calculator.calculate_carbon_intensity(
            total_carbon=1900000,  # kgCO2e
            project_area=5000,     # m²
            area_unit="m²"
        )

        # 1,900,000 / 5,000 = 380 kgCO2e/m²
        assert intensity == Decimal('380')

    def test_extract_base_unit(self):
        """Test extraction of base unit from emission factor unit."""
        assert self.calculator._extract_base_unit("kgCO2e/m³") == "m³"
        assert self.calculator._extract_base_unit("kgCO2e/ton") == "ton"
        assert self.calculator._extract_base_unit("kgCO2e/m²") == "m²"

    @patch('suna.backend.lca.carbon_calculator.get_emission_factor')
    def test_calculate_project_carbon(self, mock_get_ef):
        """Test full project carbon calculation."""
        # Mock get_emission_factor to return appropriate values
        def get_ef_side_effect(client, material_id, **kwargs):
            if 'concrete' in material_id.lower():
                return {
                    'material_id': material_id,
                    'emission_factor': Decimal('445.6'),
                    'unit': 'kgCO2e/m³',
                    'label_en': 'Concrete C30',
                    'category': 'Concrete'
                }
            elif 'steel' in material_id.lower():
                return {
                    'material_id': material_id,
                    'emission_factor': Decimal('3000'),
                    'unit': 'kgCO2e/ton',
                    'label_en': 'Steel Rebar',
                    'category': 'Steel'
                }

        mock_get_ef.side_effect = get_ef_side_effect

        # Use material_id to avoid matching complexity
        boq = [
            {
                'material_name': 'Concrete C30',
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'quantity': 100,
                'unit': 'm³',
                'category': 'Concrete'
            },
            {
                'material_name': 'Steel Rebar',
                'material_id': 'http://tgo.or.th/materials/steel-rebar',
                'quantity': 10,
                'unit': 'ton',
                'category': 'Steel'
            }
        ]

        result = self.calculator.calculate_project_carbon(boq)

        # Total: (100 × 445.6) + (10 × 3000) = 74560 kgCO2e
        assert result['total_carbon_kgco2e'] == 74560.0
        assert result['total_carbon_tonco2e'] == 74.56
        assert result['data_quality']['matched_materials'] == 2
        assert result['data_quality']['unmatched_materials'] == 0
        assert len(result['breakdown_by_material']) == 2

    def test_error_handling_invalid_baseline(self):
        """Test error handling for invalid baseline."""
        with pytest.raises(CarbonCalculationError):
            self.calculator.calculate_carbon_savings(1000000, 0)

    def test_error_handling_invalid_area(self):
        """Test error handling for invalid area."""
        with pytest.raises(CarbonCalculationError):
            self.calculator.calculate_carbon_intensity(1000000, 0)


class TestIntegration:
    """Integration tests (require actual GraphDB connection)."""

    @pytest.mark.integration
    def test_full_workflow_with_graphdb(self):
        """
        Integration test with actual GraphDB.

        Note: This test requires GraphDB to be running and populated with TGO data.
        Skip if GraphDB is not available.
        """
        pytest.skip("Integration test - requires running GraphDB instance")

        # This would be an actual integration test
        # from suna.backend.core.knowledge_graph import GraphDBClient
        # client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
        # calculator = CarbonCalculator(client)
        #
        # boq = [...]
        # result = calculator.generate_carbon_report(boq)
        # assert result['edge_certification']['compliant'] in [True, False]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

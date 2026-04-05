"""
Tests for Material Matcher with RapidFuzz integration.

Tests cover:
- RapidFuzz algorithm integration
- Thai abbreviation expansion
- Confidence classification
- Category auto-detection
- Performance benchmarks
"""

import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal

from lca.material_matcher import MaterialMatcher, MaterialMatchError
from boq.thai_text_utils import expand_thai_abbreviations, normalize_thai_text, extract_material_category_hint


class TestThaiAbbreviationExpansion:
    """Test Thai abbreviation expansion in matching."""

    def test_expand_thai_abbreviations(self):
        """Test basic abbreviation expansion."""
        assert expand_thai_abbreviations('คสล. C30') == 'คอนกรีต C30'
        assert expand_thai_abbreviations('100 ตร.ม.') == '100 ตารางเมตร'
        assert expand_thai_abbreviations('50 ลบ.ม.') == '50 ลูกบาศก์เมตร'
        assert expand_thai_abbreviations('1000 กก.') == '1000 กิโลกรัม'

    def test_expand_multiple_abbreviations(self):
        """Test multiple abbreviations in one string."""
        text = 'คสล. C30 100 ลบ.ม.'
        result = expand_thai_abbreviations(text)
        assert 'คอนกรีต' in result
        assert 'ลูกบาศก์เมตร' in result
        assert 'คสล.' not in result
        assert 'ลบ.ม.' not in result

    def test_normalize_thai_text(self):
        """Test Thai text normalization."""
        # Whitespace normalization
        assert normalize_thai_text('คอนกรีต  C30') == 'คอนกรีต c30'

        # Abbreviation expansion + normalization
        result = normalize_thai_text('คสล. C30  100  ตร.ม.')
        assert 'คอนกรีต' in result
        assert 'ตารางเมตร' in result
        assert '  ' not in result  # No double spaces


class TestCategoryDetection:
    """Test automatic category detection."""

    def test_detect_concrete_thai(self):
        """Test concrete category detection from Thai text."""
        assert extract_material_category_hint('คอนกรีตผสมเสร็จ C30') == 'concrete'
        assert extract_material_category_hint('คสล. C40') == 'concrete'

    def test_detect_steel_thai(self):
        """Test steel category detection from Thai text."""
        assert extract_material_category_hint('เหล็กเสริม SD40') == 'steel'
        assert extract_material_category_hint('เหล็กข้ออ้อย 12 มม.') == 'steel'

    def test_detect_glass(self):
        """Test glass category detection."""
        assert extract_material_category_hint('กระจกใส 6 มม.') == 'glass'
        assert extract_material_category_hint('Clear glass 6mm') == 'glass'

    def test_detect_wood(self):
        """Test wood category detection."""
        assert extract_material_category_hint('ไม้อัด 12 มม.') == 'wood'
        assert extract_material_category_hint('Plywood 12mm') == 'wood'

    def test_detect_unknown(self):
        """Test unknown category for unrecognized materials."""
        assert extract_material_category_hint('วัสดุพิเศษ XYZ') == 'unknown'


class TestConfidenceClassification:
    """Test confidence threshold classification."""

    def test_classify_auto_match(self):
        """Test high confidence classification."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        assert matcher.classify_confidence(0.95) == "auto_match"
        assert matcher.classify_confidence(0.90) == "auto_match"
        assert matcher.classify_confidence(1.0) == "auto_match"

    def test_classify_review_required(self):
        """Test medium confidence classification."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        assert matcher.classify_confidence(0.85) == "review_required"
        assert matcher.classify_confidence(0.75) == "review_required"
        assert matcher.classify_confidence(0.70) == "review_required"

    def test_classify_rejected(self):
        """Test low confidence classification."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        assert matcher.classify_confidence(0.65) == "rejected"
        assert matcher.classify_confidence(0.50) == "rejected"
        assert matcher.classify_confidence(0.0) == "rejected"

    def test_boundary_conditions(self):
        """Test confidence boundary values."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Boundary at 0.90
        assert matcher.classify_confidence(0.89999) == "review_required"
        assert matcher.classify_confidence(0.90000) == "auto_match"

        # Boundary at 0.70
        assert matcher.classify_confidence(0.69999) == "rejected"
        assert matcher.classify_confidence(0.70000) == "review_required"


class TestRapidFuzzIntegration:
    """Test RapidFuzz algorithm integration."""

    def test_token_set_ratio_word_order_independence(self):
        """Test word-order independent matching with RapidFuzz."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Test word order independence
        score1 = matcher._calculate_confidence('เหล็กเสริม SD40', 'SD40 เหล็กเสริม')
        score2 = matcher._calculate_confidence('SD40 เหล็กเสริม', 'เหล็กเสริม SD40')

        # Should have high confidence due to token_set_ratio
        assert score1 >= 0.9
        assert score2 >= 0.9
        assert abs(score1 - score2) < 0.01  # Should be very similar

    def test_exact_match(self):
        """Test exact match returns 1.0 confidence."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        score = matcher._calculate_confidence('คอนกรีต C30', 'คอนกรีต C30')
        assert score == 1.0

    def test_substring_match(self):
        """Test substring match returns 0.95 confidence."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        score = matcher._calculate_confidence('คอนกรีต', 'คอนกรีตผสมเสร็จ C30')
        assert score == 0.95

    def test_partial_match(self):
        """Test partial matching."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Similar but not identical
        score = matcher._calculate_confidence('คอนกรีต C30', 'คอนกรีต C40')
        assert 0.7 < score < 1.0

    def test_no_match(self):
        """Test completely different strings."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        score = matcher._calculate_confidence('คอนกรีต', 'เหล็กเสริม')
        assert score < 0.5


class TestMaterialMatcherWithMock:
    """Test MaterialMatcher with mocked GraphDB client."""

    def test_find_material_with_thai_abbreviation(self):
        """Test that find_material expands Thai abbreviations before searching."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Mock the search_materials function
        from core.knowledge_graph import sparql_queries
        original_search = sparql_queries.search_materials

        def mock_search(client, query, **kwargs):
            # Verify that query has abbreviations expanded
            assert 'คอนกรีต' in query or 'concrete' in query.lower()
            return [
                {
                    'material_id': 'http://tgo.or.th/materials/concrete-c30',
                    'label': 'คอนกรีต C30',
                    'emission_factor': Decimal('445.6'),
                    'unit': 'kgCO2e/m³',
                    'category': 'Concrete'
                }
            ]

        sparql_queries.search_materials = mock_search

        try:
            # Test with abbreviation
            results = matcher.find_material('คสล. C30', language='th')
            assert len(results) > 0
        finally:
            # Restore original function
            sparql_queries.search_materials = original_search

    def test_category_auto_detection(self):
        """Test automatic category detection for Thai materials."""
        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Mock search_materials
        from core.knowledge_graph import sparql_queries
        original_search = sparql_queries.search_materials

        detected_category = None

        def mock_search(client, query, category_filter=None, **kwargs):
            nonlocal detected_category
            detected_category = category_filter
            return [
                {
                    'material_id': 'http://tgo.or.th/materials/concrete-c30',
                    'label': 'คอนกรีต C30',
                    'emission_factor': Decimal('445.6'),
                    'unit': 'kgCO2e/m³',
                    'category': 'Concrete'
                }
            ]

        sparql_queries.search_materials = mock_search

        try:
            # Test with Thai concrete description
            results = matcher.find_material('คอนกรีตผสมเสร็จ C30', language='th')
            assert detected_category == 'concrete'
        finally:
            sparql_queries.search_materials = original_search


class TestPerformance:
    """Test matching performance with RapidFuzz."""

    def test_confidence_calculation_speed(self):
        """Test that confidence calculation is fast."""
        import time

        mock_client = Mock()
        matcher = MaterialMatcher(mock_client)

        # Test 100 confidence calculations
        start = time.time()
        for i in range(100):
            matcher._calculate_confidence(
                f'คอนกรีต C{i % 50}',
                f'คอนกรีตผสมเสร็จ C{i % 50}'
            )
        duration = time.time() - start

        # Should be fast with RapidFuzz (< 0.1 seconds for 100 calculations)
        assert duration < 0.1, f"Confidence calculation too slow: {duration}s for 100 calculations"

    def test_normalization_speed(self):
        """Test that text normalization is fast."""
        import time

        # Test 1000 normalizations
        start = time.time()
        for i in range(1000):
            normalize_thai_text(f'คสล. C{i % 50} {i} ตร.ม.')
        duration = time.time() - start

        # Should be very fast (< 0.1 seconds for 1000 normalizations)
        assert duration < 0.1, f"Normalization too slow: {duration}s for 1000 operations"


@pytest.mark.integration
class TestMaterialMatcherIntegration:
    """Integration tests requiring actual GraphDB connection."""

    @pytest.mark.skip(reason="Requires live GraphDB connection")
    def test_find_concrete_material(self):
        """Test finding concrete materials from actual database."""
        # This test would require actual GraphDB setup
        # Skipped for now, to be enabled when GraphDB is available
        pass

    @pytest.mark.skip(reason="Requires live GraphDB connection")
    def test_match_accuracy_on_real_data(self):
        """Test matching accuracy on real BOQ data."""
        # This test would validate ≥90% matching accuracy
        # Skipped for now, to be enabled with test data
        pass

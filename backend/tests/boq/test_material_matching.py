"""
Tests for BOQ Material Matching Integration.

Tests cover:
- Matching BOQ materials to TGO database
- Confidence scoring and classification
- Alternative material suggestions
- Match statistics calculation
- BOQMaterialMatch serialization
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from boq.models import BOQMaterial
from boq.material_matching import (
    match_boq_materials,
    calculate_match_statistics,
    BOQMaterialMatch
)


@pytest.fixture
def sample_boq_materials():
    """Sample BOQ materials for testing."""
    return [
        BOQMaterial(
            line_number=1,
            description_th="คอนกรีตผสมเสร็จ 280 กก./ตร.ม.",
            description_en="Ready-mixed concrete 280 kg/m³",
            quantity=Decimal("1000.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        ),
        BOQMaterial(
            line_number=2,
            description_th="เหล็กเสริม SD40 ขนาด 12 มม.",
            description_en="Reinforcement steel SD40 12mm",
            quantity=Decimal("5000.0"),
            unit="kg",
            unit_raw="กก.",
            conversion_factor=Decimal("1.0")
        ),
        BOQMaterial(
            line_number=3,
            description_th="กระจกใส 6 มม.",
            description_en="Clear glass 6mm",
            quantity=Decimal("100.0"),
            unit="m²",
            unit_raw="ตร.ม.",
            conversion_factor=Decimal("1.0")
        ),
    ]


@pytest.fixture
def mock_graphdb_client():
    """Mock GraphDB client."""
    return Mock()


class TestBOQMaterialMatch:
    """Test BOQMaterialMatch class."""

    def test_to_dict_with_match(self):
        """Test serialization with successful match."""
        boq_material = BOQMaterial(
            line_number=1,
            description_th="คอนกรีต C30",
            description_en="Concrete C30",
            quantity=Decimal("100.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        )

        tgo_match = {
            "material_id": "http://tgo.or.th/materials/concrete-c30",
            "label": "คอนกรีต C30",
            "emission_factor": Decimal("445.6"),
            "unit": "kgCO2e/m³"
        }

        alternatives = [
            {
                "material_id": "http://tgo.or.th/materials/concrete-c35",
                "label": "คอนกรีต C35",
                "confidence": 0.85,
                "emission_factor": Decimal("460.0")
            }
        ]

        match = BOQMaterialMatch(
            boq_material=boq_material,
            tgo_match=tgo_match,
            confidence=0.95,
            classification="auto_match",
            alternatives=alternatives
        )

        result = match.to_dict()

        # Verify structure
        assert result["boq_line_number"] == 1
        assert result["description_th"] == "คอนกรีต C30"
        assert result["quantity"] == "100.0"
        assert result["unit"] == "m³"

        # Verify TGO match
        assert result["tgo_match"]["material_id"] == "http://tgo.or.th/materials/concrete-c30"
        assert result["tgo_match"]["confidence"] == 0.95
        assert result["tgo_match"]["classification"] == "auto_match"

        # Verify alternatives (top 3)
        assert len(result["alternatives"]) == 1
        assert result["alternatives"][0]["material_id"] == "http://tgo.or.th/materials/concrete-c35"

    def test_to_dict_without_match(self):
        """Test serialization with no match found."""
        boq_material = BOQMaterial(
            line_number=5,
            description_th="วัสดุพิเศษ XYZ",
            description_en="Special material XYZ",
            quantity=Decimal("50.0"),
            unit="unit",
            unit_raw="ชิ้น",
            conversion_factor=Decimal("1.0")
        )

        match = BOQMaterialMatch(
            boq_material=boq_material,
            tgo_match=None,
            confidence=0.0,
            classification="rejected",
            alternatives=[]
        )

        result = match.to_dict()

        # Verify no match
        assert result["tgo_match"]["material_id"] is None
        assert result["tgo_match"]["confidence"] == 0.0
        assert result["tgo_match"]["classification"] == "rejected"
        assert len(result["alternatives"]) == 0

    def test_alternatives_limited_to_top_3(self):
        """Test that only top 3 alternatives are included."""
        boq_material = BOQMaterial(
            line_number=1,
            description_th="คอนกรีต",
            description_en="Concrete",
            quantity=Decimal("100.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        )

        # Create 5 alternatives
        alternatives = [
            {"material_id": f"mat-{i}", "label": f"Material {i}", "confidence": 0.8 - i*0.05, "emission_factor": Decimal("400.0")}
            for i in range(5)
        ]

        match = BOQMaterialMatch(
            boq_material=boq_material,
            tgo_match={"material_id": "mat-0", "label": "Material 0", "emission_factor": Decimal("445.6")},
            confidence=0.95,
            classification="auto_match",
            alternatives=alternatives
        )

        result = match.to_dict()

        # Should only have top 3 alternatives
        assert len(result["alternatives"]) == 3
        assert result["alternatives"][0]["material_id"] == "mat-0"
        assert result["alternatives"][2]["material_id"] == "mat-2"


class TestMatchBOQMaterials:
    """Test match_boq_materials function."""

    @patch('suna.backend.lca.material_matcher.MaterialMatcher')
    @patch('suna.backend.boq.material_matching._ensure_matcher_imported')
    def test_match_materials_success(self, mock_ensure_import, mock_matcher_class, sample_boq_materials, mock_graphdb_client):
        """Test successful material matching."""
        # Setup mock matcher
        mock_matcher = Mock()
        mock_matcher_class.return_value = mock_matcher

        # Mock the global import
        import boq.material_matching as mm_module
        mm_module.MaterialMatcher = mock_matcher_class

        # Mock find_material to return matches
        def mock_find_material(description, language=None, category=None):
            if 'คอนกรีต' in description:
                return [
                    {
                        'material_id': 'http://tgo.or.th/materials/concrete-c30',
                        'label': 'คอนกรีต C30',
                        'confidence': 0.95,
                        'emission_factor': Decimal('445.6'),
                        'unit': 'kgCO2e/m³'
                    }
                ]
            elif 'เหล็ก' in description:
                return [
                    {
                        'material_id': 'http://tgo.or.th/materials/steel-sd40',
                        'label': 'เหล็กเสริม SD40',
                        'confidence': 0.92,
                        'emission_factor': Decimal('2100.0'),
                        'unit': 'kgCO2e/kg'
                    }
                ]
            return []

        mock_matcher.find_material.side_effect = mock_find_material

        # Mock classify_confidence
        def mock_classify(confidence):
            if confidence >= 0.90:
                return "auto_match"
            elif confidence >= 0.70:
                return "review_required"
            return "rejected"

        mock_matcher.classify_confidence.side_effect = mock_classify

        # Test matching
        matches = match_boq_materials(sample_boq_materials, mock_graphdb_client, language="th")

        # Verify results
        assert len(matches) == 3
        assert all(isinstance(m, BOQMaterialMatch) for m in matches)

        # Check concrete match
        concrete_match = matches[0]
        assert concrete_match.classification == "auto_match"
        assert concrete_match.confidence == 0.95

        # Check steel match
        steel_match = matches[1]
        assert steel_match.classification == "auto_match"
        assert steel_match.confidence == 0.92

    @patch('suna.backend.lca.material_matcher.MaterialMatcher')
    @patch('suna.backend.boq.material_matching._ensure_matcher_imported')
    def test_match_materials_no_results(self, mock_ensure_import, mock_matcher_class, mock_graphdb_client):
        """Test matching when no results found."""
        mock_matcher = Mock()
        mock_matcher_class.return_value = mock_matcher
        mock_matcher.find_material.return_value = []

        # Mock the global import
        import boq.material_matching as mm_module
        mm_module.MaterialMatcher = mock_matcher_class

        boq_materials = [
            BOQMaterial(
                line_number=1,
                description_th="วัสดุพิเศษ Unknown",
                description_en=None,
                quantity=Decimal("10.0"),
                unit="unit",
                unit_raw="ชิ้น",
                conversion_factor=Decimal("1.0")
            )
        ]

        matches = match_boq_materials(boq_materials, mock_graphdb_client)

        assert len(matches) == 1
        assert matches[0].tgo_match is None
        assert matches[0].confidence == 0.0
        assert matches[0].classification == "rejected"

    @patch('suna.backend.lca.material_matcher.MaterialMatcher')
    @patch('suna.backend.boq.material_matching._ensure_matcher_imported')
    def test_match_materials_with_alternatives(self, mock_ensure_import, mock_matcher_class, sample_boq_materials, mock_graphdb_client):
        """Test that alternatives are captured."""
        mock_matcher = Mock()
        mock_matcher_class.return_value = mock_matcher

        # Mock the global import
        import boq.material_matching as mm_module
        mm_module.MaterialMatcher = mock_matcher_class

        # Mock find_material to return multiple matches
        mock_matcher.find_material.return_value = [
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c30',
                'label': 'คอนกรีต C30',
                'confidence': 0.95,
                'emission_factor': Decimal('445.6'),
                'unit': 'kgCO2e/m³'
            },
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c35',
                'label': 'คอนกรีต C35',
                'confidence': 0.85,
                'emission_factor': Decimal('460.0'),
                'unit': 'kgCO2e/m³'
            },
            {
                'material_id': 'http://tgo.or.th/materials/concrete-c40',
                'label': 'คอนกรีต C40',
                'confidence': 0.80,
                'emission_factor': Decimal('475.0'),
                'unit': 'kgCO2e/m³'
            }
        ]

        mock_matcher.classify_confidence.return_value = "auto_match"

        matches = match_boq_materials([sample_boq_materials[0]], mock_graphdb_client)

        # Verify alternatives are captured (top 3)
        assert len(matches[0].alternatives) == 2  # Best match + 2 alternatives = 3 total
        assert matches[0].alternatives[0]['material_id'] == 'http://tgo.or.th/materials/concrete-c35'


class TestCalculateMatchStatistics:
    """Test calculate_match_statistics function."""

    def test_statistics_calculation(self):
        """Test match statistics calculation."""
        # Create sample matches
        boq_material = BOQMaterial(
            line_number=1,
            description_th="Test",
            description_en="Test",
            quantity=Decimal("100.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        )

        matches = [
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match={"material_id": "test1", "label": "Test1", "emission_factor": Decimal("100.0")},
                confidence=0.95,
                classification="auto_match"
            ),
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match={"material_id": "test2", "label": "Test2", "emission_factor": Decimal("100.0")},
                confidence=0.85,
                classification="review_required"
            ),
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match={"material_id": "test3", "label": "Test3", "emission_factor": Decimal("100.0")},
                confidence=0.75,
                classification="review_required"
            ),
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match=None,
                confidence=0.0,
                classification="rejected"
            ),
        ]

        stats = calculate_match_statistics(matches)

        # Verify statistics
        assert stats["total_materials"] == 4
        assert stats["auto_matched"] == 1
        assert stats["review_required"] == 2
        assert stats["rejected"] == 1
        assert stats["auto_match_rate"] == 25.0  # 1/4 = 25%
        assert stats["success_rate"] == 75.0  # (1+2)/4 = 75%

    def test_statistics_empty_list(self):
        """Test statistics with empty match list."""
        stats = calculate_match_statistics([])

        assert stats["total_materials"] == 0
        assert stats["auto_matched"] == 0
        assert stats["review_required"] == 0
        assert stats["rejected"] == 0
        assert stats["auto_match_rate"] == 0
        assert stats["success_rate"] == 0

    def test_statistics_all_auto_matched(self):
        """Test statistics when all materials auto-matched."""
        boq_material = BOQMaterial(
            line_number=1,
            description_th="Test",
            description_en="Test",
            quantity=Decimal("100.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        )

        matches = [
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match={"material_id": f"test{i}", "label": f"Test{i}", "emission_factor": Decimal("100.0")},
                confidence=0.95,
                classification="auto_match"
            )
            for i in range(10)
        ]

        stats = calculate_match_statistics(matches)

        assert stats["total_materials"] == 10
        assert stats["auto_matched"] == 10
        assert stats["auto_match_rate"] == 100.0
        assert stats["success_rate"] == 100.0

    def test_statistics_all_rejected(self):
        """Test statistics when all materials rejected."""
        boq_material = BOQMaterial(
            line_number=1,
            description_th="Test",
            description_en="Test",
            quantity=Decimal("100.0"),
            unit="m³",
            unit_raw="ลบ.ม.",
            conversion_factor=Decimal("1.0")
        )

        matches = [
            BOQMaterialMatch(
                boq_material=boq_material,
                tgo_match=None,
                confidence=0.0,
                classification="rejected"
            )
            for _ in range(5)
        ]

        stats = calculate_match_statistics(matches)

        assert stats["total_materials"] == 5
        assert stats["rejected"] == 5
        assert stats["auto_match_rate"] == 0.0
        assert stats["success_rate"] == 0.0


@pytest.mark.integration
class TestMaterialMatchingIntegration:
    """Integration tests for material matching."""

    @pytest.mark.skip(reason="Requires live GraphDB connection")
    def test_end_to_end_matching(self):
        """Test complete matching workflow with real database."""
        # This would test the full integration with GraphDB
        # Skipped for now, to be enabled when GraphDB is available
        pass

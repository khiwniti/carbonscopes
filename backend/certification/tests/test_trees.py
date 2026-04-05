"""
Unit tests for TREES NC 1.1 certification calculator.

Tests cover:
- MR credit calculations (MR1, MR3, MR4)
- Gold pathway analysis
- Platinum pathway analysis
- Gap analysis
- Edge cases and error handling
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from ..trees import TREESCertification, TREESError


@pytest.fixture
def mock_graphdb_client():
    """Create mock GraphDB client."""
    client = Mock()
    client.query = MagicMock(return_value={"results": {"bindings": []}})
    return client


@pytest.fixture
def trees_cert(mock_graphdb_client):
    """Create TREES certification instance."""
    return TREESCertification(mock_graphdb_client)


class TestMRCredits:
    """Test Materials & Resources (MR) credit calculations."""

    def test_calculate_mr_credits_basic(self, trees_cert):
        """Test basic MR credits calculation."""
        materials = [
            {
                "material_id": "mat1",
                "quantity": 100,
                "value": 10000,
                "recycled_content": 0.35,  # 35% recycled
                "has_green_label": True
            },
            {
                "material_id": "mat2",
                "quantity": 50,
                "value": 5000,
                "recycled_content": 0.20,  # 20% recycled
                "has_green_label": False
            }
        ]

        result = trees_cert.calculate_mr_credits(materials)

        # Verify structure
        assert "mr1_score" in result
        assert "mr3_score" in result
        assert "mr4_score" in result
        assert "total_mr_score" in result
        assert "recycled_percentage" in result
        assert "green_labeled_percentage" in result

        # Verify recycled percentage: (10000*0.35 + 5000*0.20) / 15000 = 30%
        expected_recycled = ((10000 * 0.35) + (5000 * 0.20)) / 15000 * 100
        assert abs(result["recycled_percentage"] - expected_recycled) < 0.1

        # Verify green labeled: 10000 / 15000 = 66.67%
        expected_green = (10000 / 15000) * 100
        assert abs(result["green_labeled_percentage"] - expected_green) < 0.1

    def test_mr1_score_at_target(self, trees_cert):
        """Test MR1 score when exactly at 30% target."""
        materials = [
            {
                "quantity": 100,
                "value": 10000,
                "recycled_content": 0.30  # Exactly 30%
            }
        ]

        result = trees_cert.calculate_mr_credits(materials)

        # Should award full 2 points
        assert result["mr1_score"] == pytest.approx(2.0, rel=0.01)

    def test_mr1_score_above_target(self, trees_cert):
        """Test MR1 score when above 30% target."""
        materials = [
            {
                "quantity": 100,
                "value": 10000,
                "recycled_content": 0.45  # 45% recycled
            }
        ]

        result = trees_cert.calculate_mr_credits(materials)

        # Should cap at 2 points
        assert result["mr1_score"] == pytest.approx(2.0, rel=0.01)

    def test_mr3_score_at_target(self, trees_cert):
        """Test MR3 score when exactly at 30% green-labeled."""
        materials = [
            {"value": 7000, "has_green_label": True},
            {"value": 3000, "has_green_label": False}
        ]  # 70% green-labeled

        result = trees_cert.calculate_mr_credits(materials)

        # Should award full 2 points (exceeds 30%)
        assert result["mr3_score"] == pytest.approx(2.0, rel=0.01)

    def test_zero_materials(self, trees_cert):
        """Test with empty materials list."""
        result = trees_cert.calculate_mr_credits([])

        assert result["total_mr_score"] == 0.0
        assert result["recycled_percentage"] == 0.0
        assert result["green_labeled_percentage"] == 0.0


class TestGoldPathway:
    """Test Gold certification pathway analysis."""

    def test_gold_already_achieved(self, trees_cert):
        """Test pathway when Gold is already achieved."""
        result = trees_cert.check_gold_pathway(55.0)  # Above 50

        assert result["achievable"] is True
        assert result["status"] == "ACHIEVED"
        assert result["gap"] == 0
        assert result["estimated_effort"] == "NONE"

    def test_gold_close_gap(self, trees_cert):
        """Test pathway with small gap to Gold."""
        result = trees_cert.check_gold_pathway(47.0)  # 3 points short

        assert result["achievable"] is True
        assert result["gap"] == 3
        assert result["status"] == "IN_PROGRESS"
        assert result["estimated_effort"] == "LOW"
        assert len(result["recommendations"]) > 0

    def test_gold_medium_gap(self, trees_cert):
        """Test pathway with medium gap to Gold."""
        result = trees_cert.check_gold_pathway(40.0)  # 10 points short

        assert result["achievable"] is True
        assert result["gap"] == 10
        assert result["estimated_effort"] == "MEDIUM"

    def test_gold_large_gap(self, trees_cert):
        """Test pathway with large gap to Gold."""
        result = trees_cert.check_gold_pathway(25.0)  # 25 points short

        assert result["gap"] == 25
        assert result["estimated_effort"] == "HIGH"

    def test_gold_at_threshold(self, trees_cert):
        """Test pathway exactly at Gold threshold."""
        result = trees_cert.check_gold_pathway(50.0)  # Exactly 50

        assert result["achievable"] is True
        assert result["status"] == "ACHIEVED"
        assert result["gap"] == 0


class TestPlatinumPathway:
    """Test Platinum certification pathway analysis."""

    def test_platinum_already_achieved(self, trees_cert):
        """Test pathway when Platinum is already achieved."""
        result = trees_cert.check_platinum_pathway(75.0)  # Above 70

        assert result["achievable"] is True
        assert result["status"] == "ACHIEVED"
        assert result["gap"] == 0

    def test_platinum_small_gap(self, trees_cert):
        """Test pathway with small gap to Platinum."""
        result = trees_cert.check_platinum_pathway(65.0)  # 5 points short

        assert result["achievable"] is True
        assert result["gap"] == 5
        assert result["estimated_effort"] == "MEDIUM"

    def test_platinum_large_gap(self, trees_cert):
        """Test pathway with large gap to Platinum."""
        result = trees_cert.check_platinum_pathway(45.0)  # 25 points short

        assert result["gap"] == 25
        assert result["estimated_effort"] == "VERY_HIGH"


class TestCertificationReport:
    """Test comprehensive certification report generation."""

    def test_generate_report_mr_only(self, trees_cert):
        """Test report generation with MR credits only."""
        mr_credits = {
            "mr1_score": 1.5,
            "mr3_score": 1.8,
            "mr4_score": 1.2,
            "total_mr_score": 4.5,
            "max_mr_score": 10,
            "recycled_percentage": 25.0,
            "green_labeled_percentage": 27.0,
            "low_emission_percentage": 30.0
        }

        report = trees_cert.generate_certification_report(mr_credits)

        assert report["certification_level"] == "NOT_CERTIFIED"  # Only 4.5 points
        assert report["total_score"] == 4.5
        assert "MR" in report["category_breakdown"]
        assert report["category_breakdown"]["MR"]["score"] == 4.5

    def test_generate_report_with_other_categories(self, trees_cert):
        """Test report generation with multiple categories."""
        mr_credits = {
            "total_mr_score": 8.0,
            "max_mr_score": 10
        }

        other_scores = {
            "EN": 20.0,  # Energy
            "WA": 15.0,  # Water
            "WM": 4.0,   # Waste Management
            "IEQ": 10.0  # Indoor Environmental Quality
        }

        report = trees_cert.generate_certification_report(mr_credits, other_scores)

        # Total: 8 + 20 + 15 + 4 + 10 = 57 (Gold)
        assert report["certification_level"] == "GOLD"
        assert report["total_score"] == 57.0
        assert len(report["category_breakdown"]) == 5

    def test_generate_report_platinum_level(self, trees_cert):
        """Test report for Platinum certification."""
        mr_credits = {"total_mr_score": 9.0, "max_mr_score": 10}

        other_scores = {
            "EN": 24.0,
            "WA": 17.0,
            "WM": 5.0,
            "IEQ": 14.0,
            "MG": 5.0
        }

        report = trees_cert.generate_certification_report(mr_credits, other_scores)

        # Total: 9 + 24 + 17 + 5 + 14 + 5 = 74 (Platinum)
        assert report["certification_level"] == "PLATINUM"
        assert report["total_score"] == 74.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_negative_values_handled(self, trees_cert):
        """Test that negative values are handled gracefully."""
        materials = [
            {
                "value": -100,  # Invalid negative value
                "recycled_content": 0.3
            }
        ]

        # Should not raise exception, treat as 0
        result = trees_cert.calculate_mr_credits(materials)
        assert result["total_mr_score"] >= 0

    def test_very_large_values(self, trees_cert):
        """Test with very large material values."""
        materials = [
            {
                "value": 1e9,  # 1 billion
                "recycled_content": 0.3,
                "has_green_label": True
            }
        ]

        result = trees_cert.calculate_mr_credits(materials)

        # Should handle large values correctly
        assert result["mr1_score"] == pytest.approx(2.0, rel=0.01)
        assert result["mr3_score"] == pytest.approx(2.0, rel=0.01)

    def test_mixed_missing_optional_fields(self, trees_cert):
        """Test with materials missing optional fields."""
        materials = [
            {"value": 5000},  # Missing all optional fields
            {
                "value": 5000,
                "recycled_content": 0.5,
                "has_green_label": True
            }
        ]

        # Should not raise exception
        result = trees_cert.calculate_mr_credits(materials)
        assert "total_mr_score" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

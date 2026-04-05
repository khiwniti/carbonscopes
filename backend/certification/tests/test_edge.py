"""
Unit tests for EDGE V3 certification calculator.

Tests cover:
- Baseline calculation
- Reduction percentage calculation
- EDGE compliance checking
- Progress tracking
- Edge cases and error handling
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from ..edge import EDGECertification, EDGEError


@pytest.fixture
def mock_graphdb_client():
    """Create mock GraphDB client."""
    client = Mock()
    client.query = MagicMock(return_value={"results": {"bindings": []}})
    return client


@pytest.fixture
def edge_cert(mock_graphdb_client):
    """Create EDGE certification instance."""
    return EDGECertification(mock_graphdb_client)


class TestBaselineCalculation:
    """Test baseline calculation methods."""

    def test_calculate_baseline_regional(self, edge_cert):
        """Test baseline calculation using regional benchmark."""
        result = edge_cert.calculate_baseline(
            project_type="residential",
            floor_area=Decimal("1000")
        )

        assert "baseline_total" in result
        assert "baseline_per_sqm" in result
        assert result["project_type"] == "residential"
        assert result["floor_area"] == 1000.0
        assert result["methodology"] == "REGIONAL_BENCHMARK"

    def test_calculate_baseline_commercial(self, edge_cert):
        """Test baseline for commercial project."""
        result = edge_cert.calculate_baseline(
            project_type="commercial",
            floor_area=Decimal("2000")
        )

        # Commercial should have higher baseline than residential
        assert result["baseline_per_sqm"] > 280  # Residential default is 280

    def test_calculate_baseline_zero_area(self, edge_cert):
        """Test baseline with zero floor area."""
        result = edge_cert.calculate_baseline(
            project_type="residential",
            floor_area=Decimal("0")
        )

        assert result["baseline_total"] == 0.0
        assert result["baseline_per_sqm"] == 0.0


class TestReductionCalculation:
    """Test reduction percentage calculations."""

    def test_calculate_reduction_20_percent(self, edge_cert):
        """Test calculation for exactly 20% reduction."""
        baseline = Decimal("10000")
        actual = Decimal("8000")  # 20% reduction

        result = edge_cert.calculate_reduction(actual, baseline)

        assert result["reduction_percentage"] == pytest.approx(20.0, rel=0.01)
        assert result["reduction_absolute"] == 2000.0
        assert result["meets_edge_threshold"] is True

    def test_calculate_reduction_below_threshold(self, edge_cert):
        """Test calculation below 20% threshold."""
        baseline = Decimal("10000")
        actual = Decimal("8500")  # 15% reduction

        result = edge_cert.calculate_reduction(actual, baseline)

        assert result["reduction_percentage"] == pytest.approx(15.0, rel=0.01)
        assert result["meets_edge_threshold"] is False
        assert result["gap_percentage"] == pytest.approx(5.0, rel=0.01)

    def test_calculate_reduction_above_threshold(self, edge_cert):
        """Test calculation above 20% threshold."""
        baseline = Decimal("10000")
        actual = Decimal("7000")  # 30% reduction

        result = edge_cert.calculate_reduction(actual, baseline)

        assert result["reduction_percentage"] == pytest.approx(30.0, rel=0.01)
        assert result["meets_edge_threshold"] is True
        assert result["gap_percentage"] == 0.0

    def test_calculate_reduction_zero_baseline_error(self, edge_cert):
        """Test that zero baseline raises error."""
        with pytest.raises(EDGEError, match="Baseline carbon must be greater than zero"):
            edge_cert.calculate_reduction(Decimal("5000"), Decimal("0"))

    def test_calculate_reduction_negative_baseline_error(self, edge_cert):
        """Test that negative baseline raises error."""
        with pytest.raises(EDGEError, match="Baseline carbon must be greater than zero"):
            edge_cert.calculate_reduction(Decimal("5000"), Decimal("-100"))

    def test_calculate_reduction_actual_exceeds_baseline(self, edge_cert):
        """Test when actual exceeds baseline (negative reduction)."""
        baseline = Decimal("5000")
        actual = Decimal("6000")  # Worse than baseline

        result = edge_cert.calculate_reduction(actual, baseline)

        # Reduction should be negative
        assert result["reduction_percentage"] < 0
        assert result["meets_edge_threshold"] is False


class TestEDGECompliance:
    """Test EDGE certification compliance checking."""

    def test_edge_compliant_embodied_only(self, edge_cert):
        """Test EDGE compliance with embodied carbon only."""
        result = edge_cert.check_edge_compliance(
            reduction_percentage=Decimal("25")  # 25% reduction
        )

        assert result["edge_certified"] is True
        assert result["edge_advanced"] is False
        assert result["embodied_carbon_status"]["compliant"] is True

    def test_edge_not_compliant(self, edge_cert):
        """Test EDGE non-compliance."""
        result = edge_cert.check_edge_compliance(
            reduction_percentage=Decimal("15")  # Only 15%
        )

        assert result["edge_certified"] is False
        assert result["edge_advanced"] is False
        assert result["embodied_carbon_status"]["compliant"] is False
        assert len(result["recommendations"]) > 0

    def test_edge_advanced_compliant(self, edge_cert):
        """Test EDGE Advanced compliance."""
        result = edge_cert.check_edge_compliance(
            reduction_percentage=Decimal("25"),  # 25% embodied
            energy_reduction=Decimal("45")        # 45% energy
        )

        assert result["edge_certified"] is True
        assert result["edge_advanced"] is True
        assert result["embodied_carbon_status"]["compliant"] is True
        assert result["energy_status"]["compliant"] is True

    def test_edge_with_water_reduction(self, edge_cert):
        """Test EDGE compliance with water metrics."""
        result = edge_cert.check_edge_compliance(
            reduction_percentage=Decimal("22"),
            water_reduction=Decimal("25")
        )

        assert result["edge_certified"] is True
        assert result["water_status"]["compliant"] is True

    def test_edge_at_exact_threshold(self, edge_cert):
        """Test EDGE at exactly 20% threshold."""
        result = edge_cert.check_edge_compliance(
            reduction_percentage=Decimal("20.0")
        )

        assert result["edge_certified"] is True
        assert result["embodied_carbon_status"]["gap"] == 0.0


class TestProgressTracking:
    """Test progress tracking over time."""

    def test_track_progress_improving(self, edge_cert):
        """Test progress tracking with improving trend."""
        baseline = {
            "baseline_total": 100000.0,
            "baseline_per_sqm": 300.0
        }

        measurements = [
            {"date": "2026-01-01", "actual_carbon": 85000},  # 15% reduction
            {"date": "2026-02-01", "actual_carbon": 82000},  # 18% reduction
            {"date": "2026-03-01", "actual_carbon": 78000}   # 22% reduction
        ]

        result = edge_cert.track_progress(baseline, measurements)

        assert result["trend"] == "IMPROVING"
        assert len(result["progress_timeline"]) == 3
        assert result["latest_status"]["edge_certified"] is True

    def test_track_progress_declining(self, edge_cert):
        """Test progress tracking with declining trend."""
        baseline = {
            "baseline_total": 100000.0,
            "baseline_per_sqm": 300.0
        }

        measurements = [
            {"date": "2026-01-01", "actual_carbon": 78000},  # 22% reduction
            {"date": "2026-02-01", "actual_carbon": 82000},  # 18% reduction
            {"date": "2026-03-01", "actual_carbon": 85000}   # 15% reduction
        ]

        result = edge_cert.track_progress(baseline, measurements)

        assert result["trend"] == "DECLINING"

    def test_track_progress_single_measurement(self, edge_cert):
        """Test progress tracking with single measurement."""
        baseline = {
            "baseline_total": 100000.0,
            "baseline_per_sqm": 300.0
        }

        measurements = [
            {"date": "2026-01-01", "actual_carbon": 80000}
        ]

        result = edge_cert.track_progress(baseline, measurements)

        assert result["trend"] == "INSUFFICIENT_DATA"


class TestEDGEReport:
    """Test EDGE report generation."""

    def test_generate_edge_report_certified(self, edge_cert):
        """Test report generation for certified project."""
        baseline = {
            "baseline_total": 100000.0,
            "baseline_per_sqm": 300.0,
            "project_type": "residential"
        }

        reduction = {
            "actual_carbon": 78000.0,
            "baseline_carbon": 100000.0,
            "reduction_percentage": 22.0,
            "meets_edge_threshold": True
        }

        compliance = {
            "edge_certified": True,
            "edge_advanced": False,
            "embodied_carbon_status": {
                "compliant": True,
                "reduction_percentage": 22.0
            }
        }

        report = edge_cert.generate_edge_report(baseline, reduction, compliance)

        assert report["certification_status"]["edge_certified"] is True
        assert report["certification_status"]["certification_level"] == "EDGE"
        assert "baseline" in report
        assert "reduction" in report
        assert "compliance" in report

    def test_generate_edge_report_advanced(self, edge_cert):
        """Test report generation for EDGE Advanced."""
        baseline = {"baseline_total": 100000.0, "baseline_per_sqm": 300.0}
        reduction = {"reduction_percentage": 22.0}
        compliance = {"edge_certified": True, "edge_advanced": True}

        report = edge_cert.generate_edge_report(baseline, reduction, compliance)

        assert report["certification_status"]["certification_level"] == "EDGE Advanced"

    def test_generate_edge_report_not_certified(self, edge_cert):
        """Test report generation for non-certified project."""
        baseline = {"baseline_total": 100000.0, "baseline_per_sqm": 300.0}
        reduction = {"reduction_percentage": 15.0}
        compliance = {"edge_certified": False, "edge_advanced": False}

        report = edge_cert.generate_edge_report(baseline, reduction, compliance)

        assert report["certification_status"]["certification_level"] == "Not Certified"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_large_baseline(self, edge_cert):
        """Test with very large baseline values."""
        result = edge_cert.calculate_baseline(
            project_type="commercial",
            floor_area=Decimal("1000000")  # 1 million m²
        )

        assert result["baseline_total"] > 0
        assert result["baseline_per_sqm"] > 0

    def test_decimal_precision(self, edge_cert):
        """Test that decimal precision is maintained."""
        baseline = Decimal("10000.123456789")
        actual = Decimal("8000.123456789")

        result = edge_cert.calculate_reduction(actual, baseline)

        # Should maintain precision in calculations
        assert isinstance(result["reduction_absolute"], float)

    def test_unknown_project_type(self, edge_cert):
        """Test with unknown project type."""
        result = edge_cert.calculate_baseline(
            project_type="unknown_type",
            floor_area=Decimal("1000")
        )

        # Should use default baseline factor
        assert result["baseline_total"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

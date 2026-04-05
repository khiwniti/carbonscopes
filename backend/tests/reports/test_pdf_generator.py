"""Tests for PDF report generator."""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import tempfile

from reports.generators.pdf_generator import PDFReportGenerator


@pytest.fixture
def pdf_generator():
    """Create PDF generator instance."""
    return PDFReportGenerator()


@pytest.fixture
def sample_report_data():
    """Sample carbon analysis data for testing."""
    return {
        "analysis_id": "test-analysis-001",
        "project_name": "Test Construction Project",
        "boq_filename": "test_boq.xlsx",
        "tgo_version": "2026-03",
        "total_carbon": 125000.50,
        "material_count": 45,
        "matched_count": 42,
        "auto_matched_count": 38,
        "timestamp": datetime.now().isoformat(),
        "breakdown": [
            {
                "line_number": "01.01.001",
                "description_th": "คอนกรีตผสมเสร็จ fc 240 ksc",
                "description_en": "Ready-mix concrete fc 240 ksc",
                "quantity": 250.0,
                "unit": "ลบ.ม.",
                "carbon": 52500.0,
                "percentage": 42.0,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "02.01.002",
                "description_th": "เหล็กเส้นกลม SR24",
                "description_en": "Round steel bar SR24",
                "quantity": 15000.0,
                "unit": "กก.",
                "carbon": 27000.0,
                "percentage": 21.6,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "03.02.001",
                "description_th": "อิฐมอญ 4x8x16 ซม.",
                "description_en": "Clay brick 4x8x16 cm",
                "quantity": 50000.0,
                "unit": "ก้อน",
                "carbon": 12500.0,
                "percentage": 10.0,
                "match_classification": "auto_matched"
            },
        ],
        "statistics": {
            "auto_matched": 38,
            "review_required": 4,
            "rejected": 3,
            "auto_match_rate": 84.4
        }
    }


@pytest.fixture
def sample_audit_trail():
    """Sample audit trail data."""
    return {
        "metadata": {
            "analysis_id": "test-analysis-001",
            "calculator_version": "1.0.0",
            "tgo_version": "2026-03",
            "brightway_version": "2.4.6",
            "calculation_date": datetime.now().isoformat()
        },
        "material_calculations": [
            {
                "boq_line_number": "01.01.001",
                "description_th": "คอนกรีตผสมเสร็จ fc 240 ksc",
                "tgo_material_id": "tgo:concrete_240",
                "quantity": 250.0,
                "unit": "ลบ.ม.",
                "emission_factor_value": 210.0,
                "emission_factor_unit": "kgCO2e/m3",
                "carbon_result": 52500.0,
                "calculation_formula": "250.0 ลบ.ม. × 210.0 kgCO2e/m3 = 52500.0 kgCO2e",
                "match_confidence": 0.95
            }
        ]
    }


class TestPDFGenerator:
    """Test suite for PDF report generator."""

    def test_generator_initialization(self, pdf_generator):
        """Test PDF generator initializes correctly."""
        assert pdf_generator is not None
        assert pdf_generator.templates_dir.exists()
        assert pdf_generator.jinja_env is not None
        assert pdf_generator.font_config is not None

    def test_generate_executive_summary_english(self, pdf_generator, sample_report_data, tmp_path):
        """Test generating English executive summary PDF."""
        output_path = tmp_path / "executive_summary_en.pdf"

        pdf_bytes = pdf_generator.generate_executive_summary(
            data=sample_report_data,
            output_path=output_path,
            language="en"
        )

        # Verify PDF generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Verify it's a valid PDF (starts with %PDF)
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_executive_summary_thai(self, pdf_generator, sample_report_data, tmp_path):
        """Test generating Thai executive summary PDF."""
        output_path = tmp_path / "executive_summary_th.pdf"

        pdf_bytes = pdf_generator.generate_executive_summary(
            data=sample_report_data,
            output_path=output_path,
            language="th"
        )

        # Verify PDF generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert output_path.exists()
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_detailed_report_english(
        self,
        pdf_generator,
        sample_report_data,
        sample_audit_trail,
        tmp_path
    ):
        """Test generating detailed report with audit trail."""
        output_path = tmp_path / "detailed_report_en.pdf"

        pdf_bytes = pdf_generator.generate_detailed_report(
            data=sample_report_data,
            audit_trail=sample_audit_trail,
            output_path=output_path,
            language="en"
        )

        # Verify PDF generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert output_path.exists()
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_detailed_report_thai(
        self,
        pdf_generator,
        sample_report_data,
        sample_audit_trail,
        tmp_path
    ):
        """Test generating Thai detailed report."""
        output_path = tmp_path / "detailed_report_th.pdf"

        pdf_bytes = pdf_generator.generate_detailed_report(
            data=sample_report_data,
            audit_trail=sample_audit_trail,
            output_path=output_path,
            language="th"
        )

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert output_path.exists()

    def test_generate_without_output_path(self, pdf_generator, sample_report_data):
        """Test generating PDF without saving to file."""
        pdf_bytes = pdf_generator.generate_executive_summary(
            data=sample_report_data,
            language="en"
        )

        # Should still return PDF bytes
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

    def test_format_number_filter(self, pdf_generator):
        """Test number formatting filter."""
        formatter = pdf_generator._format_number

        assert formatter(1234.56) == "1,234.56"
        assert formatter(1000000) == "1,000,000.00"
        assert formatter("1234.56") == "1,234.56"

    def test_format_percentage_filter(self, pdf_generator):
        """Test percentage formatting filter."""
        formatter = pdf_generator._format_percentage

        assert formatter(42.5) == "42.5%"
        assert formatter(100) == "100.0%"
        assert formatter(0.123) == "0.1%"

    def test_format_decimal_filter(self, pdf_generator):
        """Test decimal formatting filter."""
        formatter = pdf_generator._format_decimal

        assert formatter(Decimal("123.456"), 2) == "123.46"
        assert formatter(123.456789, 3) == "123.457"
        assert formatter(100, 0) == "100"

    def test_format_date_filter(self, pdf_generator):
        """Test date formatting filter."""
        formatter = pdf_generator._format_date

        dt = datetime(2026, 3, 24, 15, 30, 0)
        assert formatter(dt, "%Y-%m-%d") == "2026-03-24"
        assert formatter(dt, "%B %d, %Y") == "March 24, 2026"

        # Test ISO string
        iso_string = "2026-03-24T15:30:00"
        assert formatter(iso_string, "%Y-%m-%d") == "2026-03-24"

    def test_prepare_executive_context(self, pdf_generator, sample_report_data):
        """Test context preparation for executive summary."""
        context = pdf_generator._prepare_executive_context(sample_report_data, "en")

        assert context["analysis_id"] == "test-analysis-001"
        assert context["project_name"] == "Test Construction Project"
        assert context["total_carbon"] == 125000.50
        assert context["total_carbon_tonnes"] == 125.0005
        assert context["material_count"] == 45
        assert context["matched_count"] == 42
        assert "top_contributors" in context
        assert len(context["top_contributors"]) <= 5

    def test_prepare_detailed_context(
        self,
        pdf_generator,
        sample_report_data,
        sample_audit_trail
    ):
        """Test context preparation for detailed report."""
        context = pdf_generator._prepare_detailed_context(
            sample_report_data,
            sample_audit_trail,
            "en"
        )

        assert "breakdown" in context
        assert "audit_trail" in context
        assert context["show_audit_trail"] is True
        assert "methodology" in context
        assert "assumptions" in context

    def test_methodology_text_english(self, pdf_generator):
        """Test methodology text generation (English)."""
        text = pdf_generator._get_methodology_text("en")

        assert "ISO 14040" in text
        assert "Brightway2" in text
        assert "TGO" in text

    def test_methodology_text_thai(self, pdf_generator):
        """Test methodology text generation (Thai)."""
        text = pdf_generator._get_methodology_text("th")

        assert "ISO 14040" in text
        assert "Brightway2" in text
        assert "TGO" in text
        # Verify Thai characters present
        assert any(ord(c) >= 0x0E00 and ord(c) <= 0x0E7F for c in text)

    def test_assumptions_list_english(self, pdf_generator):
        """Test assumptions list (English)."""
        assumptions = pdf_generator._get_assumptions_text("en")

        assert isinstance(assumptions, list)
        assert len(assumptions) > 0
        assert any("TGO" in a for a in assumptions)
        assert any("embodied carbon" in a for a in assumptions)

    def test_assumptions_list_thai(self, pdf_generator):
        """Test assumptions list (Thai)."""
        assumptions = pdf_generator._get_assumptions_text("th")

        assert isinstance(assumptions, list)
        assert len(assumptions) > 0
        # Verify Thai characters present
        assert any(any(ord(c) >= 0x0E00 and ord(c) <= 0x0E7F for c in a) for a in assumptions)

    def test_missing_template_file(self, pdf_generator, sample_report_data):
        """Test error handling for missing template file."""
        # Try to generate with non-existent language
        with pytest.raises(Exception):  # Jinja2 will raise TemplateNotFound
            pdf_generator.generate_executive_summary(
                data=sample_report_data,
                language="fr"  # French template doesn't exist
            )

    def test_performance_executive_summary(self, pdf_generator, sample_report_data, benchmark):
        """Benchmark executive summary generation performance."""
        # Should complete in < 5 seconds
        result = benchmark(
            pdf_generator.generate_executive_summary,
            data=sample_report_data,
            language="en"
        )

        assert result is not None
        assert len(result) > 0

    @pytest.mark.slow
    def test_large_dataset_performance(self, pdf_generator, tmp_path):
        """Test PDF generation with large dataset (100+ materials)."""
        # Create large dataset
        large_data = {
            "analysis_id": "large-test",
            "project_name": "Large Project",
            "total_carbon": 1000000.0,
            "material_count": 150,
            "matched_count": 145,
            "timestamp": datetime.now().isoformat(),
            "breakdown": [
                {
                    "line_number": f"{i:06d}",
                    "description_th": f"วัสดุ {i}",
                    "quantity": 100.0 * i,
                    "unit": "หน่วย",
                    "carbon": 500.0 * i,
                    "percentage": 0.5
                }
                for i in range(150)
            ],
            "statistics": {"auto_matched": 145}
        }

        output_path = tmp_path / "large_report.pdf"

        pdf_bytes = pdf_generator.generate_executive_summary(
            data=large_data,
            output_path=output_path,
            language="th"
        )

        assert pdf_bytes is not None
        assert output_path.exists()

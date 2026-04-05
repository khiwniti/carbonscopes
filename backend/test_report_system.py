#!/usr/bin/env python
"""Quick validation script for report generation system.

Run this to verify the report generators are working correctly.
"""

from reports.generators.pdf_generator import PDFReportGenerator
from reports.generators.excel_generator import ExcelReportGenerator
from datetime import datetime
from pathlib import Path
import tempfile


def test_initialization():
    """Test that generators initialize correctly."""
    print("=" * 60)
    print("Testing Report Generation System")
    print("=" * 60)

    # Test PDF Generator initialization
    pdf_gen = PDFReportGenerator()
    print("\n✅ PDF Generator initialized")
    print(f"   Templates dir: {pdf_gen.templates_dir}")
    print(f"   Templates exist: {pdf_gen.templates_dir.exists()}")
    print(f"   Static dir: {pdf_gen.static_dir}")

    # Test Excel Generator initialization
    excel_gen = ExcelReportGenerator()
    print("\n✅ Excel Generator initialized")

    # Test template loading
    template = pdf_gen.jinja_env.get_template('executive_summary.html')
    print("\n✅ Executive summary template loaded (English)")

    template_th = pdf_gen.jinja_env.get_template('executive_summary_th.html')
    print("✅ Executive summary template loaded (Thai)")

    # Test custom filters
    print("\n✅ Custom Jinja2 filters working:")
    print(f"   format_number(1234.56): {pdf_gen._format_number(1234.56)}")
    print(f"   format_percentage(42.5): {pdf_gen._format_percentage(42.5)}")
    print(f"   format_decimal(123.456, 2): {pdf_gen._format_decimal(123.456, 2)}")
    print(f"   format_date(now): {pdf_gen._format_date(datetime.now(), '%Y-%m-%d')}")

    print("\n" + "=" * 60)
    print("✅ ALL SYSTEMS OPERATIONAL")
    print("=" * 60)


def test_sample_generation():
    """Test generating sample reports."""
    print("\n\nGenerating Sample Reports...")
    print("-" * 60)

    # Sample data
    sample_data = {
        "analysis_id": "test-001",
        "project_name": "Test Project",
        "total_carbon": 125000.50,
        "material_count": 45,
        "matched_count": 42,
        "timestamp": datetime.now().isoformat(),
        "breakdown": [
            {
                "line_number": "01.01.001",
                "description_th": "คอนกรีตผสมเสร็จ",
                "quantity": 250.0,
                "unit": "ลบ.ม.",
                "carbon": 52500.0,
                "percentage": 42.0
            }
        ],
        "statistics": {"auto_matched": 38}
    }

    # Create temp directory
    temp_dir = Path(tempfile.gettempdir()) / "carbon_report_test"
    temp_dir.mkdir(exist_ok=True)

    # Generate PDF (English)
    pdf_gen = PDFReportGenerator()
    try:
        pdf_path = temp_dir / "test_executive_summary_en.pdf"
        pdf_bytes = pdf_gen.generate_executive_summary(
            data=sample_data,
            output_path=pdf_path,
            language="en"
        )
        print(f"✅ PDF Generated (EN): {pdf_path}")
        print(f"   Size: {len(pdf_bytes):,} bytes")
    except Exception as e:
        print(f"❌ PDF Generation failed: {e}")

    # Generate PDF (Thai)
    try:
        pdf_path_th = temp_dir / "test_executive_summary_th.pdf"
        pdf_bytes_th = pdf_gen.generate_executive_summary(
            data=sample_data,
            output_path=pdf_path_th,
            language="th"
        )
        print(f"✅ PDF Generated (TH): {pdf_path_th}")
        print(f"   Size: {len(pdf_bytes_th):,} bytes")
    except Exception as e:
        print(f"❌ PDF Generation (Thai) failed: {e}")

    # Generate Excel
    excel_gen = ExcelReportGenerator()
    try:
        excel_path = temp_dir / "test_carbon_report.xlsx"
        excel_bytes = excel_gen.generate_report(
            data=sample_data,
            output_path=excel_path
        )
        print(f"✅ Excel Generated: {excel_path}")
        print(f"   Size: {len(excel_bytes):,} bytes")
    except Exception as e:
        print(f"❌ Excel Generation failed: {e}")

    print("\n" + "-" * 60)
    print(f"Sample reports saved to: {temp_dir}")
    print("-" * 60)


if __name__ == "__main__":
    test_initialization()

    # Uncomment to test actual report generation
    # test_sample_generation()

    print("\n\n🎉 Report Generation System Validation Complete!")
    print("\nTo generate sample reports, uncomment test_sample_generation() in this script.")
    print("Or run: pytest tests/reports/ -v")

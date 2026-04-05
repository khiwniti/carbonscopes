"""Shared fixtures for report generation tests."""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import tempfile


@pytest.fixture
def mock_carbon_data():
    """Complete mock carbon analysis data."""
    return {
        "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
        "project_name": "Bangkok Condominium Project",
        "boq_filename": "bangkok_condo_boq.xlsx",
        "boq_file_id": "file-123",
        "tgo_version": "2026-03",
        "total_carbon": 245678.90,
        "material_count": 87,
        "matched_count": 82,
        "auto_matched_count": 75,
        "timestamp": "2026-03-24T10:30:00+00:00",
        "breakdown": [
            {
                "line_number": "01.01.001",
                "description_th": "คอนกรีตผสมเสร็จ fc 280 ksc",
                "description_en": "Ready-mix concrete fc 280 ksc",
                "quantity": 450.0,
                "unit": "ลบ.ม.",
                "carbon": 94500.0,
                "percentage": 38.5,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "02.01.002",
                "description_th": "เหล็กเส้นเหนียว SD40",
                "description_en": "Deformed steel bar SD40",
                "quantity": 25000.0,
                "unit": "กก.",
                "carbon": 45000.0,
                "percentage": 18.3,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "03.01.003",
                "description_th": "อิฐมอญ 4x8x16 ซม.",
                "description_en": "Clay brick 4x8x16 cm",
                "quantity": 80000.0,
                "unit": "ก้อน",
                "carbon": 32000.0,
                "percentage": 13.0,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "04.02.001",
                "description_th": "ปูนซีเมนต์ปอร์ตแลนด์ ตราช้าง TPI",
                "description_en": "Portland cement TPI",
                "quantity": 2500.0,
                "unit": "ถุง",
                "carbon": 22500.0,
                "percentage": 9.2,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "05.01.004",
                "description_th": "กระเบื้องดินเผา 6x30 ซม.",
                "description_en": "Terracotta tile 6x30 cm",
                "quantity": 3500.0,
                "unit": "ตร.ม.",
                "carbon": 17500.0,
                "percentage": 7.1,
                "match_classification": "review_required"
            },
            {
                "line_number": "06.03.005",
                "description_th": "แผ่นยิปซัม 9 มม.",
                "description_en": "Gypsum board 9 mm",
                "quantity": 5000.0,
                "unit": "ตร.ม.",
                "carbon": 15000.0,
                "percentage": 6.1,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "07.02.006",
                "description_th": "สีทาภายนอก TOA Weatherguard",
                "description_en": "Exterior paint TOA Weatherguard",
                "quantity": 500.0,
                "unit": "แกลลอน",
                "carbon": 8750.0,
                "percentage": 3.6,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "08.01.007",
                "description_th": "กระจกลามิเนต 6+6 มม.",
                "description_en": "Laminated glass 6+6 mm",
                "quantity": 800.0,
                "unit": "ตร.ม.",
                "carbon": 6400.0,
                "percentage": 2.6,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "09.04.008",
                "description_th": "ท่อ PVC ขนาด 4 นิ้ว",
                "description_en": "PVC pipe 4 inch",
                "quantity": 1200.0,
                "unit": "ม.",
                "carbon": 3600.0,
                "percentage": 1.5,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "10.02.009",
                "description_th": "สายไฟ THW 2.5 ตร.มม.",
                "description_en": "Electric wire THW 2.5 sq.mm",
                "quantity": 5000.0,
                "unit": "ม.",
                "carbon": 428.90,
                "percentage": 0.2,
                "match_classification": "auto_matched"
            },
        ],
        "statistics": {
            "auto_matched": 75,
            "review_required": 7,
            "rejected": 5,
            "auto_match_rate": 86.2,
            "total_items": 87
        }
    }


@pytest.fixture
def mock_audit_trail():
    """Complete mock audit trail data."""
    return {
        "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
        "metadata": {
            "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
            "calculator_version": "1.0.0",
            "tgo_version": "2026-03",
            "brightway_version": "2.4.6",
            "calculation_date": "2026-03-24T10:30:00+00:00",
            "total_materials": 87,
            "calculation_time_seconds": 4.2
        },
        "material_calculations": [
            {
                "boq_line_number": "01.01.001",
                "description_th": "คอนกรีตผสมเสร็จ fc 280 ksc",
                "description_en": "Ready-mix concrete fc 280 ksc",
                "tgo_material_id": "tgo:concrete_280_ksc",
                "tgo_material_label": "Ready-mix Concrete 280 kg/cm²",
                "quantity": 450.0,
                "unit": "ลบ.ม.",
                "emission_factor_value": 210.0,
                "emission_factor_unit": "kgCO2e/m³",
                "emission_factor_version": "2026-03",
                "emission_factor_effective_date": "2026-01-01",
                "carbon_result": 94500.0,
                "calculation_formula": "450.0 ลบ.ม. × 210.0 kgCO2e/m³ = 94500.0 kgCO2e",
                "match_confidence": 0.96,
                "match_classification": "auto_matched"
            },
            {
                "boq_line_number": "02.01.002",
                "description_th": "เหล็กเส้นเหนียว SD40",
                "description_en": "Deformed steel bar SD40",
                "tgo_material_id": "tgo:steel_bar_sd40",
                "tgo_material_label": "Deformed Steel Bar SD40",
                "quantity": 25000.0,
                "unit": "กก.",
                "emission_factor_value": 1.8,
                "emission_factor_unit": "kgCO2e/kg",
                "emission_factor_version": "2026-03",
                "emission_factor_effective_date": "2026-01-01",
                "carbon_result": 45000.0,
                "calculation_formula": "25000.0 กก. × 1.8 kgCO2e/kg = 45000.0 kgCO2e",
                "match_confidence": 0.94,
                "match_classification": "auto_matched"
            },
        ]
    }


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

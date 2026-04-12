"""
Tests for carbon calculation pipeline.

Requires:
- Mock GraphDB client
- Mock PostgreSQL database
- Sample BOQ Excel files
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from boq.carbon_pipeline import CarbonCalculationPipeline
from boq.audit_trail import CalculationAudit, MaterialCalculationAudit
from boq.material_matching import BOQMaterialMatch
from boq.models import BOQMaterial, BOQParseResult
from lca.carbon_calculator import CarbonCalculator


@pytest.fixture
def mock_graphdb_client():
    """Mock GraphDB client."""
    client = Mock()
    # Mock emission factor query response will be handled in get_emission_factor mock
    return client


@pytest.fixture
def mock_carbon_calculator():
    """Mock Brightway2 calculator."""
    calculator = Mock(spec=CarbonCalculator)
    return calculator


@pytest.fixture
def sample_boq_material():
    """Create sample BOQ material for testing."""
    return BOQMaterial(
        line_number=1,
        description_th="คอนกรีต C30",
        description_en="Concrete C30",
        quantity=Decimal("100.0"),
        unit="m³",
        unit_raw="ลบ.ม.",
        conversion_factor=Decimal("1.0")
    )


@pytest.fixture
def sample_boq_parse_result(sample_boq_material):
    """Create sample BOQ parse result."""
    return BOQParseResult(
        file_id="test_file_id_12345",
        filename="test.xlsx",
        status="parsed",
        materials=[sample_boq_material],
        metadata={"success_rate": 100.0, "total_lines": 1, "parsed_lines": 1}
    )


@pytest.fixture
def sample_boq_material_match(sample_boq_material):
    """Create sample BOQ material match."""
    return BOQMaterialMatch(
        boq_material=sample_boq_material,
        tgo_match={
            "material_id": "http://tgo.or.th/materials/concrete-c30",
            "label": "Concrete C30",
            "category": "Concrete"
        },
        confidence=Decimal("0.95"),
        classification="auto_match",
        match_method="exact"
    )


def test_pipeline_initialization(mock_graphdb_client, mock_carbon_calculator):
    """Test pipeline initialization."""
    pipeline = CarbonCalculationPipeline(
        graphdb_client=mock_graphdb_client,
        carbon_calculator=mock_carbon_calculator,
        tgo_version="2026-03"
    )

    assert pipeline.graphdb_client == mock_graphdb_client
    assert pipeline.carbon_calculator == mock_carbon_calculator
    assert pipeline.tgo_version == "2026-03"


@patch('carbonscope.backend.boq.carbon_pipeline.parse_boq')
@patch('carbonscope.backend.boq.carbon_pipeline.match_boq_materials')
@patch('carbonscope.backend.boq.carbon_pipeline.get_emission_factor')
@patch('carbonscope.backend.boq.carbon_pipeline.get_db')
def test_calculate_boq_carbon_complete_pipeline(
    mock_get_db,
    mock_get_ef,
    mock_match,
    mock_parse,
    mock_graphdb_client,
    mock_carbon_calculator,
    sample_boq_parse_result,
    sample_boq_material_match
):
    """Test complete pipeline execution."""
    # Mock parse_boq response
    mock_parse.return_value = sample_boq_parse_result

    # Mock match_boq_materials response
    mock_match.return_value = [sample_boq_material_match]

    # Mock get_emission_factor response
    mock_get_ef.return_value = {
        "material_id": "http://tgo.or.th/materials/concrete-c30",
        "emission_factor": Decimal("445.6"),
        "unit": "kgCO2e/m³",
        "label_en": "Concrete C30",
        "label_th": "คอนกรีต C30",
        "category": "Concrete",
        "effective_date": "2026-01-15",
        "version": "2026-03"
    }

    # Mock database session
    mock_db_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db_session
    mock_db_session.flush = MagicMock()
    mock_db_session.commit = MagicMock()

    # Create a mock audit with id
    mock_audit = Mock()
    mock_audit.id = "test-audit-id-123"
    mock_db_session.add = MagicMock(side_effect=lambda obj: setattr(obj, 'id', "test-audit-id-123"))

    pipeline = CarbonCalculationPipeline(
        graphdb_client=mock_graphdb_client,
        carbon_calculator=mock_carbon_calculator
    )

    # Execute pipeline
    result = pipeline.calculate_boq_carbon("/fake/path/test.xlsx")

    # Assertions
    assert result["boq_file_id"] == "test_file_id_12345"
    assert "total_carbon" in result
    assert result["material_count"] == 1
    assert "analysis_id" in result
    assert "breakdown" in result
    assert len(result["breakdown"]) == 1


def test_calculate_material_carbon_with_match(
    mock_graphdb_client,
    mock_carbon_calculator,
    sample_boq_material_match
):
    """Test material carbon calculation with successful match."""
    pipeline = CarbonCalculationPipeline(
        graphdb_client=mock_graphdb_client,
        carbon_calculator=mock_carbon_calculator
    )

    with patch('carbonscope.backend.boq.carbon_pipeline.get_emission_factor') as mock_get_ef:
        mock_get_ef.return_value = {
            "emission_factor": Decimal("445.6"),
            "unit": "kgCO2e/m³",
            "version": "2026-03",
            "effective_date": "2026-01-15"
        }

        result = pipeline._calculate_material_carbon(sample_boq_material_match)

        assert result["carbon_result"] == Decimal("100.0") * Decimal("445.6")
        assert result["calculation_formula"] is not None
        assert "100.0 m³ × 445.6" in result["calculation_formula"]
        assert result["tgo_material_id"] == "http://tgo.or.th/materials/concrete-c30"


def test_calculate_material_carbon_no_match(
    mock_graphdb_client,
    mock_carbon_calculator,
    sample_boq_material
):
    """Test material carbon calculation with no match."""
    # Create match with no TGO match
    no_match = BOQMaterialMatch(
        boq_material=sample_boq_material,
        tgo_match=None,
        confidence=Decimal("0.0"),
        classification="rejected",
        match_method="none"
    )

    pipeline = CarbonCalculationPipeline(
        graphdb_client=mock_graphdb_client,
        carbon_calculator=mock_carbon_calculator
    )

    result = pipeline._calculate_material_carbon(no_match)

    assert result["carbon_result"] is None
    assert result["tgo_material_id"] is None
    assert result["calculation_formula"] is None
    assert result["match_classification"] == "rejected"


def test_pipeline_with_unmatched_materials():
    """Test pipeline handling of unmatched materials."""
    # Materials with no TGO match should return carbon = None
    pass  # TODO: Implement


def test_pipeline_audit_trail_storage():
    """Test audit trail is correctly stored in database."""
    # Use pytest-postgresql or similar for database testing
    pass  # TODO: Implement


def test_get_audit_trail():
    """Test audit trail retrieval."""
    pass  # TODO: Implement


def test_pipeline_deterministic_calculation():
    """Test pipeline produces deterministic results."""
    # Run same BOQ twice, assert identical results
    pass  # TODO: Implement


def test_pipeline_error_handling():
    """Test pipeline error handling."""
    # Test: BOQ parsing failure
    # Test: Material matching failure
    # Test: Emission factor not found
    # Test: Database storage failure
    pass  # TODO: Implement


def test_decimal_precision_maintained():
    """Test that Decimal precision is maintained throughout pipeline."""
    # Verify no float conversion occurs
    pass  # TODO: Implement


def test_human_readable_formula():
    """Test calculation formula is human-readable."""
    # Verify formula format: "100.0 m³ × 445.6 kgCO2e/m³ = 44560.0 kgCO2e"
    pass  # TODO: Implement

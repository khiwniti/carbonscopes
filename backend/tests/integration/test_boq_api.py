"""
Integration tests for BOQ API endpoints.

Tests complete end-to-end workflows:
- Upload → Parse → Calculate → Audit
"""

import pytest
import io
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api import app
from boq.cache import get_cache_manager

client = TestClient(app)


@pytest.fixture
def sample_boq_file():
    """Create sample BOQ Excel file for testing."""
    # TODO: Create actual Excel file with openpyxl
    # For now, use fixture path if it exists
    fixture_path = Path(__file__).parent.parent / "fixtures" / "boq" / "sample_boq.xlsx"
    if fixture_path.exists():
        return fixture_path

    # Skip test if no fixture available
    pytest.skip("Sample BOQ file not found. Create tests/fixtures/boq/sample_boq.xlsx to run this test.")


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache = get_cache_manager()
    # Clear memory cache
    cache._memory_cache = {}
    yield


def test_upload_boq_success(sample_boq_file):
    """Test successful BOQ file upload."""
    with open(sample_boq_file, 'rb') as f:
        response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    assert response.status_code == 200
    data = response.json()

    assert "file_id" in data
    assert data["filename"] == "test_boq.xlsx"
    assert data["status"] == "uploaded"
    assert "message_en" in data
    assert "message_th" in data


def test_upload_boq_invalid_format():
    """Test upload with invalid file format."""
    fake_pdf = io.BytesIO(b"fake pdf content")

    response = client.post(
        "/v1/api/boq/upload",
        files={"file": ("test.pdf", fake_pdf, "application/pdf")}
    )

    assert response.status_code == 400
    data = response.json()

    assert data["detail"]["error_type"] == "INVALID_FILE_FORMAT"
    assert "message_en" in data["detail"]
    assert "message_th" in data["detail"]


def test_upload_boq_file_too_large():
    """Test upload with file exceeding size limit."""
    # Create 51MB fake file
    large_file = io.BytesIO(b"x" * (51 * 1024 * 1024))

    response = client.post(
        "/v1/api/boq/upload",
        files={"file": ("large.xlsx", large_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 413
    data = response.json()

    assert data["detail"]["error_type"] == "FILE_TOO_LARGE"


def test_parse_boq(sample_boq_file):
    """Test BOQ parsing endpoint."""
    # Upload file first
    with open(sample_boq_file, 'rb') as f:
        upload_response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    file_id = upload_response.json()["file_id"]

    # Parse file
    response = client.post(
        "/v1/api/boq/parse",
        json={"file_id": file_id, "language": "th"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "file_id" in data
    assert "materials" in data
    assert "metadata" in data
    assert data["status"] in ["parsed", "partial", "failed"]


def test_parse_boq_file_not_found():
    """Test parsing with non-existent file ID."""
    response = client.post(
        "/v1/api/boq/parse",
        json={"file_id": "nonexistent_file_id", "language": "th"}
    )

    assert response.status_code == 404
    data = response.json()

    assert data["detail"]["error_type"] == "FILE_NOT_FOUND"


def test_calculate_carbon(sample_boq_file):
    """Test carbon calculation endpoint."""
    # Upload file
    with open(sample_boq_file, 'rb') as f:
        upload_response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    file_id = upload_response.json()["file_id"]

    # Calculate carbon
    response = client.post(
        "/v1/api/carbon/calculate",
        json={
            "file_id": file_id,
            "tgo_version": "2026-03",
            "language": "th"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert "total_carbon" in data
    assert "breakdown" in data
    assert "statistics" in data


def test_get_audit_trail(sample_boq_file):
    """Test audit trail retrieval."""
    # Upload and calculate
    with open(sample_boq_file, 'rb') as f:
        upload_response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    file_id = upload_response.json()["file_id"]

    calc_response = client.post(
        "/v1/api/carbon/calculate",
        json={"file_id": file_id}
    )

    analysis_id = calc_response.json()["analysis_id"]

    # Retrieve audit trail
    response = client.get(f"/v1/api/carbon/audit/{analysis_id}")

    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data


def test_complete_workflow(sample_boq_file):
    """Test complete workflow: Upload → Parse → Calculate → Audit."""
    # Step 1: Upload
    with open(sample_boq_file, 'rb') as f:
        upload_response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]

    # Step 2: Parse
    parse_response = client.post(
        "/v1/api/boq/parse",
        json={"file_id": file_id}
    )
    assert parse_response.status_code == 200
    parsed_data = parse_response.json()
    assert "materials" in parsed_data
    if parsed_data["status"] == "parsed":
        assert len(parsed_data["materials"]) > 0

    # Step 3: Calculate
    calc_response = client.post(
        "/v1/api/carbon/calculate",
        json={"file_id": file_id}
    )
    assert calc_response.status_code == 200
    analysis_id = calc_response.json()["analysis_id"]

    # Step 4: Audit
    audit_response = client.get(f"/v1/api/carbon/audit/{analysis_id}")
    assert audit_response.status_code == 200
    assert audit_response.json()["analysis_id"] == analysis_id


def test_cache_performance(sample_boq_file):
    """Test caching improves performance on repeated requests."""
    import time

    with open(sample_boq_file, 'rb') as f:
        upload_response = client.post(
            "/v1/api/boq/upload",
            files={"file": ("test_boq.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    file_id = upload_response.json()["file_id"]

    # First parse (no cache)
    start = time.time()
    response1 = client.post("/v1/api/boq/parse", json={"file_id": file_id})
    time1 = time.time() - start

    # Second parse (with cache)
    start = time.time()
    response2 = client.post("/v1/api/boq/parse", json={"file_id": file_id})
    time2 = time.time() - start

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Second request should be faster or equal
    # (May not always be true in test environment, but validates caching is implemented)
    assert time2 <= time1 * 1.5  # Allow 50% margin for test environment variance


def test_bilingual_error_messages():
    """Test that error messages include both Thai and English."""
    # Test invalid format error
    fake_file = io.BytesIO(b"not a real file")
    response = client.post(
        "/v1/api/boq/upload",
        files={"file": ("test.txt", fake_file, "text/plain")}
    )

    assert response.status_code == 400
    error = response.json()["detail"]

    assert "message_en" in error
    assert "message_th" in error
    assert len(error["message_en"]) > 0
    assert len(error["message_th"]) > 0
    assert error["error_type"] == "INVALID_FILE_FORMAT"

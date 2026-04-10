import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime
import uuid

from backend.api.v1.reports import router as reports_router, ReportGenerationRequest, ReportGenerationResponse

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(reports_router)
    return TestClient(app)

def test_generate_report_pdf_success(client):
    """Test successful PDF report generation."""
    # Mock generators to avoid actual PDF/Excel creation
    with patch("backend.api.v1.reports.PDFReportGenerator") as mock_pdf_gen, \
         patch("backend.api.v1.reports.ExcelReportGenerator") as mock_excel_gen:
        
        mock_pdf_gen.return_value.generate_executive_summary.return_value = b"pdf content"
        
        request_data = {
            "analysis_id": str(uuid.uuid4()),
            "report_type": "pdf",
            "language": "en",
            "include_audit_trail": False
        }
        
        response = client.post("/api/v1/reports/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["report_type"] == "pdf"
        assert data["pdf_url"] is not None
        assert data["excel_url"] is None

def test_generate_report_excel_success(client):
    """Test successful Excel report generation."""
    with patch("backend.api.v1.reports.PDFReportGenerator") as mock_pdf_gen, \
         patch("backend.api.v1.reports.ExcelReportGenerator") as mock_excel_gen:
        
        mock_excel_gen.return_value.generate_report.return_value = b"excel content"
        
        request_data = {
            "analysis_id": str(uuid.uuid4()),
            "report_type": "excel",
            "language": "en"
        }
        
        response = client.post("/api/v1/reports/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["report_type"] == "excel"
        assert data["excel_url"] is not None
        assert data["pdf_url"] is None

def test_generate_report_both_success(client):
    """Test successful generation of both PDF and Excel reports."""
    with patch("backend.api.v1.reports.PDFReportGenerator") as mock_pdf_gen, \
         patch("backend.api.v1.reports.ExcelReportGenerator") as mock_excel_gen:
        
        mock_pdf_gen.return_value.generate_executive_summary.return_value = b"pdf content"
        mock_excel_gen.return_value.generate_report.return_value = b"excel content"
        
        request_data = {
            "analysis_id": str(uuid.uuid4()),
            "report_type": "both",
            "language": "en"
        }
        
        response = client.post("/api/v1/reports/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["pdf_url"] is not None
        assert data["excel_url"] is not None

def test_get_report_status_not_found(client):
    """Test getting status for a non-existent report."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/reports/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"]["error_type"] == "REPORT_NOT_FOUND"

def test_generate_report_invalid_request(client):
    """Test report generation with invalid request data."""
    # Missing analysis_id
    request_data = {
        "report_type": "pdf"
    }
    response = client.post("/api/v1/reports/generate", json=request_data)
    assert response.status_code == 422

def test_download_report_not_found(client):
    """Test downloading a non-existent report."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/reports/{fake_id}/download/pdf")
    assert response.status_code == 404

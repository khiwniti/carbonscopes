"""FastAPI endpoints for report generation.

Provides REST API for generating PDF and Excel carbon analysis reports.
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from reports.generators.pdf_generator import PDFReportGenerator
from reports.generators.excel_generator import ExcelReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


# ==================== Request/Response Models ====================

class ReportGenerationRequest(BaseModel):
    """Request model for report generation."""
    analysis_id: str = Field(description="Carbon analysis ID")
    report_type: str = Field(
        default="pdf",
        description="Report type: 'pdf', 'excel', or 'both'"
    )
    language: str = Field(
        default="en",
        description="Report language: 'en' or 'th'"
    )
    include_audit_trail: bool = Field(
        default=False,
        description="Include detailed audit trail (PDF only)"
    )
    project_name: Optional[str] = Field(
        default=None,
        description="Optional project name override"
    )


class ReportGenerationResponse(BaseModel):
    """Response model for report generation."""
    report_id: str
    analysis_id: str
    report_type: str
    language: str
    status: str  # "generating", "completed", "failed"
    pdf_url: Optional[str] = None
    excel_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


# ==================== In-memory report storage (replace with DB in production) ====================

_report_storage: Dict[str, Dict[str, Any]] = {}


def store_report(report_id: str, report_data: Dict[str, Any]) -> None:
    """Store generated report metadata (in-memory for now)."""
    _report_storage[report_id] = report_data


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve report metadata by ID."""
    return _report_storage.get(report_id)


# ==================== Dependencies ====================

def get_pdf_generator() -> PDFReportGenerator:
    """Dependency: Get PDF generator instance."""
    return PDFReportGenerator()


def get_excel_generator() -> ExcelReportGenerator:
    """Dependency: Get Excel generator instance."""
    return ExcelReportGenerator()


# ==================== Helper Functions ====================

def get_analysis_data(analysis_id: str) -> Dict[str, Any]:
    """Fetch carbon analysis data by ID.

    In production, this would query the database.
    For now, returns mock data.
    """
    # TODO: Replace with actual database query
    # from boq.db_sync import get_db
    # analysis = db.query(CarbonAnalysis).filter_by(id=analysis_id).first()

    logger.warning(f"Using mock data for analysis: {analysis_id}")

    return {
        "analysis_id": analysis_id,
        "project_name": "Sample Construction Project",
        "boq_filename": "sample_boq.xlsx",
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
            {
                "line_number": "04.01.003",
                "description_th": "ปูนซีเมนต์ปอร์ตแลนด์ ตราช้าง",
                "description_en": "Portland cement Chang brand",
                "quantity": 1500.0,
                "unit": "ถุง",
                "carbon": 10875.0,
                "percentage": 8.7,
                "match_classification": "auto_matched"
            },
            {
                "line_number": "05.03.004",
                "description_th": "กระเบื้องดินเผา 6x25 ซม.",
                "description_en": "Terracotta tile 6x25 cm",
                "quantity": 2000.0,
                "unit": "ตร.ม.",
                "carbon": 8000.0,
                "percentage": 6.4,
                "match_classification": "review_required"
            },
        ],
        "statistics": {
            "auto_matched": 38,
            "review_required": 4,
            "rejected": 3,
            "auto_match_rate": 84.4
        }
    }


def get_audit_trail(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Fetch audit trail for analysis.

    In production, this would query the audit trail table.
    """
    # TODO: Replace with actual database query
    logger.warning(f"Using mock audit trail for analysis: {analysis_id}")

    return {
        "metadata": {
            "analysis_id": analysis_id,
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


# ==================== Endpoints ====================

@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    pdf_generator: PDFReportGenerator = Depends(get_pdf_generator),
    excel_generator: ExcelReportGenerator = Depends(get_excel_generator)
) -> ReportGenerationResponse:
    """
    Generate carbon analysis report (PDF and/or Excel).

    Supports:
    - Executive summary (PDF)
    - Detailed technical report (PDF)
    - Multi-sheet Excel workbook
    - Bilingual (Thai/English)
    - Audit trail inclusion

    Example:
        curl -X POST "http://localhost:8000/api/v1/reports/generate" \\
             -H "Content-Type: application/json" \\
             -d '{
               "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
               "report_type": "both",
               "language": "th",
               "include_audit_trail": true
             }'
    """
    try:
        # Generate report ID
        report_id = str(uuid.uuid4())

        logger.info(f"Generating report: {report_id} for analysis: {request.analysis_id}")

        # Fetch analysis data
        analysis_data = get_analysis_data(request.analysis_id)

        # Override project name if provided
        if request.project_name:
            analysis_data["project_name"] = request.project_name

        # Fetch audit trail if requested
        audit_trail = None
        if request.include_audit_trail:
            audit_trail = get_audit_trail(request.analysis_id)

        # Create temporary directory for reports
        temp_dir = Path(tempfile.gettempdir()) / "carbon_reports" / report_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize response
        response_data = {
            "report_id": report_id,
            "analysis_id": request.analysis_id,
            "report_type": request.report_type,
            "language": request.language,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "pdf_url": None,
            "excel_url": None,
            "error_message": None
        }

        # Generate PDF report
        if request.report_type in ["pdf", "both"]:
            try:
                pdf_path = temp_dir / f"carbon_report_{request.language}.pdf"

                if request.include_audit_trail:
                    pdf_bytes = pdf_generator.generate_detailed_report(
                        data=analysis_data,
                        audit_trail=audit_trail,
                        output_path=pdf_path,
                        language=request.language
                    )
                else:
                    pdf_bytes = pdf_generator.generate_executive_summary(
                        data=analysis_data,
                        output_path=pdf_path,
                        language=request.language
                    )

                # In production, upload to cloud storage (S3, GCS, etc.)
                response_data["pdf_url"] = f"/api/v1/reports/{report_id}/download/pdf"
                logger.info(f"PDF report generated: {pdf_path}")

            except Exception as e:
                logger.error(f"PDF generation failed: {e}", exc_info=True)
                response_data["status"] = "failed"
                response_data["error_message"] = f"PDF generation failed: {str(e)}"

        # Generate Excel report
        if request.report_type in ["excel", "both"]:
            try:
                excel_path = temp_dir / f"carbon_report.xlsx"

                excel_bytes = excel_generator.generate_report(
                    data=analysis_data,
                    audit_trail=audit_trail if request.include_audit_trail else None,
                    output_path=excel_path
                )

                # In production, upload to cloud storage
                response_data["excel_url"] = f"/api/v1/reports/{report_id}/download/excel"
                logger.info(f"Excel report generated: {excel_path}")

            except Exception as e:
                logger.error(f"Excel generation failed: {e}", exc_info=True)
                response_data["status"] = "failed"
                response_data["error_message"] = f"Excel generation failed: {str(e)}"

        # Mark completion time
        response_data["completed_at"] = datetime.now().isoformat()

        # Store report metadata
        store_report(report_id, response_data)

        logger.info(f"Report generation complete: {report_id}")

        return ReportGenerationResponse(**response_data)

    except Exception as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "REPORT_GENERATION_ERROR",
                "message_en": f"Report generation failed: {str(e)}",
                "message_th": f"การสร้างรายงานล้มเหลว: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/{report_id}")
async def get_report_status(report_id: str) -> JSONResponse:
    """
    Get report generation status and metadata.

    Returns:
    - Report generation status
    - Download URLs (if completed)
    - Error message (if failed)

    Example:
        curl "http://localhost:8000/api/v1/reports/550e8400-e29b-41d4-a716-446655440000"
    """
    report = get_report(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "REPORT_NOT_FOUND",
                "message_en": f"Report not found: {report_id}",
                "message_th": f"ไม่พบรายงาน: {report_id}",
                "timestamp": datetime.now().isoformat()
            }
        )

    return JSONResponse(content=report)


@router.get("/{report_id}/download/{file_type}")
async def download_report(report_id: str, file_type: str) -> StreamingResponse:
    """
    Download generated report file.

    Args:
        report_id: Report UUID
        file_type: 'pdf' or 'excel'

    Returns:
        Report file as streaming response

    Example:
        curl "http://localhost:8000/api/v1/reports/{id}/download/pdf" -o report.pdf
    """
    report = get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Report not ready. Status: {report['status']}"
        )

    # Get report file path
    temp_dir = Path(tempfile.gettempdir()) / "carbon_reports" / report_id

    if file_type == "pdf":
        language = report.get("language", "en")
        file_path = temp_dir / f"carbon_report_{language}.pdf"
        media_type = "application/pdf"
        filename = f"carbon_report_{report['analysis_id']}.pdf"
    elif file_type == "excel":
        file_path = temp_dir / "carbon_report.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"carbon_report_{report['analysis_id']}.xlsx"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    # Stream file
    def file_iterator():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(
        file_iterator(),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

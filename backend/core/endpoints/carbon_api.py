"""
Carbon Calculation API Endpoints.

Provides:
- Carbon footprint calculation
- Audit trail retrieval
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Lazy import to avoid dependency loading at module import time
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/carbon", tags=["Carbon"])


# ==================== Request/Response Models ====================

class CarbonCalculationRequest(BaseModel):
    """Request model for carbon calculation."""
    file_id: str = Field(description="BOQ file ID from upload")
    tgo_version: str = Field(default="2026-03", description="TGO database version")
    language: str = Field(default="th", description="Language for material matching")
    uploaded_by: Optional[str] = Field(default=None, description="User identifier")


# ==================== Dependency Injection ====================

def get_carbon_pipeline():
    """Dependency: Get carbon calculation pipeline instance."""
    # Import here to avoid circular dependencies and load dependencies lazily
    from boq.carbon_pipeline import CarbonCalculationPipeline

    try:
        from core.knowledge_graph.graphdb_client import get_graphdb_client
        graphdb_client = get_graphdb_client()
    except Exception as e:
        logger.warning(f"GraphDB client not available: {e}")
        graphdb_client = None

    try:
        from lca.carbon_calculator import CarbonCalculator
        carbon_calculator = CarbonCalculator()
    except Exception as e:
        logger.warning(f"Carbon calculator not available: {e}")
        carbon_calculator = None

    return CarbonCalculationPipeline(
        graphdb_client=graphdb_client,
        carbon_calculator=carbon_calculator
    )


# ==================== Endpoints ====================

@router.post("/calculate")
async def calculate_carbon(
    request: CarbonCalculationRequest,
    pipeline = Depends(get_carbon_pipeline)
) -> JSONResponse:
    """
    Calculate carbon footprint for BOQ.

    Complete pipeline:
    1. Parse BOQ (cached if available)
    2. Match materials to TGO database
    3. Query emission factors
    4. Calculate carbon using Brightway2
    5. Generate audit trail
    6. Return results with breakdown

    Returns:
    - analysis_id: UUID for audit trail retrieval
    - total_carbon: Total kgCO2e
    - breakdown: Per-material carbon contribution
    - statistics: Matching and calculation stats

    Example:
        curl -X POST "http://localhost:8000/api/carbon/calculate" \\
             -H "Content-Type: application/json" \\
             -d '{
               "file_id": "abc123...",
               "tgo_version": "2026-03",
               "language": "th"
             }'
    """
    try:
        # Find uploaded file
        temp_dir = Path(tempfile.gettempdir()) / "boq_uploads"
        uploaded_files = list(temp_dir.glob(f"{request.file_id}.*"))

        if not uploaded_files:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_type": "FILE_NOT_FOUND",
                    "message_en": f"BOQ file not found: {request.file_id}",
                    "message_th": f"ไม่พบไฟล์ BOQ: {request.file_id}",
                    "timestamp": datetime.now().isoformat()
                }
            )

        file_path = str(uploaded_files[0])

        # Execute carbon calculation pipeline
        logger.info(f"Starting carbon calculation for: {request.file_id}")
        result = pipeline.calculate_boq_carbon(
            boq_file_path=file_path,
            uploaded_by=request.uploaded_by,
            language=request.language
        )

        logger.info(f"Carbon calculation complete: {result['total_carbon']} kgCO2e")

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except ValueError as e:
        # BOQ parsing or validation error
        logger.error(f"Calculation validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "VALIDATION_ERROR",
                "message_en": str(e),
                "message_th": f"ข้อผิดพลาดในการตรวจสอบ: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Calculation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "CALCULATION_ERROR",
                "message_en": f"Carbon calculation failed: {str(e)}",
                "message_th": f"การคำนวณคาร์บอนล้มเหลว: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/audit/{analysis_id}")
async def get_audit_trail(
    analysis_id: str,
    pipeline = Depends(get_carbon_pipeline)
) -> JSONResponse:
    """
    Retrieve complete calculation audit trail.

    Returns:
    - Input BOQ file metadata
    - All material calculations
    - Emission factors used
    - Calculation formulas
    - Total results

    For consultant review and certification body submission.

    Example:
        curl "http://localhost:8000/api/carbon/audit/550e8400-e29b-41d4-a716-446655440000"
    """
    try:
        logger.info(f"Retrieving audit trail: {analysis_id}")

        audit = pipeline.get_audit_trail(analysis_id)

        return JSONResponse(content=audit)

    except ValueError:
        # Audit not found
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "AUDIT_NOT_FOUND",
                "message_en": f"Audit trail not found: {analysis_id}",
                "message_th": f"ไม่พบบันทึกการตรวจสอบ: {analysis_id}",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Audit retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "AUDIT_ERROR",
                "message_en": f"Failed to retrieve audit trail: {str(e)}",
                "message_th": f"ดึงบันทึกการตรวจสอบล้มเหลว: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

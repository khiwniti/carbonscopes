"""
BOQ (Bill of Quantities) API Endpoints.

Provides:
- BOQ file upload
- BOQ parsing
- Material extraction
"""

import logging
import hashlib
import tempfile
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from boq.parser import parse_boq
from boq.cache import get_cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/boq", tags=["BOQ"])


# ==================== Request/Response Models ====================

class BOQUploadResponse(BaseModel):
    """Response model for BOQ upload."""
    file_id: str = Field(description="SHA256 hash of uploaded file")
    filename: str
    size_bytes: int
    status: str = Field(description="uploaded, processing, or error")
    message_en: Optional[str] = None
    message_th: Optional[str] = None


class BOQParseRequest(BaseModel):
    """Request model for BOQ parsing."""
    file_id: str = Field(description="File ID from upload response")
    language: str = Field(default="th", description="Language for parsing (th or en)")


class ErrorResponse(BaseModel):
    """Bilingual error response model."""
    error_type: str
    message_en: str
    message_th: str
    details: Optional[dict] = None
    timestamp: str


# ==================== Endpoints ====================

@router.post("/upload", response_model=BOQUploadResponse)
async def upload_boq(
    file: UploadFile = File(..., description="BOQ Excel file (.xlsx or .xls)")
) -> BOQUploadResponse:
    """
    Upload Thai BOQ Excel file.

    Validates:
    - File format (.xlsx, .xls only)
    - File size (<50MB)
    - File is not corrupted

    Returns:
    - file_id: SHA256 hash for subsequent operations
    - filename: Original filename
    - size_bytes: File size

    Example:
        curl -X POST "http://localhost:8000/api/boq/upload" \\
             -F "file=@project-boq.xlsx"
    """
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error_type="INVALID_FILENAME",
                    message_en="Filename is missing",
                    message_th="ไม่มีชื่อไฟล์",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.xlsx', '.xls']:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error_type="INVALID_FILE_FORMAT",
                    message_en=f"Invalid file format: {file_ext}. Must be .xlsx or .xls",
                    message_th=f"รูปแบบไฟล์ไม่ถูกต้อง: {file_ext} ต้องเป็น .xlsx หรือ .xls",
                    details={"allowed_formats": [".xlsx", ".xls"]},
                    timestamp=datetime.now().isoformat()
                ).dict()
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size (<50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=ErrorResponse(
                    error_type="FILE_TOO_LARGE",
                    message_en=f"File too large: {file_size / 1024 / 1024:.2f}MB. Maximum: 50MB",
                    message_th=f"ไฟล์ใหญ่เกินไป: {file_size / 1024 / 1024:.2f}MB สูงสุด: 50MB",
                    details={"size_bytes": file_size, "max_size_bytes": MAX_FILE_SIZE},
                    timestamp=datetime.now().isoformat()
                ).dict()
            )

        # Generate file hash (for caching and identification)
        file_id = hashlib.sha256(content).hexdigest()

        # Save to temporary storage
        temp_dir = Path(tempfile.gettempdir()) / "boq_uploads"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / f"{file_id}{file_ext}"

        with open(temp_path, 'wb') as f:
            f.write(content)

        logger.info(f"BOQ file uploaded: {file.filename} ({file_size} bytes) -> {file_id}")

        return BOQUploadResponse(
            file_id=file_id,
            filename=file.filename,
            size_bytes=file_size,
            status="uploaded",
            message_en="File uploaded successfully",
            message_th="อัปโหลดไฟล์สำเร็จ"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_type="UPLOAD_ERROR",
                message_en=f"Upload failed: {str(e)}",
                message_th=f"อัปโหลดล้มเหลว: {str(e)}",
                timestamp=datetime.now().isoformat()
            ).dict()
        )


@router.post("/parse")
async def parse_boq_file(request: BOQParseRequest) -> JSONResponse:
    """
    Parse uploaded BOQ file.

    Extracts:
    - Material descriptions (Thai + English)
    - Quantities with units
    - Line numbers

    Returns:
    - Parsed material list
    - Parsing metadata (success rate, error count)
    - Bilingual error messages for parsing failures

    Example:
        curl -X POST "http://localhost:8000/api/boq/parse" \\
             -H "Content-Type: application/json" \\
             -d '{"file_id": "abc123...", "language": "th"}'
    """
    try:
        # Check cache first
        cache = get_cache_manager()
        cached_parsed = cache.get_parsed_boq(request.file_id)

        if cached_parsed:
            logger.info(f"Cache hit: Parsed BOQ for file {request.file_id}")
            return JSONResponse(content=cached_parsed)

        # Find uploaded file
        temp_dir = Path(tempfile.gettempdir()) / "boq_uploads"
        uploaded_files = list(temp_dir.glob(f"{request.file_id}.*"))

        if not uploaded_files:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error_type="FILE_NOT_FOUND",
                    message_en=f"BOQ file not found: {request.file_id}",
                    message_th=f"ไม่พบไฟล์ BOQ: {request.file_id}",
                    details={"file_id": request.file_id},
                    timestamp=datetime.now().isoformat()
                ).dict()
            )

        file_path = str(uploaded_files[0])

        # Parse BOQ
        logger.info(f"Parsing BOQ file: {file_path}")
        result = parse_boq(file_path)

        # Convert to dictionary for JSON response
        result_dict = {
            "file_id": result.file_id,
            "filename": result.filename,
            "status": result.status,
            "materials": [
                {
                    "line_number": m.line_number,
                    "description_th": m.description_th,
                    "description_en": m.description_en,
                    "quantity": str(m.quantity),
                    "unit": m.unit,
                    "unit_raw": m.unit_raw,
                    "conversion_factor": str(m.conversion_factor)
                }
                for m in result.materials
            ],
            "metadata": result.metadata,
            "errors": [
                {
                    "error_type": e.get("error_type"),
                    "line_number": e.get("line_number"),
                    "column": e.get("column"),
                    "message_en": e.get("message_en"),
                    "message_th": e.get("message_th"),
                    "suggestion": e.get("suggestion"),
                    "timestamp": e.get("timestamp")
                }
                for e in result.errors
            ]
        }

        # Cache parsed result
        cache.cache_parsed_boq(request.file_id, result_dict)

        logger.info(f"BOQ parsed: {len(result.materials)} materials (success rate: {result.metadata['success_rate']}%)")

        return JSONResponse(content=result_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parsing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_type="PARSE_ERROR",
                message_en=f"Parsing failed: {str(e)}",
                message_th=f"การแปลงล้มเหลว: {str(e)}",
                timestamp=datetime.now().isoformat()
            ).dict()
        )

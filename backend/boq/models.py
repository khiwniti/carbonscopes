"""
BOQ Data Models.

Pydantic models for Bill of Quantities (BOQ) parsing results.
All quantities use Decimal for deterministic calculations (Brightway2 compatibility).
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


class BOQMaterial(BaseModel):
    """Material entry parsed from BOQ Excel file."""

    line_number: int = Field(description="Line number in source BOQ file")
    description_th: str = Field(description="Thai material description")
    description_en: Optional[str] = Field(default=None, description="English material description")
    quantity: Decimal = Field(description="Material quantity (exact decimal)")
    unit: str = Field(description="Normalized unit (m³, kg, m², etc.)")
    unit_raw: str = Field(description="Original Thai unit from BOQ")
    conversion_factor: Decimal = Field(default=Decimal("1.0"), description="Conversion from raw to normalized unit")


class BOQParseResult(BaseModel):
    """Complete BOQ parsing result with materials, metadata, and errors."""

    file_id: str = Field(description="SHA256 hash of file content")
    filename: str
    status: str = Field(description="parsed, partial, or failed")
    materials: list[BOQMaterial]
    metadata: dict = Field(description="total_lines, parsed_lines, success_rate")
    errors: list[dict] = Field(default_factory=list, description="Parsing errors")


class BOQError(BaseModel):
    """Bilingual error message for BOQ parsing failures."""

    error_type: str = Field(description="PARSE_ERROR, UNIT_ERROR, FORMAT_ERROR")
    line_number: Optional[int] = None
    column: Optional[str] = None
    message_en: str
    message_th: str
    suggestion: Optional[str] = None
    timestamp: str

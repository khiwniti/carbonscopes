"""
Carbon Calculation Audit Trail.

Stores complete calculation transparency for consultant review and certification bodies.
Provides 5-year retention for compliance.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

# Create Base for SQLAlchemy models
Base = declarative_base()


class CalculationAudit(Base):
    """
    Main audit record for a complete BOQ carbon calculation.

    Tracks:
    - Input BOQ file metadata
    - Calculation parameters (TGO version, method)
    - Summary results (total carbon, material count)
    - Calculation timestamp
    """

    __tablename__ = "calculation_audits"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Input BOQ tracking
    boq_file_id = Column(String(64), nullable=False, index=True)  # SHA256 hash
    boq_filename = Column(String(255), nullable=False)
    uploaded_by = Column(String(255), nullable=True)  # User email/ID
    file_size_bytes = Column(Integer, nullable=True)

    # Calculation parameters
    tgo_version = Column(String(50), nullable=False, index=True)  # e.g., "2026-03"
    calculation_mode = Column(String(50), default="deterministic")
    brightway_version = Column(String(50), nullable=True)

    # Summary results (stored as Decimal for precision)
    total_carbon_kgco2e = Column(Numeric(precision=20, scale=6), nullable=False)
    material_count = Column(Integer, nullable=False)
    matched_count = Column(Integer, nullable=False)
    auto_matched_count = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    material_calculations = relationship("MaterialCalculationAudit", back_populates="audit", cascade="all, delete-orphan")

    # Indexes for query performance
    __table_args__ = (
        Index('idx_audit_created_at', 'created_at'),
        Index('idx_audit_boq_file', 'boq_file_id'),
        Index('idx_audit_tgo_version', 'tgo_version'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "analysis_id": str(self.id),
            "boq_file_id": self.boq_file_id,
            "boq_filename": self.boq_filename,
            "uploaded_by": self.uploaded_by,
            "tgo_version": self.tgo_version,
            "calculation_mode": self.calculation_mode,
            "total_carbon": str(self.total_carbon_kgco2e),
            "unit": "kgCO2e",
            "material_count": self.material_count,
            "matched_count": self.matched_count,
            "auto_matched_count": self.auto_matched_count,
            "timestamp": self.created_at.isoformat(),
        }


class MaterialCalculationAudit(Base):
    """
    Detailed audit record for individual material calculations.

    Stores:
    - Material description (Thai + English)
    - Matched TGO material ID and confidence
    - Emission factor used (value, unit, version, date)
    - Calculation steps (quantity × emission factor = result)
    - Final carbon result for this material
    """

    __tablename__ = "material_calculation_audits"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to main audit
    audit_id = Column(UUID(as_uuid=True), ForeignKey('calculation_audits.id'), nullable=False, index=True)

    # BOQ material data
    boq_line_number = Column(Integer, nullable=False)
    description_th = Column(Text, nullable=False)
    description_en = Column(Text, nullable=True)
    quantity = Column(Numeric(precision=20, scale=6), nullable=False)
    unit = Column(String(50), nullable=False)

    # Matched TGO material
    tgo_material_id = Column(String(255), nullable=True)  # NULL if no match
    tgo_material_label = Column(String(255), nullable=True)
    match_confidence = Column(Numeric(precision=5, scale=3), nullable=True)
    match_classification = Column(String(50), nullable=True)  # auto_match, review_required, rejected

    # Emission factor used
    emission_factor_value = Column(Numeric(precision=20, scale=6), nullable=True)
    emission_factor_unit = Column(String(50), nullable=True)
    emission_factor_version = Column(String(50), nullable=True)
    emission_factor_effective_date = Column(DateTime(timezone=True), nullable=True)

    # Calculation result
    carbon_result_kgco2e = Column(Numeric(precision=20, scale=6), nullable=True)
    calculation_formula = Column(Text, nullable=True)  # Human-readable formula string

    # Relationship
    audit = relationship("CalculationAudit", back_populates="material_calculations")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "line_number": self.boq_line_number,
            "description_th": self.description_th,
            "description_en": self.description_en,
            "quantity": str(self.quantity),
            "unit": self.unit,
            "tgo_match": {
                "material_id": self.tgo_material_id,
                "label": self.tgo_material_label,
                "confidence": float(self.match_confidence) if self.match_confidence else None,
                "classification": self.match_classification,
            },
            "emission_factor": {
                "value": str(self.emission_factor_value) if self.emission_factor_value else None,
                "unit": self.emission_factor_unit,
                "version": self.emission_factor_version,
                "effective_date": self.emission_factor_effective_date.isoformat() if self.emission_factor_effective_date else None,
            },
            "calculation": {
                "formula": self.calculation_formula,
                "result": str(self.carbon_result_kgco2e) if self.carbon_result_kgco2e else None,
                "unit": "kgCO2e"
            }
        }


# Database migration required:
# alembic revision --autogenerate -m "Add calculation audit tables"
# alembic upgrade head

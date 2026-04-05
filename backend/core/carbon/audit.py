"""Audit trail model for carbon calculations.

Stores calculation metadata for consultant transparency.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4


class CalculationStep(BaseModel):
    step_name: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditTrail(BaseModel):
    calculation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database_version: str
    materials: List[Dict]
    steps: List[CalculationStep]
    total_carbon: Decimal
    deterministic: bool
    precision: str = "Decimal(28)"

"""
Data models for the audit trail system.

Defines enums, pydantic models, and database schemas for audit events.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Any, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    """Types of events that can be audited."""

    DATA_CHANGE = "DATA_CHANGE"
    LCA_CALCULATION = "LCA_CALCULATION"
    CERTIFICATION_ASSESSMENT = "CERTIFICATION_ASSESSMENT"
    QUERY = "QUERY"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    USER_ACTION = "USER_ACTION"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class Operation(str, Enum):
    """CRUD and specialized operations."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CALCULATE = "CALCULATE"
    ASSESS = "ASSESS"
    QUERY = "QUERY"
    EXECUTE = "EXECUTE"


class AuditEvent(BaseModel):
    """
    Core audit event model.

    Captures a single auditable event with full context.
    """

    audit_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: EventType
    user_id: Optional[str] = None
    operation: Operation
    resource_type: str
    resource_id: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }
        use_enum_values = True

    @field_validator('metadata', 'before_state', 'after_state', mode='before')
    @classmethod
    def validate_json_serializable(cls, v):
        """Ensure all dict values are JSON-serializable."""
        if v is None:
            return v

        def convert_value(val):
            if isinstance(val, Decimal):
                return str(val)
            elif isinstance(val, datetime):
                return val.isoformat()
            elif isinstance(val, UUID):
                return str(val)
            elif isinstance(val, dict):
                return {k: convert_value(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [convert_value(item) for item in val]
            return val

        return {k: convert_value(v) for k, v in v.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with JSON-serializable values."""
        return {
            "audit_id": str(self.audit_id),
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type if isinstance(self.event_type, str) else self.event_type.value,
            "user_id": self.user_id,
            "operation": self.operation if isinstance(self.operation, str) else self.operation.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "metadata": self.metadata,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
        }


class AuditQuery(BaseModel):
    """
    Query parameters for searching audit logs.
    """

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[EventType] = None
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    operation: Optional[Operation] = None
    success: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)

    class Config:
        use_enum_values = True


class AuditQueryResult(BaseModel):
    """
    Result of an audit query.
    """

    events: List[AuditEvent]
    total_count: int
    query: AuditQuery

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ResourceHistory(BaseModel):
    """
    Complete history of a specific resource.
    """

    resource_type: str
    resource_id: str
    events: List[AuditEvent]
    first_event: Optional[datetime] = None
    last_event: Optional[datetime] = None
    event_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class AuditStatistics(BaseModel):
    """
    Aggregate statistics for audit logs.
    """

    total_events: int
    events_by_type: Dict[str, int]
    events_by_operation: Dict[str, int]
    success_rate: float
    time_range: Optional[tuple[datetime, datetime]] = None
    most_active_users: List[tuple[str, int]] = Field(default_factory=list)
    most_modified_resources: List[tuple[str, int]] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

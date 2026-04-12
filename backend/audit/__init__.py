"""
Comprehensive audit trail system for carbonscope BIM agent.

This module provides a robust audit logging system that tracks:
- TGO data version changes
- LCA calculations performed
- EDGE certification assessments
- TREES certification assessments
- GraphDB queries executed
- User actions
- System configuration changes

Usage:
    from audit import AuditLogger, EventType, Operation

    audit = AuditLogger()
    audit.log_event(
        event_type=EventType.LCA_CALCULATION,
        operation=Operation.CALCULATE,
        resource_type="Project",
        resource_id="project-123",
        after_state={"total_carbon": 1500},
        metadata={"materials_count": 5}
    )
"""

from audit.audit_logger import AuditLogger
from audit.models import (
    EventType,
    Operation,
    AuditEvent,
    AuditQuery,
)
from audit.decorators import audit_log

__all__ = [
    "AuditLogger",
    "EventType",
    "Operation",
    "AuditEvent",
    "AuditQuery",
    "audit_log",
]

__version__ = "1.0.0"

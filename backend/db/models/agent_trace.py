"""AgentTrace database model for agent execution tracing and observability.

This model stores complete execution traces for all agent actions,
enabling debugging, auditing, and performance analysis.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AgentTrace(Base):
    """Agent execution trace for debugging and auditing.

    Stores complete state snapshots and timing information for every
    agent execution, enabling full observability of multi-agent workflows.

    Attributes:
        trace_id: Unique identifier for this trace
        thread_id: Conversation/session thread ID
        agent_name: Name of the agent that executed
        action: User query or action that triggered execution
        input_state: Full input state snapshot (JSON)
        output_state: Full output state snapshot (JSON)
        start_time: Execution start timestamp
        end_time: Execution end timestamp
        duration_ms: Execution duration in milliseconds
        user_id: User who triggered the action
        boq_id: BOQ ID if applicable
        error: Error message if execution failed (nullable)
        created_at: Trace creation timestamp
    """

    __tablename__ = "agent_traces"

    trace_id = Column(String, primary_key=True, doc="Unique trace identifier")
    thread_id = Column(String, index=True, doc="Conversation thread ID")
    agent_name = Column(String, index=True, doc="Agent name")
    action = Column(String, doc="User query or action")
    input_state = Column(JSON, doc="Input state snapshot")
    output_state = Column(JSON, doc="Output state snapshot")
    start_time = Column(DateTime, doc="Execution start time")
    end_time = Column(DateTime, doc="Execution end time")
    duration_ms = Column(Integer, doc="Execution duration in milliseconds")
    user_id = Column(String, index=True, doc="User ID")
    boq_id = Column(String, index=True, nullable=True, doc="BOQ ID if applicable")
    error = Column(Text, nullable=True, doc="Error message if failed")
    created_at = Column(DateTime, default=datetime.now, doc="Trace creation timestamp")

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_thread_created", "thread_id", "created_at"),
        Index("idx_agent_created", "agent_name", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
    )

    def __repr__(self):
        """String representation for debugging."""
        status = "error" if self.error else "success"
        return (
            f"<AgentTrace(trace_id={self.trace_id}, "
            f"agent={self.agent_name}, "
            f"status={status}, "
            f"duration={self.duration_ms}ms)>"
        )

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "thread_id": self.thread_id,
            "agent_name": self.agent_name,
            "action": self.action,
            "input_state": self.input_state,
            "output_state": self.output_state,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "user_id": self.user_id,
            "boq_id": self.boq_id,
            "error": self.error,
            "status": "error" if self.error else "success",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

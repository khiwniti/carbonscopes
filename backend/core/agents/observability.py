"""Observability infrastructure for multi-agent system.

This module provides:
1. Structured logging for agent actions and decisions
2. Trace storage in PostgreSQL for debugging
3. Prometheus metrics for coordination health monitoring
"""

import logging
import time
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Optional
from decimal import Decimal

# Import structlog if available, fallback to standard logging
try:
    import structlog
    logger = structlog.get_logger()
    HAS_STRUCTLOG = True
except ImportError:
    logger = logging.getLogger(__name__)
    HAS_STRUCTLOG = False

# Import Prometheus client if available
try:
    from prometheus_client import Counter, Histogram, Gauge
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    # Define dummy classes if Prometheus not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def inc(self):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def observe(self, value):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def inc(self):
            pass
        def dec(self):
            pass
        def set(self, value):
            pass


# Prometheus metrics
agent_invocations = Counter(
    "agent_invocations_total",
    "Total agent invocations",
    ["agent_name", "status"]
)

agent_duration = Histogram(
    "agent_duration_seconds",
    "Agent execution duration in seconds",
    ["agent_name"]
)

agent_errors = Counter(
    "agent_errors_total",
    "Total agent errors",
    ["agent_name", "error_type"]
)

coordination_failures = Counter(
    "coordination_failures_total",
    "Multi-agent coordination failures"
)

handoff_latency = Histogram(
    "handoff_latency_seconds",
    "Latency for agent handoffs",
    ["from_agent", "to_agent"]
)

active_agents = Gauge(
    "active_agents",
    "Number of currently active agents"
)


class AgentLogger:
    """Structured logger for agent actions and decisions.

    Provides methods for logging:
    - Agent actions with structured data
    - Routing decisions
    - Agent errors with context
    - Trace storage in PostgreSQL
    """

    def __init__(self, db_session_factory=None):
        """Initialize AgentLogger.

        Args:
            db_session_factory: Optional factory function to get database session.
                              If None, trace storage will be skipped.
        """
        self.db_session_factory = db_session_factory

    def log_agent_action(
        self,
        agent_name: str,
        action: str,
        input_state: Dict[str, Any],
        output_state: Dict[str, Any],
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log agent action with structured data.

        Args:
            agent_name: Name of the agent
            action: User query or action description
            input_state: Input state dictionary
            output_state: Output state dictionary
            duration_ms: Execution duration in milliseconds
            metadata: Optional additional metadata
        """
        log_data = {
            "event": "agent_action",
            "agent_name": agent_name,
            "action": action,
            "input_keys": list(input_state.keys()),
            "output_keys": list(output_state.keys()),
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
        }

        if metadata:
            log_data.update(metadata)

        if HAS_STRUCTLOG:
            logger.info(**log_data)
        else:
            logger.info(f"Agent action: {log_data}")

    def log_routing_decision(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        query: str,
        agent_history: list
    ):
        """Log supervisor routing decision.

        Args:
            from_agent: Source agent (typically "supervisor")
            to_agent: Target agent
            reason: Routing reason/rationale
            query: User query that triggered routing
            agent_history: List of agents in execution chain
        """
        log_data = {
            "event": "routing_decision",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "query": query,
            "agent_history": agent_history,
            "timestamp": datetime.now().isoformat(),
        }

        if HAS_STRUCTLOG:
            logger.info(**log_data)
        else:
            logger.info(f"Routing: {from_agent} -> {to_agent}: {reason}")

    def log_agent_error(
        self,
        agent_name: str,
        error: Exception,
        state: Dict[str, Any],
        retry_count: int = 0
    ):
        """Log agent error with context.

        Args:
            agent_name: Name of the agent
            error: Exception that occurred
            state: Agent state at time of error
            retry_count: Number of retries attempted
        """
        log_data = {
            "event": "agent_error",
            "agent_name": agent_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "state_keys": list(state.keys()),
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
        }

        if HAS_STRUCTLOG:
            logger.error(**log_data)
        else:
            logger.error(
                f"Agent error in {agent_name}: {type(error).__name__}: {str(error)}"
            )

    async def store_trace(
        self,
        trace_id: str,
        thread_id: str,
        agent_name: str,
        action: str,
        input_state: Dict[str, Any],
        output_state: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        user_id: str,
        boq_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Store agent trace in PostgreSQL.

        Args:
            trace_id: Unique trace identifier
            thread_id: Conversation thread ID
            agent_name: Name of the agent
            action: User query or action
            input_state: Input state snapshot
            output_state: Output state snapshot
            start_time: Execution start time
            end_time: Execution end time
            user_id: User ID
            boq_id: BOQ ID if applicable
            error: Error message if execution failed
        """
        if not self.db_session_factory:
            logger.debug("No database session factory - skipping trace storage")
            return

        try:
            from suna.backend.db.models.agent_trace import AgentTrace

            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Serialize state (convert Decimals to float for JSON)
            input_serialized = self._serialize_state(input_state)
            output_serialized = self._serialize_state(output_state)

            trace = AgentTrace(
                trace_id=trace_id,
                thread_id=thread_id,
                agent_name=agent_name,
                action=action,
                input_state=input_serialized,
                output_state=output_serialized,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                user_id=user_id,
                boq_id=boq_id,
                error=error
            )

            # Get database session and store trace
            session = self.db_session_factory()
            session.add(trace)
            session.commit()

            logger.debug(f"Stored trace {trace_id} for agent {agent_name}")

        except Exception as e:
            logger.error(f"Failed to store trace: {str(e)}", exc_info=True)

    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize state for JSON storage.

        Converts Decimal and other non-JSON types to JSON-compatible types.

        Args:
            state: State dictionary

        Returns:
            Serialized state dictionary
        """
        serialized = {}

        for key, value in state.items():
            if isinstance(value, Decimal):
                serialized[key] = float(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                serialized[key] = self._serialize_value(value)
            else:
                serialized[key] = value

        return serialized

    def _serialize_value(self, value):
        """Recursively serialize values."""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        else:
            return value


async def execute_agent_with_observability(
    agent,
    state: Dict[str, Any],
    logger_instance: AgentLogger,
    thread_id: str = "unknown",
    user_id: str = "unknown",
    boq_id: Optional[str] = None
) -> Dict[str, Any]:
    """Execute agent with full observability instrumentation.

    This wrapper function:
    1. Records execution metrics (Prometheus)
    2. Logs structured events
    3. Stores execution trace in PostgreSQL
    4. Handles errors gracefully

    Args:
        agent: Agent instance to execute
        state: AgentState dictionary
        logger_instance: AgentLogger instance
        thread_id: Conversation thread ID
        user_id: User ID
        boq_id: BOQ ID if applicable

    Returns:
        Agent execution result dictionary

    Raises:
        Exception: Re-raises any agent execution errors after logging
    """
    start = time.time()
    trace_id = str(uuid4())
    start_dt = datetime.now()

    try:
        # Increment active agents gauge
        active_agents.inc()

        # Execute agent
        result = await agent.execute(state)

        # Record success metrics
        agent_invocations.labels(
            agent_name=agent.name,
            status="success"
        ).inc()

        # Log action
        duration_ms = (time.time() - start) * 1000
        logger_instance.log_agent_action(
            agent_name=agent.name,
            action=state.get("user_query", ""),
            input_state=state,
            output_state=result,
            duration_ms=duration_ms
        )

        # Store trace
        await logger_instance.store_trace(
            trace_id=trace_id,
            thread_id=thread_id,
            agent_name=agent.name,
            action=state.get("user_query", ""),
            input_state=state,
            output_state=result,
            start_time=start_dt,
            end_time=datetime.now(),
            user_id=user_id,
            boq_id=boq_id
        )

        return result

    except Exception as e:
        # Record error metrics
        agent_invocations.labels(
            agent_name=agent.name,
            status="error"
        ).inc()

        agent_errors.labels(
            agent_name=agent.name,
            error_type=type(e).__name__
        ).inc()

        # Log error
        logger_instance.log_agent_error(agent.name, e, state)

        # Store error trace
        await logger_instance.store_trace(
            trace_id=trace_id,
            thread_id=thread_id,
            agent_name=agent.name,
            action=state.get("user_query", ""),
            input_state=state,
            output_state={},
            start_time=start_dt,
            end_time=datetime.now(),
            user_id=user_id,
            boq_id=boq_id,
            error=str(e)
        )

        # Re-raise error
        raise

    finally:
        # Record duration and decrement active agents
        duration = time.time() - start
        agent_duration.labels(agent_name=agent.name).observe(duration)
        active_agents.dec()

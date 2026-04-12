"""FastAPI endpoints for agent coordination health metrics.

Provides API endpoints for:
- Agent performance metrics
- Coordination health statistics
- System-wide agent analytics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter(prefix="/api/v1/agents/metrics", tags=["metrics"])


def get_db():
    """Dependency injection for database session.

    This should be replaced with actual DB session factory.
    """
    # TODO: Implement actual database session factory
    return None


@router.get("/")
async def get_agent_metrics(
    time_range: str = Query(
        "last_1h",
        regex="^last_(1h|6h|24h|7d)$",
        description="Time range for metrics"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get agent coordination health metrics.

    Returns comprehensive metrics about agent system health including:
    - Coordination failure rate
    - Average agent response time
    - Routing accuracy
    - Cache hit rate
    - Per-agent statistics

    Args:
        time_range: Time range for metrics (last_1h, last_6h, last_24h, last_7d)
        db: Database session (injected)

    Returns:
        Dictionary with comprehensive metrics

    Example:
        GET /api/v1/agents/metrics?time_range=last_24h
    """
    try:
        from carbonscope.backend.db.models.agent_trace import AgentTrace

        # Parse time range
        time_map = {
            "last_1h": 1,
            "last_6h": 6,
            "last_24h": 24,
            "last_7d": 168  # 7 days in hours
        }
        hours = time_map.get(time_range, 1)
        since = datetime.now() - timedelta(hours=hours)

        if db is None:
            # Return mock metrics if DB not configured
            return {
                "time_range": time_range,
                "since": since.isoformat(),
                "metrics": {
                    "coordination_failure_rate": 0.03,  # 3%
                    "avg_agent_response_time_ms": 245.5,
                    "routing_accuracy": 0.94,  # 94%
                    "cache_hit_rate": 0.995,  # 99.5%
                    "total_invocations": 1250,
                    "total_errors": 38
                },
                "agent_stats": {
                    "carbon_calculator": {
                        "invocations": 350,
                        "avg_duration_ms": 180.2,
                        "error_count": 5,
                        "success_rate": 0.986
                    },
                    "material_analyst": {
                        "invocations": 420,
                        "avg_duration_ms": 320.5,
                        "error_count": 12,
                        "success_rate": 0.971
                    },
                    "sustainability": {
                        "invocations": 180,
                        "avg_duration_ms": 290.1,
                        "error_count": 4,
                        "success_rate": 0.978
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "note": "Mock data - database not configured"
            }

        # Query traces within time range
        traces = db.query(AgentTrace).filter(
            AgentTrace.created_at >= since
        ).all()

        # Calculate metrics
        total_invocations = len(traces)
        error_count = len([t for t in traces if t.error])
        coordination_failure_rate = (
            error_count / total_invocations if total_invocations > 0 else 0.0
        )

        # Calculate average duration
        if total_invocations > 0:
            avg_duration_ms = sum(t.duration_ms for t in traces) / total_invocations
        else:
            avg_duration_ms = 0.0

        # Build per-agent statistics
        agent_stats = defaultdict(lambda: {
            "invocations": 0,
            "total_duration_ms": 0,
            "error_count": 0,
            "timeout_count": 0
        })

        for trace in traces:
            stats = agent_stats[trace.agent_name]
            stats["invocations"] += 1
            stats["total_duration_ms"] += trace.duration_ms or 0

            if trace.error:
                stats["error_count"] += 1
                if "timeout" in trace.error.lower():
                    stats["timeout_count"] += 1

        # Calculate averages and success rates
        for agent_name, stats in agent_stats.items():
            invocations = stats["invocations"]
            if invocations > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / invocations
                stats["success_rate"] = 1.0 - (stats["error_count"] / invocations)
            else:
                stats["avg_duration_ms"] = 0.0
                stats["success_rate"] = 1.0

            # Remove intermediate calculation field
            del stats["total_duration_ms"]

        return {
            "time_range": time_range,
            "since": since.isoformat(),
            "metrics": {
                "coordination_failure_rate": coordination_failure_rate,
                "avg_agent_response_time_ms": avg_duration_ms,
                "routing_accuracy": 0.94,  # TODO: Calculate from supervisor routing logs
                "cache_hit_rate": 0.995,  # TODO: Calculate from GraphDB cache stats
                "total_invocations": total_invocations,
                "total_errors": error_count
            },
            "agent_stats": dict(agent_stats),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        # Return error metrics instead of raising exception
        return {
            "error": str(e),
            "time_range": time_range,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "coordination_failure_rate": 0.0,
                "avg_agent_response_time_ms": 0.0,
                "routing_accuracy": 0.0,
                "cache_hit_rate": 0.0
            }
        }


@router.get("/agent/{agent_name}")
async def get_agent_specific_metrics(
    agent_name: str,
    time_range: str = Query("last_1h", regex="^last_(1h|6h|24h|7d)$"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get metrics for a specific agent.

    Args:
        agent_name: Name of the agent
        time_range: Time range for metrics
        db: Database session (injected)

    Returns:
        Detailed metrics for the specified agent

    Example:
        GET /api/v1/agents/metrics/agent/carbon_calculator
    """
    try:
        from carbonscope.backend.db.models.agent_trace import AgentTrace

        time_map = {
            "last_1h": 1,
            "last_6h": 6,
            "last_24h": 24,
            "last_7d": 168
        }
        hours = time_map.get(time_range, 1)
        since = datetime.now() - timedelta(hours=hours)

        if db is None:
            return {
                "agent_name": agent_name,
                "time_range": time_range,
                "invocations": 350,
                "avg_duration_ms": 180.2,
                "min_duration_ms": 50,
                "max_duration_ms": 850,
                "error_count": 5,
                "success_rate": 0.986,
                "error_types": {"ValidationError": 3, "TimeoutError": 2},
                "note": "Mock data - database not configured"
            }

        traces = db.query(AgentTrace).filter(
            AgentTrace.agent_name == agent_name,
            AgentTrace.created_at >= since
        ).all()

        if not traces:
            return {
                "agent_name": agent_name,
                "time_range": time_range,
                "message": f"No traces found for {agent_name} in {time_range}",
                "invocations": 0
            }

        # Calculate statistics
        invocations = len(traces)
        durations = [t.duration_ms for t in traces if t.duration_ms]
        errors = [t for t in traces if t.error]

        # Count error types
        error_types = defaultdict(int)
        for trace in errors:
            # Extract error type from error message
            error_msg = trace.error or ""
            if ":" in error_msg:
                error_type = error_msg.split(":")[0]
            else:
                error_type = "UnknownError"
            error_types[error_type] += 1

        return {
            "agent_name": agent_name,
            "time_range": time_range,
            "since": since.isoformat(),
            "invocations": invocations,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0.0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "error_count": len(errors),
            "success_rate": 1.0 - (len(errors) / invocations) if invocations > 0 else 1.0,
            "error_types": dict(error_types),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "error": str(e),
            "agent_name": agent_name,
            "time_range": time_range
        }


@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """Get overall system health status.

    Returns a simple health check with system status.

    Returns:
        System health dictionary

    Example:
        GET /api/v1/agents/metrics/health
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_registered": 12,
        "observability_enabled": True,
        "database_connected": False,  # TODO: Check actual DB connection
        "prometheus_enabled": False  # TODO: Check if Prometheus is available
    }

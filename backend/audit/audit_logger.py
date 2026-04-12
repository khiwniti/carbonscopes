"""
Core audit logger implementation.

Provides thread-safe, append-only logging to SQLite database with
querying, export, and compliance features.
"""

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

import structlog

from audit.models import (
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    ResourceHistory,
    AuditStatistics,
    EventType,
    Operation,
)

logger = structlog.get_logger(__name__)


class AuditLogger:
    """
    Thread-safe audit logger with SQLite backend.

    Features:
    - Append-only logging (no deletion)
    - Thread-safe operations
    - Query API for compliance reporting
    - Export to JSON/CSV formats
    - Resource history tracking
    - Aggregate statistics

    Args:
        db_path: Path to SQLite database file (default: carbonscope/backend/audit/audit_log.db)
        auto_create_db: Whether to create database if it doesn't exist (default: True)

    Example:
        >>> audit = AuditLogger()
        >>> audit.log_event(
        ...     event_type=EventType.LCA_CALCULATION,
        ...     operation=Operation.CALCULATE,
        ...     resource_type="Project",
        ...     resource_id="proj-123",
        ...     after_state={"total_carbon": 1500.5}
        ... )
    """

    _instance_lock = threading.Lock()
    _instances: Dict[str, "AuditLogger"] = {}

    def __new__(cls, db_path: Optional[Union[str, Path]] = None, **kwargs):
        """
        Implement singleton pattern per database path.

        This ensures only one logger instance per database to avoid
        connection conflicts and maintain thread safety.
        """
        if db_path is None:
            db_path = Path(__file__).parent / "audit_log.db"
        else:
            db_path = Path(db_path)

        db_path_str = str(db_path.absolute())

        with cls._instance_lock:
            if db_path_str not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[db_path_str] = instance
            return cls._instances[db_path_str]

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        auto_create_db: bool = True,
    ):
        """Initialize the audit logger."""
        # Prevent re-initialization
        if hasattr(self, "_initialized"):
            return

        if db_path is None:
            self.db_path = Path(__file__).parent / "audit_log.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        if auto_create_db:
            self._initialize_database()

        self._initialized = True
        logger.info(
            "audit_logger_initialized",
            db_path=str(self.db_path),
            thread_safe=True,
        )

    def _initialize_database(self):
        """Create database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create audit_events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    audit_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    operation TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    before_state TEXT,
                    after_state TEXT,
                    metadata TEXT,
                    success INTEGER NOT NULL DEFAULT 1,
                    error_message TEXT,
                    duration_ms REAL
                )
                """
            )

            # Create indexes for common query patterns
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON audit_events(timestamp)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_event_type
                ON audit_events(event_type)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_resource
                ON audit_events(resource_type, resource_id)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON audit_events(user_id)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_operation
                ON audit_events(operation)
                """
            )

            conn.commit()

            logger.info("audit_database_initialized", db_path=str(self.db_path))

    @contextmanager
    def _get_connection(self):
        """Get a thread-safe database connection."""
        with self._lock:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0,
            )
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    def log_event(
        self,
        event_type: EventType,
        operation: Operation,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> UUID:
        """
        Log an audit event.

        Args:
            event_type: Type of event (DATA_CHANGE, LCA_CALCULATION, etc.)
            operation: Operation performed (CREATE, UPDATE, CALCULATE, etc.)
            resource_type: Type of resource affected (Material, Project, etc.)
            resource_id: Unique identifier of the resource
            user_id: Optional user identifier
            before_state: State before the operation (for updates)
            after_state: State after the operation
            metadata: Additional context information
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            duration_ms: Duration of operation in milliseconds

        Returns:
            UUID of the created audit event

        Example:
            >>> audit.log_event(
            ...     event_type=EventType.LCA_CALCULATION,
            ...     operation=Operation.CALCULATE,
            ...     resource_type="Project",
            ...     resource_id="proj-123",
            ...     after_state={"total_carbon": 1500.5},
            ...     metadata={"materials_count": 5}
            ... )
        """
        event = AuditEvent(
            event_type=event_type,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_events (
                    audit_id, timestamp, event_type, user_id, operation,
                    resource_type, resource_id, before_state, after_state,
                    metadata, success, error_message, duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.audit_id),
                    event.timestamp.isoformat(),
                    event.event_type if isinstance(event.event_type, str) else event.event_type.value,
                    event.user_id,
                    event.operation if isinstance(event.operation, str) else event.operation.value,
                    event.resource_type,
                    event.resource_id,
                    json.dumps(event.before_state) if event.before_state else None,
                    json.dumps(event.after_state) if event.after_state else None,
                    json.dumps(event.metadata) if event.metadata else None,
                    1 if event.success else 0,
                    event.error_message,
                    event.duration_ms,
                ),
            )
            conn.commit()

        logger.info(
            "audit_event_logged",
            audit_id=str(event.audit_id),
            event_type=event_type if isinstance(event_type, str) else event_type.value,
            operation=operation if isinstance(operation, str) else operation.value,
            resource_type=resource_type,
            resource_id=resource_id,
        )

        return event.audit_id

    def query_logs(
        self,
        query: Optional[AuditQuery] = None,
        **kwargs,
    ) -> AuditQueryResult:
        """
        Query audit logs with filtering.

        Args:
            query: AuditQuery object with filter parameters
            **kwargs: Alternative to passing AuditQuery, provide filters as kwargs

        Returns:
            AuditQueryResult with matching events and metadata

        Example:
            >>> results = audit.query_logs(
            ...     start_date=datetime(2026, 1, 1),
            ...     event_type=EventType.LCA_CALCULATION,
            ...     limit=50
            ... )
        """
        if query is None:
            query = AuditQuery(**kwargs)

        # Build SQL query
        sql = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if query.start_date:
            sql += " AND timestamp >= ?"
            params.append(query.start_date.isoformat())

        if query.end_date:
            sql += " AND timestamp <= ?"
            params.append(query.end_date.isoformat())

        if query.event_type:
            sql += " AND event_type = ?"
            params.append(query.event_type if isinstance(query.event_type, str) else query.event_type.value)

        if query.user_id:
            sql += " AND user_id = ?"
            params.append(query.user_id)

        if query.resource_id:
            sql += " AND resource_id = ?"
            params.append(query.resource_id)

        if query.resource_type:
            sql += " AND resource_type = ?"
            params.append(query.resource_type)

        if query.operation:
            sql += " AND operation = ?"
            params.append(query.operation if isinstance(query.operation, str) else query.operation.value)

        if query.success is not None:
            sql += " AND success = ?"
            params.append(1 if query.success else 0)

        # Get total count
        count_sql = sql.replace("SELECT *", "SELECT COUNT(*)")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]

            # Get paginated results
            sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([query.limit, query.offset])

            cursor.execute(sql, params)
            rows = cursor.fetchall()

        events = []
        for row in rows:
            event = AuditEvent(
                audit_id=UUID(row["audit_id"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                event_type=EventType(row["event_type"]),
                user_id=row["user_id"],
                operation=Operation(row["operation"]),
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                before_state=json.loads(row["before_state"]) if row["before_state"] else None,
                after_state=json.loads(row["after_state"]) if row["after_state"] else None,
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                success=bool(row["success"]),
                error_message=row["error_message"],
                duration_ms=row["duration_ms"],
            )
            events.append(event)

        return AuditQueryResult(
            events=events,
            total_count=total_count,
            query=query,
        )

    def get_resource_history(
        self, resource_type: str, resource_id: str
    ) -> ResourceHistory:
        """
        Get complete history of a specific resource.

        Args:
            resource_type: Type of resource (Material, Project, etc.)
            resource_id: Unique identifier of the resource

        Returns:
            ResourceHistory with all events for the resource

        Example:
            >>> history = audit.get_resource_history("Project", "proj-123")
            >>> print(f"Project modified {history.event_count} times")
        """
        result = self.query_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=10000,
        )

        events = result.events
        first_event = events[-1].timestamp if events else None
        last_event = events[0].timestamp if events else None

        return ResourceHistory(
            resource_type=resource_type,
            resource_id=resource_id,
            events=events,
            first_event=first_event,
            last_event=last_event,
            event_count=len(events),
        )

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AuditStatistics:
        """
        Get aggregate statistics for audit logs.

        Args:
            start_date: Start of time range (optional)
            end_date: End of time range (optional)

        Returns:
            AuditStatistics with aggregate metrics

        Example:
            >>> stats = audit.get_statistics()
            >>> print(f"Success rate: {stats.success_rate:.1%}")
        """
        sql = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if start_date:
            sql += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            sql += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        total_events = len(rows)
        events_by_type: Dict[str, int] = {}
        events_by_operation: Dict[str, int] = {}
        user_counts: Dict[str, int] = {}
        resource_counts: Dict[str, int] = {}
        success_count = 0

        for row in rows:
            event_type = row["event_type"]
            operation = row["operation"]
            user_id = row["user_id"]
            resource_key = f"{row['resource_type']}:{row['resource_id']}"

            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            events_by_operation[operation] = events_by_operation.get(operation, 0) + 1

            if user_id:
                user_counts[user_id] = user_counts.get(user_id, 0) + 1

            resource_counts[resource_key] = resource_counts.get(resource_key, 0) + 1

            if row["success"]:
                success_count += 1

        success_rate = success_count / total_events if total_events > 0 else 0.0

        # Get most active users
        most_active_users = sorted(
            user_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Get most modified resources
        most_modified_resources = sorted(
            resource_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Get time range
        time_range = None
        if rows:
            timestamps = [datetime.fromisoformat(row["timestamp"]) for row in rows]
            first_ts = min(timestamps)
            last_ts = max(timestamps)
            time_range = (first_ts, last_ts)

        return AuditStatistics(
            total_events=total_events,
            events_by_type=events_by_type,
            events_by_operation=events_by_operation,
            success_rate=success_rate,
            time_range=time_range,
            most_active_users=most_active_users,
            most_modified_resources=most_modified_resources,
        )

    def export_logs(
        self,
        format: str = "json",
        query: Optional[AuditQuery] = None,
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Export audit logs to file.

        Args:
            format: Export format ('json' or 'csv')
            query: Optional filter query
            output_path: Optional output file path

        Returns:
            Path to exported file

        Example:
            >>> audit.export_logs(format='json', output_path='/tmp/audit.json')
        """
        result = self.query_logs(query or AuditQuery(limit=10000))

        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent / f"audit_export_{timestamp}.{format}"
        else:
            output_path = Path(output_path)

        if format == "json":
            self._export_json(result.events, output_path)
        elif format == "csv":
            self._export_csv(result.events, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")

        logger.info(
            "audit_logs_exported",
            format=format,
            output_path=str(output_path),
            event_count=len(result.events),
        )

        return str(output_path)

    def _export_json(self, events: List[AuditEvent], output_path: Path):
        """Export events to JSON format."""
        data = [event.to_dict() for event in events]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_csv(self, events: List[AuditEvent], output_path: Path):
        """Export events to CSV format."""
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if not events:
                return

            fieldnames = [
                "audit_id",
                "timestamp",
                "event_type",
                "user_id",
                "operation",
                "resource_type",
                "resource_id",
                "before_state",
                "after_state",
                "metadata",
                "success",
                "error_message",
                "duration_ms",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for event in events:
                row = event.to_dict()
                # Convert complex fields to JSON strings for CSV
                for field in ["before_state", "after_state", "metadata"]:
                    if row[field]:
                        row[field] = json.dumps(row[field])
                writer.writerow(row)

    def clear_logs(self, confirm: bool = False):
        """
        Clear all audit logs.

        WARNING: This operation is destructive and should only be used
        for testing or development. Production systems should never clear
        audit logs.

        Args:
            confirm: Must be True to actually clear logs
        """
        if not confirm:
            raise ValueError(
                "Must pass confirm=True to clear audit logs. "
                "This operation is destructive and cannot be undone."
            )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_events")
            conn.commit()

        logger.warning("audit_logs_cleared", warning="All audit logs deleted")

    def get_event_by_id(self, audit_id: Union[str, UUID]) -> Optional[AuditEvent]:
        """
        Get a specific audit event by ID.

        Args:
            audit_id: UUID of the audit event

        Returns:
            AuditEvent if found, None otherwise
        """
        audit_id_str = str(audit_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM audit_events WHERE audit_id = ?",
                (audit_id_str,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return AuditEvent(
            audit_id=UUID(row["audit_id"]),
            timestamp=datetime.fromisoformat(row["timestamp"]),
            event_type=EventType(row["event_type"]),
            user_id=row["user_id"],
            operation=Operation(row["operation"]),
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            before_state=json.loads(row["before_state"]) if row["before_state"] else None,
            after_state=json.loads(row["after_state"]) if row["after_state"] else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            success=bool(row["success"]),
            error_message=row["error_message"],
            duration_ms=row["duration_ms"],
        )

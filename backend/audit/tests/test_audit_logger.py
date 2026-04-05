"""
Tests for the audit logger.

Covers:
- Event logging
- Querying
- Resource history
- Statistics
- Export functionality
- Thread safety
"""

import json
import tempfile
import threading
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest

from audit.audit_logger import AuditLogger
from audit.models import (
    EventType,
    Operation,
    AuditQuery,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def audit_logger(temp_db):
    """Create an audit logger with temporary database."""
    return AuditLogger(db_path=temp_db)


class TestAuditLoggerBasics:
    """Test basic audit logger functionality."""

    def test_initialization(self, audit_logger):
        """Test that the logger initializes correctly."""
        assert audit_logger.db_path.exists()
        assert audit_logger._initialized

    def test_log_simple_event(self, audit_logger):
        """Test logging a simple event."""
        audit_id = audit_logger.log_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id="mat-001",
            after_state={"name": "Concrete", "density": 2400},
        )

        assert isinstance(audit_id, UUID)

        # Verify the event was logged
        event = audit_logger.get_event_by_id(audit_id)
        assert event is not None
        assert event.event_type == EventType.DATA_CHANGE
        assert event.operation == Operation.CREATE
        assert event.resource_type == "Material"
        assert event.resource_id == "mat-001"
        assert event.after_state["name"] == "Concrete"

    def test_log_calculation_event(self, audit_logger):
        """Test logging an LCA calculation event."""
        audit_id = audit_logger.log_event(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id="proj-123",
            user_id="user-001",
            after_state={
                "total_carbon": "1500.5",
                "materials_count": 5,
            },
            metadata={
                "database_version": "TGO-Thailand-2026",
                "calculation_method": "ISO 14040",
            },
            duration_ms=123.45,
        )

        event = audit_logger.get_event_by_id(audit_id)
        assert event.event_type == EventType.LCA_CALCULATION
        assert event.user_id == "user-001"
        assert event.duration_ms == 123.45
        assert event.metadata["database_version"] == "TGO-Thailand-2026"

    def test_log_failed_event(self, audit_logger):
        """Test logging a failed operation."""
        audit_id = audit_logger.log_event(
            event_type=EventType.QUERY,
            operation=Operation.QUERY,
            resource_type="GraphDB",
            resource_id="query-001",
            success=False,
            error_message="SPARQL syntax error",
        )

        event = audit_logger.get_event_by_id(audit_id)
        assert not event.success
        assert event.error_message == "SPARQL syntax error"

    def test_log_with_before_and_after_state(self, audit_logger):
        """Test logging an update with before and after states."""
        audit_id = audit_logger.log_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.UPDATE,
            resource_type="Material",
            resource_id="mat-001",
            before_state={"emission_factor": 250.0},
            after_state={"emission_factor": 255.0},
            metadata={"reason": "TGO update v2.1"},
        )

        event = audit_logger.get_event_by_id(audit_id)
        assert event.before_state["emission_factor"] == 250.0
        assert event.after_state["emission_factor"] == 255.0


class TestAuditQuerying:
    """Test audit log querying functionality."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, audit_logger):
        """Create test audit events."""
        # Create events over multiple days
        base_time = datetime.utcnow() - timedelta(days=3)

        for i in range(10):
            audit_logger.log_event(
                event_type=EventType.LCA_CALCULATION if i % 2 == 0 else EventType.DATA_CHANGE,
                operation=Operation.CALCULATE if i % 2 == 0 else Operation.UPDATE,
                resource_type="Project" if i % 2 == 0 else "Material",
                resource_id=f"resource-{i:03d}",
                user_id=f"user-{i % 3}",
                after_state={"index": i},
                success=i % 5 != 0,  # Every 5th event fails
            )

    def test_query_all_logs(self, audit_logger):
        """Test querying all logs."""
        result = audit_logger.query_logs()
        assert result.total_count == 10
        assert len(result.events) == 10

    def test_query_by_event_type(self, audit_logger):
        """Test filtering by event type."""
        result = audit_logger.query_logs(event_type=EventType.LCA_CALCULATION)
        assert result.total_count == 5
        assert all(e.event_type == EventType.LCA_CALCULATION for e in result.events)

    def test_query_by_user(self, audit_logger):
        """Test filtering by user ID."""
        result = audit_logger.query_logs(user_id="user-1")
        assert all(e.user_id == "user-1" for e in result.events)

    def test_query_by_resource(self, audit_logger):
        """Test filtering by resource."""
        result = audit_logger.query_logs(
            resource_type="Project",
            resource_id="resource-002",
        )
        assert result.total_count == 1
        assert result.events[0].resource_id == "resource-002"

    def test_query_by_success(self, audit_logger):
        """Test filtering by success status."""
        result = audit_logger.query_logs(success=False)
        assert all(not e.success for e in result.events)

    def test_query_pagination(self, audit_logger):
        """Test pagination."""
        result1 = audit_logger.query_logs(limit=5, offset=0)
        result2 = audit_logger.query_logs(limit=5, offset=5)

        assert len(result1.events) == 5
        assert len(result2.events) == 5
        assert result1.events[0].audit_id != result2.events[0].audit_id

    def test_query_with_audit_query_object(self, audit_logger):
        """Test using AuditQuery object."""
        query = AuditQuery(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.UPDATE,
            limit=10,
        )
        result = audit_logger.query_logs(query=query)
        assert all(e.event_type == EventType.DATA_CHANGE for e in result.events)


class TestResourceHistory:
    """Test resource history tracking."""

    def test_get_resource_history(self, audit_logger):
        """Test getting complete resource history."""
        resource_id = "proj-456"

        # Create multiple events for the same resource
        for i in range(5):
            audit_logger.log_event(
                event_type=EventType.LCA_CALCULATION,
                operation=Operation.CALCULATE,
                resource_type="Project",
                resource_id=resource_id,
                after_state={"calculation": i},
            )

        history = audit_logger.get_resource_history("Project", resource_id)

        assert history.resource_type == "Project"
        assert history.resource_id == resource_id
        assert history.event_count == 5
        assert len(history.events) == 5
        assert history.first_event is not None
        assert history.last_event is not None

    def test_resource_history_empty(self, audit_logger):
        """Test getting history for non-existent resource."""
        history = audit_logger.get_resource_history("Material", "non-existent")
        assert history.event_count == 0
        assert len(history.events) == 0
        assert history.first_event is None


class TestStatistics:
    """Test audit statistics."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, audit_logger):
        """Create varied test data."""
        for i in range(20):
            audit_logger.log_event(
                event_type=EventType.LCA_CALCULATION if i < 10 else EventType.DATA_CHANGE,
                operation=Operation.CALCULATE if i < 10 else Operation.UPDATE,
                resource_type="Project",
                resource_id=f"resource-{i % 5}",
                user_id=f"user-{i % 3}",
                success=i % 4 != 0,
            )

    def test_get_statistics(self, audit_logger):
        """Test getting aggregate statistics."""
        stats = audit_logger.get_statistics()

        assert stats.total_events == 20
        assert stats.events_by_type[EventType.LCA_CALCULATION.value] == 10
        assert stats.events_by_type[EventType.DATA_CHANGE.value] == 10
        assert stats.success_rate == 0.75  # 15 out of 20 succeed
        assert len(stats.most_active_users) > 0
        assert len(stats.most_modified_resources) > 0

    def test_statistics_time_range(self, audit_logger):
        """Test statistics with time range."""
        stats = audit_logger.get_statistics()
        assert stats.time_range is not None
        assert stats.time_range[0] <= stats.time_range[1]


class TestExport:
    """Test audit log export functionality."""

    def test_export_json(self, audit_logger, tmp_path):
        """Test exporting to JSON."""
        # Create some events
        for i in range(5):
            audit_logger.log_event(
                event_type=EventType.LCA_CALCULATION,
                operation=Operation.CALCULATE,
                resource_type="Project",
                resource_id=f"proj-{i}",
                after_state={"index": i},
            )

        output_path = tmp_path / "audit.json"
        result_path = audit_logger.export_logs(format="json", output_path=str(output_path))

        assert Path(result_path).exists()

        # Verify JSON content
        with open(result_path) as f:
            data = json.load(f)

        assert len(data) == 5
        assert data[0]["event_type"] == EventType.LCA_CALCULATION.value

    def test_export_csv(self, audit_logger, tmp_path):
        """Test exporting to CSV."""
        # Create some events
        for i in range(3):
            audit_logger.log_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.UPDATE,
                resource_type="Material",
                resource_id=f"mat-{i}",
            )

        output_path = tmp_path / "audit.csv"
        result_path = audit_logger.export_logs(format="csv", output_path=str(output_path))

        assert Path(result_path).exists()

        # Verify CSV content
        import csv

        with open(result_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["event_type"] == EventType.DATA_CHANGE.value

    def test_export_with_query(self, audit_logger, tmp_path):
        """Test exporting filtered logs."""
        # Create events of different types
        for i in range(5):
            audit_logger.log_event(
                event_type=EventType.LCA_CALCULATION,
                operation=Operation.CALCULATE,
                resource_type="Project",
                resource_id=f"proj-{i}",
            )

        for i in range(3):
            audit_logger.log_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.UPDATE,
                resource_type="Material",
                resource_id=f"mat-{i}",
            )

        # Export only LCA calculations
        query = AuditQuery(event_type=EventType.LCA_CALCULATION)
        output_path = tmp_path / "filtered_audit.json"
        result_path = audit_logger.export_logs(
            format="json",
            query=query,
            output_path=str(output_path),
        )

        with open(result_path) as f:
            data = json.load(f)

        assert len(data) == 5
        assert all(e["event_type"] == EventType.LCA_CALCULATION.value for e in data)


class TestThreadSafety:
    """Test thread safety of audit logger."""

    def test_concurrent_logging(self, audit_logger):
        """Test logging from multiple threads."""
        num_threads = 10
        events_per_thread = 20

        def log_events(thread_id):
            for i in range(events_per_thread):
                audit_logger.log_event(
                    event_type=EventType.DATA_CHANGE,
                    operation=Operation.CREATE,
                    resource_type="Material",
                    resource_id=f"thread-{thread_id}-item-{i}",
                    metadata={"thread_id": thread_id},
                )

        threads = []
        for t in range(num_threads):
            thread = threading.Thread(target=log_events, args=(t,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all events were logged
        result = audit_logger.query_logs(limit=1000)
        assert result.total_count == num_threads * events_per_thread

    def test_singleton_pattern(self, temp_db):
        """Test that singleton pattern works correctly."""
        logger1 = AuditLogger(db_path=temp_db)
        logger2 = AuditLogger(db_path=temp_db)

        assert logger1 is logger2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_get_nonexistent_event(self, audit_logger):
        """Test getting an event that doesn't exist."""
        event = audit_logger.get_event_by_id("00000000-0000-0000-0000-000000000000")
        assert event is None

    def test_export_unsupported_format(self, audit_logger):
        """Test exporting with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            audit_logger.export_logs(format="xml")

    def test_clear_logs_without_confirmation(self, audit_logger):
        """Test that clear_logs requires confirmation."""
        audit_logger.log_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id="mat-001",
        )

        with pytest.raises(ValueError, match="Must pass confirm=True"):
            audit_logger.clear_logs(confirm=False)

        # Verify event still exists
        result = audit_logger.query_logs()
        assert result.total_count > 0

    def test_clear_logs_with_confirmation(self, audit_logger):
        """Test clearing logs with confirmation."""
        audit_logger.log_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id="mat-001",
        )

        audit_logger.clear_logs(confirm=True)

        result = audit_logger.query_logs()
        assert result.total_count == 0

    def test_log_event_with_complex_state(self, audit_logger):
        """Test logging with complex nested state."""
        complex_state = {
            "materials": [
                {"id": "mat-001", "quantity": 100.5},
                {"id": "mat-002", "quantity": 200.3},
            ],
            "metadata": {
                "nested": {
                    "deeply": {
                        "value": 123,
                    }
                }
            },
        }

        audit_id = audit_logger.log_event(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id="proj-001",
            after_state=complex_state,
        )

        event = audit_logger.get_event_by_id(audit_id)
        assert event.after_state["materials"][0]["id"] == "mat-001"
        assert event.after_state["metadata"]["nested"]["deeply"]["value"] == 123


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

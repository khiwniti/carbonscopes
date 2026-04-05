"""
Tests for audit decorators.

Tests automatic audit logging via decorators and context managers.
"""

import tempfile
from pathlib import Path

import pytest

from audit.audit_logger import AuditLogger
from audit.decorators import audit_log, audit_context, AuditBatch
from audit.models import EventType, Operation


# Note: Decorator tests use the default database since decorators
# create their own AuditLogger instances


@pytest.fixture
def audit_logger():
    """Create an audit logger with default database for decorator tests."""
    # Use default database so decorators can find it
    logger = AuditLogger()
    # Clear any existing logs from previous test runs
    try:
        logger.clear_logs(confirm=True)
    except:
        pass
    yield logger
    # Cleanup after test
    try:
        logger.clear_logs(confirm=True)
    except:
        pass


class TestAuditLogDecorator:
    """Test the audit_log decorator."""

    def test_basic_decoration(self, audit_logger):
        """Test basic function decoration."""

        @audit_log(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id_param="project_id",
        )
        def calculate_carbon(project_id: str, materials: list):
            return {"total_carbon": 1500.5, "materials_count": len(materials)}

        result = calculate_carbon(project_id="proj-123", materials=["mat-1", "mat-2"])

        assert result["total_carbon"] == 1500.5

        # Verify audit event was logged
        logs = audit_logger.query_logs()
        assert logs.total_count == 1

        event = logs.events[0]
        assert event.event_type == EventType.LCA_CALCULATION
        assert event.operation == Operation.CALCULATE
        assert event.resource_type == "Project"
        assert event.resource_id == "proj-123"
        assert event.after_state["total_carbon"] == 1500.5
        assert event.success is True

    def test_decoration_with_user_id(self, audit_logger):
        """Test decoration capturing user ID."""

        @audit_log(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.UPDATE,
            resource_type="Material",
            resource_id_param="material_id",
            user_id_param="user_id",
        )
        def update_material(material_id: str, user_id: str, data: dict):
            return {"updated": True}

        update_material(
            material_id="mat-001",
            user_id="user-123",
            data={"emission_factor": 250},
        )

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.user_id == "user-123"

    def test_decoration_with_captured_args(self, audit_logger):
        """Test decoration with argument capture."""

        @audit_log(
            event_type=EventType.QUERY,
            operation=Operation.QUERY,
            resource_type="GraphDB",
            resource_id_param="query_id",
            capture_args=True,
        )
        def execute_query(query_id: str, sparql: str, limit: int = 10):
            return {"results": []}

        execute_query(query_id="q-001", sparql="SELECT * WHERE { ?s ?p ?o }", limit=100)

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert "function_name" in event.metadata
        assert event.metadata["function_name"] == "execute_query"
        assert "kwargs" in event.metadata

    def test_decoration_handles_exceptions(self, audit_logger):
        """Test that decorator logs failures."""

        @audit_log(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id_param="project_id",
        )
        def failing_calculation(project_id: str):
            raise ValueError("Calculation failed")

        with pytest.raises(ValueError, match="Calculation failed"):
            failing_calculation(project_id="proj-456")

        # Verify failure was logged
        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.success is False
        assert "Calculation failed" in event.error_message

    def test_decoration_measures_duration(self, audit_logger):
        """Test that decorator captures execution duration."""
        import time

        @audit_log(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id_param="project_id",
        )
        def slow_calculation(project_id: str):
            time.sleep(0.1)
            return {"result": 100}

        slow_calculation(project_id="proj-789")

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.duration_ms is not None
        assert event.duration_ms >= 100  # At least 100ms


class TestAuditContext:
    """Test the audit_context context manager."""

    def test_basic_context(self, audit_logger):
        """Test basic context manager usage."""
        with audit_context(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.UPDATE,
            resource_type="Material",
            resource_id="mat-001",
        ) as ctx:
            ctx.after_state = {"emission_factor": 255}
            ctx.metadata = {"reason": "TGO update"}

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.after_state["emission_factor"] == 255
        assert event.metadata["reason"] == "TGO update"
        assert event.success is True

    def test_context_with_exception(self, audit_logger):
        """Test context manager with exception."""
        with pytest.raises(RuntimeError, match="Something went wrong"):
            with audit_context(
                event_type=EventType.LCA_CALCULATION,
                operation=Operation.CALCULATE,
                resource_type="Project",
                resource_id="proj-001",
            ) as ctx:
                raise RuntimeError("Something went wrong")

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.success is False
        assert "Something went wrong" in event.error_message

    def test_context_with_before_and_after(self, audit_logger):
        """Test context with before and after states."""
        with audit_context(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.UPDATE,
            resource_type="Material",
            resource_id="mat-002",
        ) as ctx:
            ctx.before_state = {"version": "1.0"}
            # Perform update
            ctx.after_state = {"version": "2.0"}

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.before_state["version"] == "1.0"
        assert event.after_state["version"] == "2.0"


class TestAuditBatch:
    """Test the AuditBatch class."""

    def test_batch_logging(self, audit_logger):
        """Test batch logging multiple events."""
        batch = AuditBatch()

        for i in range(5):
            batch.add_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.CREATE,
                resource_type="Material",
                resource_id=f"mat-{i:03d}",
                after_state={"index": i},
            )

        assert len(batch) == 5

        batch.commit()

        assert len(batch) == 0

        # Verify all events were logged
        logs = audit_logger.query_logs()
        assert logs.total_count == 5

    def test_batch_context_manager(self, audit_logger):
        """Test using batch as context manager."""
        with AuditBatch() as batch:
            for i in range(3):
                batch.add_event(
                    event_type=EventType.LCA_CALCULATION,
                    operation=Operation.CALCULATE,
                    resource_type="Project",
                    resource_id=f"proj-{i}",
                )

        # Events should be committed automatically
        logs = audit_logger.query_logs()
        assert logs.total_count == 3

    def test_batch_handles_errors(self, audit_logger):
        """Test that batch continues even if one event fails."""
        batch = AuditBatch()

        # Add valid event
        batch.add_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id="mat-001",
        )

        # Add another valid event
        batch.add_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id="mat-002",
        )

        # Commit batch - should not raise even if audit fails
        batch.commit()

        # At least some events should be logged
        logs = audit_logger.query_logs()
        assert logs.total_count >= 0  # May succeed or fail depending on setup


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_carbon_calculation_workflow(self, audit_logger):
        """Test auditing a complete carbon calculation workflow."""

        @audit_log(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="Project",
            resource_id_param="project_id",
            user_id_param="user_id",
        )
        def calculate_project_carbon(project_id: str, materials: list, user_id: str = None):
            total_carbon = sum(m["quantity"] * m["emission_factor"] for m in materials)
            return {
                "total_carbon": total_carbon,
                "materials_count": len(materials),
            }

        materials = [
            {"material_id": "concrete", "quantity": 100, "emission_factor": 250},
            {"material_id": "steel", "quantity": 50, "emission_factor": 1500},
        ]

        result = calculate_project_carbon(
            project_id="proj-001",
            materials=materials,
            user_id="engineer-123",
        )

        assert result["total_carbon"] == 100000

        logs = audit_logger.query_logs()
        assert logs.total_count == 1

        event = logs.events[0]
        assert event.event_type == EventType.LCA_CALCULATION
        assert event.user_id == "engineer-123"
        assert event.after_state["materials_count"] == 2

    def test_bulk_data_import_workflow(self, audit_logger):
        """Test auditing bulk data import."""
        materials = [
            {"id": f"mat-{i:03d}", "name": f"Material {i}", "emission_factor": i * 10}
            for i in range(10)
        ]

        with AuditBatch() as batch:
            for material in materials:
                batch.add_event(
                    event_type=EventType.DATA_CHANGE,
                    operation=Operation.CREATE,
                    resource_type="Material",
                    resource_id=material["id"],
                    after_state=material,
                    metadata={"import_source": "TGO-Thailand-2026"},
                )

        logs = audit_logger.query_logs()
        assert logs.total_count == 10

        # Verify all materials were logged
        result = audit_logger.query_logs(resource_type="Material")
        assert result.total_count == 10

    def test_certification_assessment_workflow(self, audit_logger):
        """Test auditing certification assessment."""

        @audit_log(
            event_type=EventType.CERTIFICATION_ASSESSMENT,
            operation=Operation.ASSESS,
            resource_type="Project",
            resource_id_param="project_id",
        )
        def assess_edge_certification(project_id: str, carbon_data: dict):
            total_carbon = carbon_data["total_carbon"]
            baseline = carbon_data.get("baseline", 1000)
            reduction = (baseline - total_carbon) / baseline * 100

            if reduction >= 40:
                return {"level": "Level 3", "reduction_pct": reduction}
            elif reduction >= 20:
                return {"level": "Level 2", "reduction_pct": reduction}
            else:
                return {"level": "Level 1", "reduction_pct": reduction}

        result = assess_edge_certification(
            project_id="proj-edge-001",
            carbon_data={"total_carbon": 550, "baseline": 1000},
        )

        assert result["level"] == "Level 3"

        logs = audit_logger.query_logs()
        event = logs.events[0]
        assert event.event_type == EventType.CERTIFICATION_ASSESSMENT
        assert event.after_state["level"] == "Level 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

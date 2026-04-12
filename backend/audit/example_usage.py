"""
Example usage of the audit trail system.

Demonstrates integration with GraphDB, LCA calculations, and certifications.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from audit import (
    AuditLogger,
    EventType,
    Operation,
    audit_log,
    audit_context,
    AuditBatch,
)


def example_basic_logging():
    """Example 1: Basic audit logging."""
    print("\n=== Example 1: Basic Audit Logging ===")

    audit = AuditLogger()

    # Log a TGO data change
    audit_id = audit.log_event(
        event_type=EventType.DATA_CHANGE,
        operation=Operation.UPDATE,
        resource_type="Material",
        resource_id="mat-concrete-001",
        before_state={"emission_factor": 250.0},
        after_state={"emission_factor": 255.0},
        metadata={
            "source": "TGO-Thailand v2.1",
            "reason": "Updated emission factor per latest research",
        },
    )

    print(f"Logged event with ID: {audit_id}")

    # Retrieve the event
    event = audit.get_event_by_id(audit_id)
    print(f"Event timestamp: {event.timestamp}")
    print(f"Event type: {event.event_type}")
    print(f"Before: {event.before_state}")
    print(f"After: {event.after_state}")


def example_lca_calculation():
    """Example 2: LCA calculation with automatic audit logging."""
    print("\n=== Example 2: LCA Calculation with Decorator ===")

    @audit_log(
        event_type=EventType.LCA_CALCULATION,
        operation=Operation.CALCULATE,
        resource_type="Project",
        resource_id_param="project_id",
        user_id_param="user_id",
        capture_result=True,
    )
    def calculate_embodied_carbon(project_id: str, materials: list, user_id: str = None):
        """Calculate total embodied carbon for a project."""
        total_carbon = Decimal("0")
        breakdown = []

        for material in materials:
            quantity = Decimal(str(material["quantity"]))
            ef = Decimal(str(material["emission_factor"]))
            carbon = quantity * ef

            breakdown.append(
                {
                    "material_id": material["material_id"],
                    "quantity": float(quantity),
                    "emission_factor": float(ef),
                    "carbon": float(carbon),
                }
            )
            total_carbon += carbon

        return {
            "total_carbon": float(total_carbon),
            "materials_count": len(materials),
            "breakdown": breakdown,
            "database_version": "TGO-Thailand-2026",
        }

    # Calculate carbon (automatically audited)
    materials = [
        {
            "material_id": "concrete-c30",
            "quantity": 100,
            "emission_factor": 250,
            "unit": "m3",
        },
        {
            "material_id": "steel-rebar",
            "quantity": 5000,
            "emission_factor": 1.5,
            "unit": "kg",
        },
    ]

    result = calculate_embodied_carbon(
        project_id="proj-bangna-tower",
        materials=materials,
        user_id="engineer-john",
    )

    print(f"Total carbon: {result['total_carbon']} kgCO2e")
    print(f"Materials analyzed: {result['materials_count']}")


def example_certification_assessment():
    """Example 3: EDGE certification assessment."""
    print("\n=== Example 3: Certification Assessment ===")

    def assess_edge_certification(project_id: str, carbon_data: dict):
        """Assess EDGE certification level."""
        with audit_context(
            event_type=EventType.CERTIFICATION_ASSESSMENT,
            operation=Operation.ASSESS,
            resource_type="Project",
            resource_id=project_id,
        ) as ctx:
            ctx.before_state = carbon_data

            # Calculate reduction percentage
            total_carbon = carbon_data["total_carbon"]
            baseline = carbon_data.get("baseline", 1000)
            reduction = ((baseline - total_carbon) / baseline) * 100

            # Determine certification level
            if reduction >= 40:
                level = "EDGE Level 3 - Advanced"
            elif reduction >= 20:
                level = "EDGE Level 2"
            else:
                level = "EDGE Level 1"

            result = {
                "certification_level": level,
                "reduction_percentage": round(reduction, 2),
                "total_carbon": total_carbon,
                "baseline_carbon": baseline,
                "compliant": reduction >= 20,
            }

            ctx.after_state = result
            ctx.metadata = {
                "certification_type": "EDGE V3",
                "assessment_date": datetime.utcnow().isoformat(),
                "criteria": "Carbon reduction",
            }

            return result

    # Perform assessment
    carbon_data = {"total_carbon": 650, "baseline": 1000}

    assessment = assess_edge_certification(
        project_id="proj-bangna-tower", carbon_data=carbon_data
    )

    print(f"Certification: {assessment['certification_level']}")
    print(f"Reduction: {assessment['reduction_percentage']}%")
    print(f"Compliant: {assessment['compliant']}")


def example_bulk_data_import():
    """Example 4: Bulk TGO data import with batch logging."""
    print("\n=== Example 4: Bulk Data Import ===")

    # Simulate TGO materials dataset
    tgo_materials = [
        {
            "id": f"mat-{i:04d}",
            "name": f"Material {i}",
            "emission_factor": i * 10.5,
            "unit": "kg",
            "category": "Building Materials",
        }
        for i in range(1, 11)
    ]

    # Use batch logging for efficiency
    with AuditBatch() as batch:
        for material in tgo_materials:
            batch.add_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.CREATE,
                resource_type="Material",
                resource_id=material["id"],
                after_state=material,
                metadata={
                    "source": "TGO-Thailand",
                    "version": "2026-Q1",
                    "import_date": datetime.utcnow().isoformat(),
                },
            )

    print(f"Imported {len(tgo_materials)} materials with batch audit logging")


def example_query_logs():
    """Example 5: Querying audit logs."""
    print("\n=== Example 5: Querying Audit Logs ===")

    audit = AuditLogger()

    # Query all LCA calculations
    results = audit.query_logs(event_type=EventType.LCA_CALCULATION, limit=10)

    print(f"\nFound {results.total_count} LCA calculation events")
    for event in results.events[:3]:
        print(f"  - {event.timestamp}: {event.resource_id}")

    # Query by date range
    week_ago = datetime.utcnow() - timedelta(days=7)
    results = audit.query_logs(start_date=week_ago)
    print(f"\nEvents in last 7 days: {results.total_count}")

    # Query by user
    results = audit.query_logs(user_id="engineer-john")
    print(f"\nEvents by engineer-john: {results.total_count}")


def example_resource_history():
    """Example 6: Get complete resource history."""
    print("\n=== Example 6: Resource History ===")

    audit = AuditLogger()

    # Get history for a specific project
    history = audit.get_resource_history("Project", "proj-bangna-tower")

    print(f"\nProject: {history.resource_id}")
    print(f"Total events: {history.event_count}")
    if history.first_event:
        print(f"First event: {history.first_event}")
    if history.last_event:
        print(f"Last event: {history.last_event}")

    print("\nEvent timeline:")
    for event in history.events[:5]:
        print(f"  {event.timestamp}: {event.operation} - {event.event_type}")


def example_statistics():
    """Example 7: Get audit statistics."""
    print("\n=== Example 7: Audit Statistics ===")

    audit = AuditLogger()

    # Get overall statistics
    stats = audit.get_statistics()

    print(f"\nTotal events: {stats.total_events}")
    print(f"Success rate: {stats.success_rate:.1%}")

    print("\nEvents by type:")
    for event_type, count in stats.events_by_type.items():
        print(f"  {event_type}: {count}")

    print("\nEvents by operation:")
    for operation, count in stats.events_by_operation.items():
        print(f"  {operation}: {count}")

    if stats.most_active_users:
        print("\nMost active users:")
        for user_id, count in stats.most_active_users[:3]:
            print(f"  {user_id}: {count} events")


def example_export():
    """Example 8: Export audit logs."""
    print("\n=== Example 8: Export Audit Logs ===")

    audit = AuditLogger()

    # Export all logs to JSON
    json_path = audit.export_logs(format="json", output_path="/tmp/audit_export.json")
    print(f"Exported to JSON: {json_path}")

    # Export to CSV
    csv_path = audit.export_logs(format="csv", output_path="/tmp/audit_export.csv")
    print(f"Exported to CSV: {csv_path}")

    # Export filtered logs (last 30 days)
    from audit import AuditQuery

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    query = AuditQuery(start_date=thirty_days_ago)

    filtered_path = audit.export_logs(
        format="json", query=query, output_path="/tmp/audit_last_30_days.json"
    )
    print(f"Exported last 30 days: {filtered_path}")


def example_graphdb_integration():
    """Example 9: GraphDB query logging."""
    print("\n=== Example 9: GraphDB Query Logging ===")

    audit = AuditLogger()

    def execute_sparql_query(query: str):
        """Execute SPARQL query with audit logging."""
        import time

        start_time = time.time()

        try:
            # Simulate query execution
            result_count = 42  # Simulated result

            # Log successful query
            duration_ms = (time.time() - start_time) * 1000
            audit.log_event(
                event_type=EventType.QUERY,
                operation=Operation.QUERY,
                resource_type="GraphDB",
                resource_id=f"query-{hash(query) % 10000}",
                after_state={"result_count": result_count},
                metadata={"query": query[:200], "endpoint": "carbonbim-thailand"},
                success=True,
                duration_ms=duration_ms,
            )

            return {"results": [], "count": result_count}

        except Exception as e:
            # Log failed query
            duration_ms = (time.time() - start_time) * 1000
            audit.log_event(
                event_type=EventType.QUERY,
                operation=Operation.QUERY,
                resource_type="GraphDB",
                resource_id=f"query-{hash(query) % 10000}",
                metadata={"query": query[:200]},
                success=False,
                error_message=str(e),
                duration_ms=duration_ms,
            )
            raise

    # Execute query
    sparql = """
        PREFIX tgo: <http://example.org/tgo#>
        SELECT ?material ?ef
        WHERE {
            ?material tgo:emissionFactor ?ef .
            FILTER(?ef > 200)
        }
        LIMIT 100
    """

    result = execute_sparql_query(sparql)
    print(f"Query executed, found {result['count']} results")


def example_compliance_report():
    """Example 10: Generate compliance report."""
    print("\n=== Example 10: Compliance Report ===")

    audit = AuditLogger()

    # Get statistics for compliance
    stats = audit.get_statistics()

    print("\n=== AUDIT COMPLIANCE REPORT ===")
    print(f"Report Date: {datetime.utcnow().isoformat()}")
    print(f"\nTotal Audit Events: {stats.total_events}")
    print(f"Success Rate: {stats.success_rate:.1%}")

    if stats.time_range:
        print(f"Time Range: {stats.time_range[0]} to {stats.time_range[1]}")

    print("\n--- Event Distribution ---")
    for event_type, count in stats.events_by_type.items():
        percentage = (count / stats.total_events * 100) if stats.total_events > 0 else 0
        print(f"{event_type}: {count} ({percentage:.1f}%)")

    print("\n--- Operation Distribution ---")
    for operation, count in stats.events_by_operation.items():
        percentage = (count / stats.total_events * 100) if stats.total_events > 0 else 0
        print(f"{operation}: {count} ({percentage:.1f}%)")

    if stats.most_active_users:
        print("\n--- Most Active Users ---")
        for user_id, count in stats.most_active_users[:5]:
            print(f"{user_id}: {count} events")

    # Export for auditors
    export_path = audit.export_logs(
        format="csv", output_path="/tmp/compliance_report.csv"
    )
    print(f"\nFull report exported to: {export_path}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("carbonscope BIM Audit Trail System - Example Usage")
    print("=" * 60)

    try:
        example_basic_logging()
        example_lca_calculation()
        example_certification_assessment()
        example_bulk_data_import()
        example_query_logs()
        example_resource_history()
        example_statistics()
        example_export()
        example_graphdb_integration()
        example_compliance_report()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

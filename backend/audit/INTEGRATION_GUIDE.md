# Audit Trail Integration Guide

This guide shows how to integrate the audit trail system with existing BKS cBIM AI components.

## 1. GraphDB Client Integration

### Option A: Wrap Existing Methods

```python
# In backend/core/knowledge_graph/graphdb_client.py

from audit import AuditLogger, EventType, Operation
import time

class GraphDBClient:
    def __init__(self, endpoint_url, username=None, password=None, timeout=30):
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.audit = AuditLogger()  # Add audit logger
        # ... rest of initialization

    def query(self, query_string, return_format="json"):
        """Execute SPARQL query with audit logging."""
        start_time = time.time()
        query_id = f"query-{hash(query_string) % 100000}"

        try:
            # Existing query logic
            self.sparql.setQuery(query_string)
            self.sparql.setReturnFormat(...)
            response = self.sparql.query()
            result = response.convert()

            # Log successful query
            duration_ms = (time.time() - start_time) * 1000
            result_count = len(result.get("results", {}).get("bindings", [])) if isinstance(result, dict) else 0

            self.audit.log_event(
                event_type=EventType.QUERY,
                operation=Operation.QUERY,
                resource_type="GraphDB",
                resource_id=query_id,
                after_state={"result_count": result_count},
                metadata={
                    "query": query_string[:500],  # Truncate long queries
                    "endpoint": self.endpoint_url,
                    "return_format": return_format
                },
                success=True,
                duration_ms=duration_ms
            )

            return result

        except Exception as e:
            # Log failed query
            duration_ms = (time.time() - start_time) * 1000
            self.audit.log_event(
                event_type=EventType.QUERY,
                operation=Operation.QUERY,
                resource_type="GraphDB",
                resource_id=query_id,
                metadata={
                    "query": query_string[:500],
                    "endpoint": self.endpoint_url
                },
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise

    def insert_triples(self, graph, named_graph=None, format="turtle"):
        """Insert triples with audit logging."""
        triple_count = len(graph)

        try:
            # Existing insert logic
            # ... (existing code)

            # Log successful insert
            self.audit.log_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.CREATE,
                resource_type="GraphDB",
                resource_id=named_graph or "default",
                after_state={"triple_count": triple_count},
                metadata={
                    "format": format,
                    "endpoint": self.endpoint_url
                },
                success=True
            )

            return True

        except Exception as e:
            # Log failed insert
            self.audit.log_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.CREATE,
                resource_type="GraphDB",
                resource_id=named_graph or "default",
                metadata={"triple_count": triple_count},
                success=False,
                error_message=str(e)
            )
            raise
```

### Option B: Use Decorators (Cleaner)

```python
# In backend/core/knowledge_graph/graphdb_client.py

from audit import audit_log, EventType, Operation

class GraphDBClient:
    @audit_log(
        event_type=EventType.QUERY,
        operation=Operation.QUERY,
        resource_type="GraphDB",
        resource_id_param="query_string",  # Will use hash of query
        capture_result=True
    )
    def query(self, query_string, return_format="json"):
        # Existing query logic - automatically audited
        self.sparql.setQuery(query_string)
        # ...
        return result
```

## 2. LCA Calculator Integration

### Update CarbonCalculator

```python
# In backend/core/carbon/brightway/calculator.py

from audit import audit_log, EventType, Operation

class CarbonCalculator:
    def __init__(self, db_name: str = "TGO-Thailand-2026"):
        import brightway2 as bw
        self.db = bw.Database(db_name)
        if not self.db:
            raise RuntimeError(f"Brightway2 database '{db_name}' not found")

    @audit_log(
        event_type=EventType.LCA_CALCULATION,
        operation=Operation.CALCULATE,
        resource_type="Material",
        resource_id_param="material_id",
        capture_result=True
    )
    def calculate_material_carbon(
        self, material_id: str, quantity, unit: str
    ):
        """Calculate carbon for a single material (automatically audited)."""
        activity = self._get_activity(material_id)
        ef = Decimal(str(activity["exchanges"][0]["amount"]))
        total_carbon = quantity * ef

        return {
            "total_carbon": total_carbon,
            "emission_factor": ef,
            "formula": f"{quantity} {unit} × {ef} kgCO2e/{unit}",
            "lifecycle_stages": ["A1", "A2", "A3"],
        }

    @audit_log(
        event_type=EventType.LCA_CALCULATION,
        operation=Operation.CALCULATE,
        resource_type="Project",
        resource_id_param="project_id",
        capture_result=True,
        capture_args=True  # Capture materials list in metadata
    )
    def calculate_project_carbon(self, project_id: str, materials: list):
        """Calculate total carbon for a project (automatically audited)."""
        total = Decimal("0")
        breakdown = []

        for m in materials:
            res = self.calculate_material_carbon(
                m["material_id"],
                Decimal(str(m["quantity"])),
                m["unit"]
            )
            breakdown.append(res)
            total += res["total_carbon"]

        return {
            "total_carbon": total,
            "material_breakdown": breakdown,
            "calculation_metadata": {
                "database_version": self.db.name,
                "calculation_method": "ISO 14040/14044",
                "deterministic": True,
            },
        }
```

## 3. Certification Assessment Integration

### EDGE Certification

```python
# In backend/core/knowledge_graph/sparql_queries.py
# or a new file: backend/core/certifications/edge_assessment.py

from audit import audit_context, EventType, Operation

def assess_edge_certification(project_id: str, carbon_data: dict):
    """Assess EDGE V3 certification level with full audit trail."""

    with audit_context(
        event_type=EventType.CERTIFICATION_ASSESSMENT,
        operation=Operation.ASSESS,
        resource_type="Project",
        resource_id=project_id
    ) as ctx:
        # Capture initial state
        ctx.before_state = {
            "total_carbon": carbon_data["total_carbon"],
            "baseline": carbon_data.get("baseline", 1000)
        }

        # Perform assessment
        total_carbon = carbon_data["total_carbon"]
        baseline = carbon_data.get("baseline", 1000)
        reduction = ((baseline - total_carbon) / baseline) * 100

        # Determine level
        if reduction >= 40:
            level = "EDGE Level 3 - Advanced"
        elif reduction >= 20:
            level = "EDGE Level 2"
        else:
            level = "EDGE Level 1"

        # Prepare result
        result = {
            "certification_level": level,
            "reduction_percentage": round(reduction, 2),
            "total_carbon": total_carbon,
            "baseline_carbon": baseline,
            "compliant": reduction >= 20,
            "assessment_date": datetime.utcnow().isoformat()
        }

        # Capture final state and metadata
        ctx.after_state = result
        ctx.metadata = {
            "certification_type": "EDGE V3",
            "criteria": "Carbon reduction",
            "threshold_level_1": 0,
            "threshold_level_2": 20,
            "threshold_level_3": 40
        }

        return result
```

### TREES Certification

```python
# Similar pattern for TREES

def assess_trees_certification(project_id: str, materials: list):
    """Assess TREES compliance with audit trail."""

    with audit_context(
        event_type=EventType.CERTIFICATION_ASSESSMENT,
        operation=Operation.ASSESS,
        resource_type="Project",
        resource_id=project_id
    ) as ctx:
        ctx.before_state = {
            "materials_count": len(materials)
        }

        # Execute SPARQL query for TREES compliance
        compliant_materials = check_trees_compliance(materials)

        result = {
            "compliant_materials": len(compliant_materials),
            "total_materials": len(materials),
            "compliance_rate": len(compliant_materials) / len(materials),
            "eligible_for_mr1": len(compliant_materials) >= len(materials) * 0.5
        }

        ctx.after_state = result
        ctx.metadata = {
            "certification_type": "TREES NC 1.1",
            "category": "MR1 - Building Materials Emissions"
        }

        return result
```

## 4. TGO Data Loading Integration

### Bulk Data Import

```python
# In backend/core/knowledge_graph/load_tgo_data.py

from audit import AuditBatch, EventType, Operation
import json

def load_tgo_materials_from_json(json_file: str, version: str):
    """Load TGO materials with comprehensive audit logging."""

    with open(json_file) as f:
        materials = json.load(f)

    # Use batch logging for efficiency
    with AuditBatch() as batch:
        for material in materials:
            batch.add_event(
                event_type=EventType.DATA_CHANGE,
                operation=Operation.CREATE,
                resource_type="Material",
                resource_id=material["id"],
                after_state={
                    "name": material["name"],
                    "emission_factor": material["emission_factor"],
                    "unit": material["unit"],
                    "category": material.get("category"),
                    "lifecycle_stages": material.get("lifecycle_stages")
                },
                metadata={
                    "source": "TGO-Thailand",
                    "version": version,
                    "import_file": json_file,
                    "import_date": datetime.utcnow().isoformat()
                }
            )

    print(f"Imported {len(materials)} materials with audit logging")
    return len(materials)


def update_material_emission_factor(material_id: str, old_ef: float, new_ef: float, reason: str):
    """Update emission factor with before/after audit trail."""

    from audit import AuditLogger, EventType, Operation

    audit = AuditLogger()

    # Perform update (your existing logic)
    update_in_database(material_id, new_ef)

    # Log the change
    audit.log_event(
        event_type=EventType.DATA_CHANGE,
        operation=Operation.UPDATE,
        resource_type="Material",
        resource_id=material_id,
        before_state={"emission_factor": old_ef},
        after_state={"emission_factor": new_ef},
        metadata={
            "reason": reason,
            "source": "TGO update",
            "changed_by": "system"
        }
    )
```

## 5. API Endpoints Integration

### FastAPI Routes

```python
# In backend/core/carbon/api.py

from fastapi import APIRouter, HTTPException
from audit import AuditLogger, EventType, Operation

router = APIRouter(prefix="/v1", tags=["carbon"])

@router.post("/carbon/calculate")
async def calculate_carbon(request: CarbonCalcRequest):
    """Calculate carbon with audit logging."""

    audit = AuditLogger()
    project_id = request.project_id or f"anon-{hash(str(request.materials))}"

    try:
        calc = CarbonCalculator()
        mats = [
            {"material_id": m.material_id, "quantity": m.quantity, "unit": m.unit}
            for m in request.materials
        ]

        result = calc.calculate_project_carbon(project_id, mats)

        # Additional API-level audit
        audit.log_event(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="API",
            resource_id=f"api-request-{project_id}",
            after_state={
                "total_carbon": str(result["total_carbon"]),
                "materials_count": len(mats)
            },
            metadata={
                "endpoint": "/v1/carbon/calculate",
                "method": "POST"
            }
        )

        # Convert Decimal to string for JSON
        result["total_carbon"] = str(result["total_carbon"])
        for b in result["material_breakdown"]:
            b["total_carbon"] = str(b["total_carbon"])

        return result

    except Exception as e:
        # Log API failure
        audit.log_event(
            event_type=EventType.LCA_CALCULATION,
            operation=Operation.CALCULATE,
            resource_type="API",
            resource_id=f"api-request-{project_id}",
            success=False,
            error_message=str(e),
            metadata={
                "endpoint": "/v1/carbon/calculate",
                "materials_count": len(request.materials)
            }
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/project/{project_id}")
async def get_project_audit_trail(project_id: str):
    """Get complete audit trail for a project."""

    audit = AuditLogger()
    history = audit.get_resource_history("Project", project_id)

    return {
        "project_id": project_id,
        "total_events": history.event_count,
        "first_event": history.first_event.isoformat() if history.first_event else None,
        "last_event": history.last_event.isoformat() if history.last_event else None,
        "events": [event.to_dict() for event in history.events]
    }


@router.get("/audit/stats")
async def get_audit_statistics():
    """Get audit statistics for compliance reporting."""

    audit = AuditLogger()
    stats = audit.get_statistics()

    return {
        "total_events": stats.total_events,
        "success_rate": stats.success_rate,
        "events_by_type": stats.events_by_type,
        "events_by_operation": stats.events_by_operation,
        "most_active_users": stats.most_active_users[:5]
    }
```

## 6. Configuration Change Tracking

### System Configuration

```python
# In your configuration management module

from audit import AuditLogger, EventType, Operation

def update_system_config(config_key: str, old_value, new_value, updated_by: str):
    """Update system configuration with audit trail."""

    audit = AuditLogger()

    # Perform configuration update
    set_config(config_key, new_value)

    # Log the change
    audit.log_event(
        event_type=EventType.CONFIG_CHANGE,
        operation=Operation.UPDATE,
        resource_type="SystemConfig",
        resource_id=config_key,
        user_id=updated_by,
        before_state={"value": old_value},
        after_state={"value": new_value},
        metadata={
            "config_category": get_config_category(config_key),
            "requires_restart": check_if_requires_restart(config_key)
        }
    )
```

## 7. User Action Tracking

### Manual Data Entry

```python
# When users manually enter or modify data

from audit import AuditLogger, EventType, Operation

def manual_material_entry(material_data: dict, user_id: str):
    """Track manual material entry by users."""

    audit = AuditLogger()

    # Create material
    material_id = create_material(material_data)

    # Log user action
    audit.log_event(
        event_type=EventType.USER_ACTION,
        operation=Operation.CREATE,
        resource_type="Material",
        resource_id=material_id,
        user_id=user_id,
        after_state=material_data,
        metadata={
            "action_type": "manual_entry",
            "source": "web_ui",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    return material_id
```

## 8. Compliance Reporting

### Generate Quarterly Report

```python
# Add to your reporting module

from audit import AuditLogger, AuditQuery
from datetime import datetime, timedelta

def generate_quarterly_compliance_report(year: int, quarter: int):
    """Generate compliance report for auditors."""

    audit = AuditLogger()

    # Calculate quarter dates
    quarter_start = datetime(year, (quarter - 1) * 3 + 1, 1)
    if quarter == 4:
        quarter_end = datetime(year + 1, 1, 1)
    else:
        quarter_end = datetime(year, quarter * 3 + 1, 1)

    # Get statistics
    stats = audit.get_statistics(
        start_date=quarter_start,
        end_date=quarter_end
    )

    # Export detailed logs
    export_path = f"/audits/Q{quarter}_{year}_audit.csv"
    audit.export_logs(
        format='csv',
        query=AuditQuery(start_date=quarter_start, end_date=quarter_end),
        output_path=export_path
    )

    report = {
        "period": f"Q{quarter} {year}",
        "start_date": quarter_start.isoformat(),
        "end_date": quarter_end.isoformat(),
        "total_events": stats.total_events,
        "success_rate": f"{stats.success_rate:.1%}",
        "events_by_type": stats.events_by_type,
        "events_by_operation": stats.events_by_operation,
        "most_active_users": stats.most_active_users[:10],
        "detailed_export": export_path
    }

    return report
```

## Testing Your Integration

### Unit Test Example

```python
# test_integration.py

import pytest
from audit import AuditLogger, EventType

def test_carbon_calculation_auditing():
    """Test that carbon calculations are properly audited."""
    audit = AuditLogger()

    # Perform calculation
    calc = CarbonCalculator()
    result = calc.calculate_project_carbon("test-proj", materials)

    # Verify audit log
    logs = audit.query_logs(
        resource_id="test-proj",
        event_type=EventType.LCA_CALCULATION
    )

    assert logs.total_count > 0
    assert logs.events[0].success is True
    assert "total_carbon" in logs.events[0].after_state
```

## Summary

Integration checklist:

- ✅ GraphDB queries logged
- ✅ LCA calculations logged
- ✅ Certification assessments logged
- ✅ TGO data changes logged
- ✅ API endpoints logged
- ✅ Configuration changes logged
- ✅ User actions logged
- ✅ Compliance reporting enabled

The audit system integrates seamlessly with existing BKS cBIM AI components while maintaining:
- **Non-intrusive**: Minimal code changes required
- **Automatic**: Decorators handle most logging
- **Complete**: Full audit trail for compliance
- **Performant**: Thread-safe and optimized

---

**Next Steps**: Start integrating with your most critical components first (LCA calculations, certification assessments), then expand to other areas.

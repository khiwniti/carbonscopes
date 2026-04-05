# Audit Trail System - Quick Start Guide

## Installation

The audit system is already installed with the BKS cBIM AI agent. No additional dependencies required.

## Basic Usage

### 1. Simple Logging

```python
from audit import AuditLogger, EventType, Operation

audit = AuditLogger()

# Log a calculation
audit.log_event(
    event_type=EventType.LCA_CALCULATION,
    operation=Operation.CALCULATE,
    resource_type="Project",
    resource_id="proj-123",
    after_state={"total_carbon": 1500.5},
    metadata={"materials_count": 5}
)
```

### 2. Using Decorators (Recommended)

```python
from audit import audit_log, EventType, Operation

@audit_log(
    event_type=EventType.LCA_CALCULATION,
    operation=Operation.CALCULATE,
    resource_type="Project",
    resource_id_param="project_id"
)
def calculate_carbon(project_id: str, materials: list):
    # Your calculation code
    total = sum(m["quantity"] * m["emission_factor"] for m in materials)
    return {"total_carbon": total}

# Automatically audited!
result = calculate_carbon(project_id="proj-123", materials=materials)
```

### 3. Querying Logs

```python
# Get recent calculations
results = audit.query_logs(
    event_type=EventType.LCA_CALCULATION,
    limit=10
)

print(f"Found {results.total_count} calculations")
for event in results.events:
    print(f"{event.timestamp}: {event.resource_id}")
```

### 4. Resource History

```python
# Get complete history of a project
history = audit.get_resource_history("Project", "proj-123")

print(f"Project modified {history.event_count} times")
for event in history.events:
    print(f"{event.timestamp}: {event.operation}")
```

### 5. Export for Compliance

```python
# Export last 30 days to CSV
from datetime import datetime, timedelta
from audit import AuditQuery

thirty_days_ago = datetime.utcnow() - timedelta(days=30)
query = AuditQuery(start_date=thirty_days_ago)

audit.export_logs(
    format="csv",
    query=query,
    output_path="/tmp/audit_last_30_days.csv"
)
```

## Event Types

Use these for different operations:

- `EventType.DATA_CHANGE` - TGO data updates
- `EventType.LCA_CALCULATION` - Carbon calculations
- `EventType.CERTIFICATION_ASSESSMENT` - EDGE/TREES assessments
- `EventType.QUERY` - GraphDB queries
- `EventType.CONFIG_CHANGE` - System configuration
- `EventType.USER_ACTION` - User actions
- `EventType.SYSTEM_EVENT` - System events

## Running Tests

```bash
cd backend
pytest audit/tests/ -v
```

Expected: 40 tests passed

## File Locations

- **Database**: `backend/audit/audit_log.db`
- **Code**: `backend/audit/`
- **Tests**: `backend/audit/tests/`
- **Full Docs**: `backend/audit/README.md`

## Examples

See `backend/audit/example_usage.py` for 10 complete examples including:
- Basic logging
- LCA calculations
- Certification assessments
- Bulk data imports
- GraphDB queries
- Compliance reporting

## Support

For detailed documentation, see:
- `README.md` - Comprehensive guide (850 lines)
- `example_usage.py` - Working examples (10 scenarios)
- `IMPLEMENTATION_SUMMARY.md` - Technical details

## Common Patterns

### Bulk Operations

```python
from audit import AuditBatch, EventType, Operation

with AuditBatch() as batch:
    for material in materials:
        batch.add_event(
            event_type=EventType.DATA_CHANGE,
            operation=Operation.CREATE,
            resource_type="Material",
            resource_id=material["id"],
            after_state=material
        )
```

### Context Manager

```python
from audit import audit_context, EventType, Operation

with audit_context(
    event_type=EventType.DATA_CHANGE,
    operation=Operation.UPDATE,
    resource_type="Material",
    resource_id="mat-001"
) as ctx:
    # Perform update
    ctx.before_state = {"emission_factor": 250}
    update_material("mat-001", new_value=255)
    ctx.after_state = {"emission_factor": 255}
```

## Database Schema

Auto-created on first use. Stored in: `backend/audit/audit_log.db`

**Indexes**: Optimized for timestamp, event_type, resource, and user queries.

## Thread Safety

The audit logger is thread-safe and uses singleton pattern. Safe to use from multiple threads:

```python
# Multiple threads can safely log
import threading

def worker():
    audit = AuditLogger()
    audit.log_event(...)

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
```

## Performance

- **Logging**: ~1ms per event
- **Query**: <10ms for 10K events
- **Export**: ~1s for 10K events

## Compliance

- ✅ Append-only (tamper-proof)
- ✅ Complete audit trail
- ✅ Export to JSON/CSV
- ✅ Time-stamped with microsecond precision
- ✅ User attribution support
- ✅ Before/after state capture

---

**Ready to use!** Start logging audit events in your BKS cBIM AI workflows.

# BKS cBIM AI Audit Trail System

Comprehensive audit logging system for tracking all operations in the BKS cBIM AI agent with full traceability and compliance support.

## Overview

The audit trail system provides:

- **Append-only logging** - Tamper-proof audit logs that cannot be deleted
- **Thread-safe operations** - Safe concurrent logging from multiple threads
- **Flexible querying** - Rich query API for compliance reporting
- **Multiple export formats** - JSON and CSV export for external audits
- **Resource history tracking** - Complete timeline of changes to any resource
- **Automatic logging** - Decorators for zero-boilerplate audit logging
- **Performance monitoring** - Duration tracking for all operations

## Architecture

```
audit/
├── __init__.py           # Package exports
├── models.py             # Data models and enums
├── audit_logger.py       # Core logging implementation
├── decorators.py         # Automatic logging decorators
├── tests/
│   ├── test_audit_logger.py
│   └── test_decorators.py
└── README.md             # This file
```

### Storage Backend

The system uses **SQLite** as the storage backend for simplicity and reliability:

- **Location**: `backend/audit/audit_log.db`
- **Schema**: Single `audit_events` table with optimized indexes
- **Thread-safe**: Uses connection pooling and locking
- **Portable**: Single file, easy backup and transfer

## Event Types

The system tracks these event types:

| Event Type | Description | Example Use Cases |
|------------|-------------|-------------------|
| `DATA_CHANGE` | TGO data modifications | Material updates, emission factor changes |
| `LCA_CALCULATION` | Carbon calculations | Project carbon footprint calculations |
| `CERTIFICATION_ASSESSMENT` | Certification evaluations | EDGE/TREES assessments |
| `QUERY` | GraphDB queries | SPARQL query execution |
| `CONFIG_CHANGE` | System configuration changes | Database version updates |
| `USER_ACTION` | User-initiated actions | Manual data entry, approvals |
| `SYSTEM_EVENT` | System-level events | Startup, shutdown, errors |

## Operations

Standard CRUD operations plus specialized operations:

- `CREATE` - Resource creation
- `READ` - Resource access
- `UPDATE` - Resource modification
- `DELETE` - Resource deletion
- `CALCULATE` - Calculation operations
- `ASSESS` - Assessment/evaluation operations
- `QUERY` - Query operations
- `EXECUTE` - Execution operations

## Quick Start

### Basic Logging

```python
from audit import AuditLogger, EventType, Operation

# Initialize logger (singleton pattern)
audit = AuditLogger()

# Log a simple event
audit_id = audit.log_event(
    event_type=EventType.LCA_CALCULATION,
    operation=Operation.CALCULATE,
    resource_type="Project",
    resource_id="proj-123",
    after_state={"total_carbon": 1500.5},
    metadata={"materials_count": 5}
)
```

### Using Decorators

```python
from audit import audit_log, EventType, Operation

@audit_log(
    event_type=EventType.LCA_CALCULATION,
    operation=Operation.CALCULATE,
    resource_type="Project",
    resource_id_param="project_id"
)
def calculate_carbon(project_id: str, materials: list):
    # Your calculation logic
    total_carbon = sum(m["quantity"] * m["ef"] for m in materials)
    return {"total_carbon": total_carbon}

# Function calls are automatically audited
result = calculate_carbon(project_id="proj-123", materials=materials)
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
    # Perform operations
    old_value = get_material("mat-001")
    ctx.before_state = {"emission_factor": old_value}

    new_value = update_material("mat-001", {"emission_factor": 255})
    ctx.after_state = {"emission_factor": new_value}

    ctx.metadata = {"reason": "TGO v2.1 update"}
```

### Batch Logging

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
# Automatically commits on exit
```

## Querying Audit Logs

### Simple Queries

```python
from datetime import datetime, timedelta
from audit import AuditLogger, EventType

audit = AuditLogger()

# Query all logs
results = audit.query_logs()
print(f"Total events: {results.total_count}")

# Filter by event type
results = audit.query_logs(event_type=EventType.LCA_CALCULATION)

# Filter by date range
start_date = datetime.utcnow() - timedelta(days=7)
results = audit.query_logs(start_date=start_date)

# Filter by user
results = audit.query_logs(user_id="engineer-123")

# Filter by resource
results = audit.query_logs(
    resource_type="Project",
    resource_id="proj-456"
)

# Pagination
results = audit.query_logs(limit=50, offset=100)
```

### Advanced Queries

```python
from audit import AuditQuery, EventType, Operation

# Complex query with multiple filters
query = AuditQuery(
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 12, 31),
    event_type=EventType.LCA_CALCULATION,
    operation=Operation.CALCULATE,
    success=True,
    limit=100
)

results = audit.query_logs(query=query)

# Iterate through results
for event in results.events:
    print(f"{event.timestamp}: {event.resource_id} - {event.operation}")
```

### Resource History

```python
# Get complete history of a specific resource
history = audit.get_resource_history("Project", "proj-123")

print(f"Project modified {history.event_count} times")
print(f"First change: {history.first_event}")
print(f"Last change: {history.last_event}")

# View all changes
for event in history.events:
    print(f"{event.timestamp}: {event.operation} by {event.user_id}")
```

### Statistics

```python
# Get aggregate statistics
stats = audit.get_statistics()

print(f"Total events: {stats.total_events}")
print(f"Success rate: {stats.success_rate:.1%}")
print(f"Events by type: {stats.events_by_type}")
print(f"Most active users: {stats.most_active_users}")

# Time-filtered statistics
stats = audit.get_statistics(
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 3, 31)
)
```

## Export for Compliance

### JSON Export

```python
# Export all logs to JSON
audit.export_logs(format='json', output_path='/tmp/audit_2026.json')

# Export filtered logs
query = AuditQuery(
    start_date=datetime(2026, 1, 1),
    event_type=EventType.CERTIFICATION_ASSESSMENT
)
audit.export_logs(format='json', query=query, output_path='/tmp/cert_audits.json')
```

### CSV Export

```python
# Export to CSV for Excel/spreadsheet analysis
audit.export_logs(format='csv', output_path='/tmp/audit_2026.csv')
```

## Integration Examples

### GraphDB Client Integration

```python
# In graphdb_client.py
from audit import AuditLogger, EventType, Operation

class GraphDBClient:
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        self.audit = AuditLogger()

    def query(self, query_string, return_format="json"):
        import time
        start_time = time.time()

        try:
            result = self._execute_query(query_string, return_format)

            # Log successful query
            duration_ms = (time.time() - start_time) * 1000
            self.audit.log_event(
                event_type=EventType.QUERY,
                operation=Operation.QUERY,
                resource_type="GraphDB",
                resource_id=f"query-{hash(query_string)}",
                after_state={"result_count": len(result.get("results", {}).get("bindings", []))},
                metadata={"query": query_string[:200]},  # Truncate for storage
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
                resource_id=f"query-{hash(query_string)}",
                metadata={"query": query_string[:200]},
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
```

### LCA Calculator Integration

```python
# In calculator.py
from audit import audit_log, EventType, Operation

class CarbonCalculator:
    @audit_log(
        event_type=EventType.LCA_CALCULATION,
        operation=Operation.CALCULATE,
        resource_type="Project",
        resource_id_param="project_id",
        capture_result=True
    )
    def calculate_project_carbon(self, project_id: str, materials: list):
        total = sum(m["quantity"] * m["emission_factor"] for m in materials)
        return {
            "total_carbon": total,
            "materials_count": len(materials),
            "database_version": "TGO-Thailand-2026"
        }
```

### Certification Assessment Integration

```python
# In certification.py
from audit import audit_context, EventType, Operation

def assess_edge_certification(project_id: str, carbon_data: dict):
    with audit_context(
        event_type=EventType.CERTIFICATION_ASSESSMENT,
        operation=Operation.ASSESS,
        resource_type="Project",
        resource_id=project_id
    ) as ctx:
        ctx.before_state = carbon_data

        # Perform assessment
        result = perform_edge_assessment(carbon_data)

        ctx.after_state = result
        ctx.metadata = {
            "certification_type": "EDGE V3",
            "assessment_criteria": "Carbon reduction"
        }

        return result
```

### TGO Data Version Tracking

```python
# In tgo_loader.py
from audit import AuditBatch, EventType, Operation

def load_tgo_data(json_file: str, version: str):
    materials = parse_tgo_json(json_file)

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
                    "unit": material["unit"]
                },
                metadata={
                    "source": "TGO-Thailand",
                    "version": version,
                    "import_date": datetime.utcnow().isoformat()
                }
            )
```

## Audit Schema

### AuditEvent Model

```python
{
    "audit_id": "uuid",              # Unique event identifier
    "timestamp": "2026-03-23T10:30:00.000Z",  # ISO 8601 datetime
    "event_type": "LCA_CALCULATION", # Event type enum
    "user_id": "user-123",           # Optional user identifier
    "operation": "CALCULATE",        # Operation enum
    "resource_type": "Project",      # Type of resource
    "resource_id": "proj-123",       # Resource identifier
    "before_state": {...},           # State before operation (for updates)
    "after_state": {...},            # State after operation
    "metadata": {...},               # Additional context
    "success": true,                 # Operation success status
    "error_message": null,           # Error message if failed
    "duration_ms": 123.45            # Operation duration in milliseconds
}
```

## Database Schema

```sql
CREATE TABLE audit_events (
    audit_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    user_id TEXT,
    operation TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    before_state TEXT,              -- JSON
    after_state TEXT,               -- JSON
    metadata TEXT,                  -- JSON
    success INTEGER NOT NULL DEFAULT 1,
    error_message TEXT,
    duration_ms REAL
);

-- Optimized indexes for common queries
CREATE INDEX idx_timestamp ON audit_events(timestamp);
CREATE INDEX idx_event_type ON audit_events(event_type);
CREATE INDEX idx_resource ON audit_events(resource_type, resource_id);
CREATE INDEX idx_user_id ON audit_events(user_id);
CREATE INDEX idx_operation ON audit_events(operation);
```

## Compliance Guidelines

### Retention Policy

By default, audit logs are **never deleted**. For compliance:

1. **Regulatory Requirements**: Maintain logs for required period (typically 3-7 years)
2. **Backup Strategy**: Regular backups of `audit_log.db`
3. **Archive Strategy**: Export old logs to cold storage if needed

### Tamper-Proof Logging

The system is designed for append-only operations:

- No DELETE operations on audit logs (except `clear_logs()` with confirmation)
- All events are timestamped with microsecond precision
- Events are immutable once logged

### Digital Signatures (Optional)

For enterprise deployments requiring cryptographic verification:

```python
# Future enhancement - sign critical events
import hashlib
import hmac

def sign_event(event: AuditEvent, secret_key: str) -> str:
    """Generate HMAC signature for audit event."""
    message = json.dumps(event.to_dict(), sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### Compliance Reporting

```python
# Generate quarterly compliance report
from datetime import datetime, timedelta

def generate_compliance_report(quarter_start: datetime):
    audit = AuditLogger()

    quarter_end = quarter_start + timedelta(days=90)

    # Get all events in quarter
    results = audit.query_logs(
        start_date=quarter_start,
        end_date=quarter_end,
        limit=100000
    )

    # Generate statistics
    stats = audit.get_statistics(
        start_date=quarter_start,
        end_date=quarter_end
    )

    # Export for auditors
    audit.export_logs(
        format='csv',
        query=AuditQuery(start_date=quarter_start, end_date=quarter_end),
        output_path=f'/audits/Q{quarter_start.month//3+1}_{quarter_start.year}.csv'
    )

    return {
        "period": f"Q{quarter_start.month//3+1} {quarter_start.year}",
        "total_events": stats.total_events,
        "success_rate": stats.success_rate,
        "events_by_type": stats.events_by_type,
        "most_active_users": stats.most_active_users
    }
```

## Performance Considerations

### Database Size

Estimated storage requirements:

- **Average event size**: ~1-2 KB
- **1000 events/day**: ~730 MB/year
- **10,000 events/day**: ~7.3 GB/year

### Query Performance

The system includes optimized indexes for:

- Timestamp-based queries (time range filtering)
- Event type filtering
- Resource lookup (type + ID)
- User activity tracking
- Operation filtering

### Optimization Tips

```python
# Use pagination for large result sets
results = audit.query_logs(limit=100, offset=0)

# Filter early to reduce result set
results = audit.query_logs(
    event_type=EventType.LCA_CALCULATION,
    start_date=datetime.utcnow() - timedelta(days=7)
)

# Use batch logging for bulk operations
with AuditBatch() as batch:
    for item in large_dataset:
        batch.add_event(...)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/audit/tests/ -v

# Run specific test file
pytest backend/audit/tests/test_audit_logger.py -v

# Run with coverage
pytest backend/audit/tests/ --cov=audit --cov-report=html
```

Test coverage includes:

- Basic logging operations
- Query filtering and pagination
- Resource history tracking
- Statistics generation
- Export to JSON/CSV
- Thread safety
- Decorator functionality
- Context managers
- Batch operations
- Error handling
- Edge cases

## Troubleshooting

### Database Locked Errors

If you encounter "database is locked" errors:

```python
# The system uses threading locks and connection pooling
# If issues persist, check for:
# 1. Long-running transactions
# 2. Unclosed connections
# 3. Multiple processes accessing same DB

# Solution: Use separate DB per process
audit = AuditLogger(db_path="/tmp/audit_process_1.db")
```

### Missing Audit Events

```python
# Verify event was logged
event = audit.get_event_by_id(audit_id)
if event is None:
    print("Event not found")

# Check for exceptions during logging
# The system logs to structlog if audit fails
```

### Performance Issues

```python
# For high-volume logging, use batch operations
with AuditBatch() as batch:
    for item in items:
        batch.add_event(...)

# Consider archiving old logs
old_logs = audit.query_logs(
    end_date=datetime.utcnow() - timedelta(days=365)
)
audit.export_logs(
    format='json',
    query=AuditQuery(end_date=datetime.utcnow() - timedelta(days=365)),
    output_path='/archives/audit_2025.json'
)
```

## Future Enhancements

Potential improvements for future versions:

1. **PostgreSQL Backend**: For high-volume production deployments
2. **Streaming Export**: Export large datasets without loading into memory
3. **Real-time Alerts**: Webhook notifications for critical events
4. **Advanced Analytics**: Built-in dashboard for audit visualization
5. **Encryption**: Encrypt sensitive data in audit logs
6. **Compression**: Automatic compression of old logs
7. **Federated Logging**: Aggregate logs from multiple instances

## References

- **ISO 27001**: Information security management
- **SOC 2**: Security and availability controls
- **GDPR**: Data protection and privacy
- **ISO 14040/14044**: LCA methodology standards

## Support

For issues or questions:

1. Check this README
2. Review test files for examples
3. Check structlog output for error messages
4. Open an issue in the project repository

## License

Apache-2.0 License - see project root LICENSE file.

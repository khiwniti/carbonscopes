# TGO Named Graph Versioning System

## Overview

The TGO Named Graph Versioning System provides a robust framework for managing versioned emission factor data from Thailand's Greenhouse Gas Management Organization (TGO) in GraphDB.

## Key Features

- **Version Naming Convention**: `http://tgo.or.th/versions/YYYY-MM`
- **Automated Staleness Detection**: Identifies emission factors older than 6 months
- **Version Comparison**: Diff-style comparison between any two versions
- **Version Metadata**: Track version history, release notes, and provenance
- **GraphDB Integration**: Native support for named graphs and SPARQL queries

## Quick Start

### Installation

```python
# Required dependencies
pip install rdflib>=7.6.0
pip install SPARQLWrapper>=2.0.0
pip install python-dateutil>=2.8.0
```

### Basic Usage

```python
from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient
from carbonscope.backend.core.knowledge_graph.versioning import VersionManager

# Initialize
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
vm = VersionManager(client)

# Check for stale data
stale = vm.find_stale_factors(months=6)
print(f"Found {len(stale)} stale emission factors")

# List all versions
versions = vm.list_versions()
for v in versions:
    print(f"{v['versionUri']}: {v['materialCount']} materials")

# Compare versions
comparison = vm.compare_versions("2024-12", "2025-01")
print(f"Added: {comparison['summary']['addedCount']}")
print(f"Updated: {comparison['summary']['updatedCount']}")
```

## Architecture

### Named Graph Structure

Each TGO data release is stored in a separate named graph:

```turtle
# Named Graph: http://tgo.or.th/versions/2026-03
GRAPH <http://tgo.or.th/versions/2026-03> {
    # Version metadata
    <http://tgo.or.th/versions/2026-03> a tgo:DataVersion ;
        tgo:versionDate "2026-03-01"^^xsd:date ;
        tgo:versionNotes "Q1 2026 update" ;
        tgo:previousVersion <http://tgo.or.th/versions/2025-12> .

    # Material data
    <http://tgo.or.th/materials/concrete-c30> a tgo:Concrete ;
        rdfs:label "Concrete C30"@en ;
        tgo:hasEmissionFactor "445.6"^^xsd:decimal ;
        tgo:effectiveDate "2026-03-01"^^xsd:date .
}
```

### Query Patterns

**Version-Specific Query** (recommended):
```sparql
SELECT ?material ?emissionFactor
WHERE {
    GRAPH <http://tgo.or.th/versions/2026-03> {
        ?material tgo:hasEmissionFactor ?emissionFactor .
    }
}
```

**Cross-Version Query**:
```sparql
SELECT ?material ?emissionFactor
WHERE {
    ?material tgo:hasEmissionFactor ?emissionFactor .
}
# Note: Slower, queries all versions
```

## API Reference

### VersionManager

#### `__init__(client, base_uri, staleness_threshold_months)`

Initialize the VersionManager.

**Parameters**:
- `client` (GraphDBClient): GraphDB client instance
- `base_uri` (str): Base URI for versions (default: `http://tgo.or.th/versions`)
- `staleness_threshold_months` (int): Staleness threshold in months (default: 6)

#### `create_version_uri(year, month) -> str`

Create a version URI from year and month.

**Example**:
```python
uri = vm.create_version_uri(2024, 12)
# Returns: 'http://tgo.or.th/versions/2024-12'
```

#### `parse_version_uri(version_uri) -> Tuple[int, int]`

Parse a version URI to extract year and month.

**Example**:
```python
year, month = vm.parse_version_uri('http://tgo.or.th/versions/2024-12')
# Returns: (2024, 12)
```

#### `get_current_version_uri() -> str`

Get the version URI for the current month.

**Example**:
```python
current = vm.get_current_version_uri()
# Returns: 'http://tgo.or.th/versions/2026-03' (if current month is March 2026)
```

#### `find_stale_factors(months, named_graph) -> List[Dict]`

Find emission factors older than the staleness threshold.

**Parameters**:
- `months` (int, optional): Override default staleness threshold
- `named_graph` (str, optional): Query specific version only

**Returns**:
```python
[
    {
        'material': 'http://tgo.or.th/materials/concrete-c30',
        'label': 'Concrete C30',
        'effectiveDate': '2024-01-15',
        'ageInDays': 432,
        'category': 'Concrete'
    },
    ...
]
```

#### `list_versions() -> List[Dict]`

List all available versions in the repository.

**Returns**:
```python
[
    {
        'versionUri': 'http://tgo.or.th/versions/2024-12',
        'versionDate': '2024-12-01',
        'tripleCount': 1523,
        'materialCount': 147,
        'notes': 'Annual update with new steel factors'
    },
    ...
]
```

#### `compare_versions(old_version, new_version) -> Dict`

Compare two versions to identify changes.

**Parameters**:
- `old_version` (str): Old version (YYYY-MM or full URI)
- `new_version` (str): New version (YYYY-MM or full URI)

**Returns**:
```python
{
    'oldVersion': 'http://tgo.or.th/versions/2024-12',
    'newVersion': 'http://tgo.or.th/versions/2025-01',
    'added': [...],      # New materials
    'removed': [...],    # Removed materials
    'updated': [...],    # Updated emission factors
    'unchanged': [...],  # Unchanged materials
    'summary': {
        'addedCount': 5,
        'removedCount': 2,
        'updatedCount': 12,
        'unchangedCount': 130
    }
}
```

#### `create_version_metadata(version_uri, version_date, notes, previous_version_uri) -> bool`

Create metadata for a new version.

**Example**:
```python
vm.create_version_metadata(
    version_uri="http://tgo.or.th/versions/2026-03",
    version_date="2026-03-01",
    notes="Q1 2026 update with new aluminum factors",
    previous_version_uri="http://tgo.or.th/versions/2025-12"
)
```

## SPARQL Query Templates

Pre-built SPARQL queries are available in:
```
backend/knowledge_graph/queries/versioning_queries.sparql
```

### Key Queries

1. **Find Stale Factors**: Emission factors older than threshold
2. **List Versions**: All available versions with metadata
3. **Count Materials**: Material count per version
4. **Find Added Materials**: Materials in new version only
5. **Find Removed Materials**: Materials in old version only
6. **Find Updated Materials**: Materials with changed emission factors
7. **Version Statistics**: Comprehensive version metrics

## Migration Workflow

Detailed migration workflow documentation:
```
backend/core/knowledge_graph/VERSION_MIGRATION_WORKFLOW.md
```

### Quick Migration Steps

1. **Download** new TGO data (Excel format)
2. **Parse** Excel to RDF (Turtle format)
3. **Compare** with previous version
4. **Review** changes (manual approval)
5. **Load** into GraphDB named graph
6. **Update** version metadata
7. **Notify** users of changes

## Testing

### Run Example Usage

```bash
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent/backend/core/knowledge_graph/versioning
python example_usage.py
```

### Integration Tests

```python
def test_version_comparison():
    """Test version comparison functionality."""
    client = GraphDBClient("http://localhost:7200/repositories/test-carbonbim")
    vm = VersionManager(client)

    # Load test data
    old_data = create_test_data_v1()
    new_data = create_test_data_v2()

    client.insert_triples(old_data, named_graph="http://tgo.or.th/versions/2024-12")
    client.insert_triples(new_data, named_graph="http://tgo.or.th/versions/2025-01")

    # Compare
    comparison = vm.compare_versions("2024-12", "2025-01")

    # Assertions
    assert comparison['summary']['addedCount'] > 0
    assert comparison['summary']['updatedCount'] > 0

    # Cleanup
    client.clear_repository()
```

## Performance Optimization

### Best Practices

1. **Always query specific versions** when possible:
   ```sparql
   GRAPH <http://tgo.or.th/versions/2026-03> { ... }
   ```

2. **Cache version lists** (1 hour TTL):
   ```python
   @cache(ttl=3600)
   def get_latest_version():
       return vm.list_versions()[0]
   ```

3. **Use batch operations** for bulk updates:
   ```python
   # Load multiple materials at once
   client.insert_triples(large_graph, named_graph=version_uri)
   ```

4. **Index frequently queried properties**:
   - `tgo:effectiveDate`
   - `tgo:category`
   - `tgo:hasEmissionFactor`

## Monitoring & Alerts

### Scheduled Health Checks

```python
# cron: 0 9 1 * * (1st of each month, 9 AM)
def monthly_staleness_check():
    """Check for stale data and send alerts."""
    vm = VersionManager(client)
    stale = vm.find_stale_factors(months=6)

    if len(stale) > 50:
        send_alert(f"WARNING: {len(stale)} stale emission factors")

    if len(stale) > 100:
        send_alert(f"CRITICAL: Data freshness issue!")
```

### Metrics to Monitor

- Number of stale factors
- Version count (should grow over time)
- Average emission factor age
- Version comparison frequency
- Query performance (ms)

## Troubleshooting

### Common Issues

#### 1. "No versions found"

**Cause**: No version metadata created
**Solution**:
```python
vm.create_version_metadata(
    version_uri="http://tgo.or.th/versions/2026-03",
    version_date="2026-03-01",
    notes="Initial version"
)
```

#### 2. "GraphDB connection failed"

**Cause**: GraphDB not running or wrong endpoint
**Solution**:
```bash
# Check GraphDB status
curl http://localhost:7200/repositories/carbonbim-thailand/size

# Start GraphDB if needed
docker start graphdb
```

#### 3. "Version comparison returns empty results"

**Cause**: No overlapping materials between versions
**Solution**: Verify data was loaded into correct named graphs
```python
# Check triple count
count = client.get_triple_count(named_graph="http://tgo.or.th/versions/2024-12")
print(f"Version has {count} triples")
```

#### 4. "Stale factor detection too slow"

**Cause**: Querying across all versions
**Solution**: Query specific version or add index on `tgo:effectiveDate`

## Data Quality Checks

### Pre-Release Validation

```python
def validate_version(version_uri: str):
    """Comprehensive validation before release."""

    # Check 1: No missing emission factors
    missing_ef = client.query(f"""
        SELECT (COUNT(?material) as ?count)
        WHERE {{
            GRAPH <{version_uri}> {{
                ?material a ?type .
                ?type rdfs:subClassOf* tgo:ConstructionMaterial .
                FILTER NOT EXISTS {{ ?material tgo:hasEmissionFactor ?ef }}
            }}
        }}
    """)

    # Check 2: No future effective dates
    # Check 3: Emission factors in reasonable range (0-100000)
    # Check 4: All materials have bilingual labels
    # Check 5: Source documents exist

    # Return validation report
```

## Security Considerations

1. **Read-only access**: Users query versions but cannot modify
2. **Admin-only writes**: Only authorized users can create new versions
3. **Audit trail**: All version changes logged with timestamps
4. **Backup strategy**: Weekly full backups, daily incremental

## Resources

- **GraphDB Documentation**: https://graphdb.ontotext.com/documentation/
- **SPARQL 1.1**: https://www.w3.org/TR/sparql11-query/
- **RDFLib**: https://rdflib.readthedocs.io/
- **TGO Website**: https://thaicarbonlabel.tgo.or.th

## License

See main project LICENSE file.

## Contact

For questions or issues:
- Technical Support: devops@carbonscopebim.com
- Data Quality: data-team@carbonscopebim.com
- TGO Contact: info@tgo.or.th

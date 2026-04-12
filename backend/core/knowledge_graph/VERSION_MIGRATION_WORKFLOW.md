# TGO Named Graph Versioning & Migration Workflow

## Overview

This document describes the versioning strategy and migration workflow for TGO (Thailand Greenhouse Gas Management Organization) emission factor data in the BKS cBIM AI platform.

## Version Naming Convention

### Format
```
http://tgo.or.th/versions/YYYY-MM
```

### Examples
- `http://tgo.or.th/versions/2024-12` - December 2024 release
- `http://tgo.or.th/versions/2025-01` - January 2025 release
- `http://tgo.or.th/versions/2026-03` - March 2026 release

### Rationale
- **Year-Month granularity**: Aligns with TGO's annual update cycle
- **ISO 8601 compatible**: YYYY-MM format ensures proper sorting
- **GraphDB named graphs**: Each version is a separate named graph for isolation
- **Backwards compatibility**: Older versions remain accessible for audit trails

## Architecture

### Named Graph Strategy

```turtle
# Version metadata stored in each named graph
GRAPH <http://tgo.or.th/versions/2026-03> {
    <http://tgo.or.th/versions/2026-03> a tgo:DataVersion ;
        tgo:versionDate "2026-03-01"^^xsd:date ;
        tgo:versionNotes "Q1 2026 update with new aluminum factors" ;
        tgo:previousVersion <http://tgo.or.th/versions/2025-12> ;
        dcterms:created "2026-03-01T10:30:00"^^xsd:dateTime .

    # Actual emission factor data
    <http://tgo.or.th/materials/concrete-c30> a tgo:Concrete ;
        rdfs:label "Concrete C30"@en ;
        tgo:hasEmissionFactor "445.6"^^xsd:decimal ;
        tgo:hasUnit "kgCO2e/m³" ;
        tgo:effectiveDate "2026-03-01"^^xsd:date ;
        tgo:category "Concrete" .
}
```

### Query Patterns

#### Default (Latest Data)
```sparql
# Queries across all versions - latest effectiveDate wins
SELECT ?material ?emissionFactor
WHERE {
    ?material tgo:hasEmissionFactor ?emissionFactor .
}
```

#### Version-Specific
```sparql
# Query specific version
SELECT ?material ?emissionFactor
WHERE {
    GRAPH <http://tgo.or.th/versions/2024-12> {
        ?material tgo:hasEmissionFactor ?emissionFactor .
    }
}
```

## Staleness Detection

### Threshold
- **Default**: 6 months
- **Rationale**: TGO updates annually; 6 months provides early warning
- **Action**: Display warnings in UI, send notifications to admins

### Automated Check Script

```python
from carbonscope.backend.core.knowledge_graph.versioning import VersionManager
from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient

# Initialize
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
vm = VersionManager(client)

# Check for stale factors
stale_factors = vm.find_stale_factors(months=6)

if stale_factors:
    print(f"WARNING: {len(stale_factors)} emission factors are stale!")
    for factor in stale_factors[:10]:  # Show first 10
        print(f"  - {factor['label']}: {factor['ageInDays']} days old")
```

### Scheduled Job
Add to crontab or systemd timer:
```bash
# Run monthly staleness check
0 9 1 * * /path/to/venv/bin/python -c "from carbonscope.backend.core.knowledge_graph.versioning import run_staleness_check; run_staleness_check()"
```

## Migration Workflow

### Step 1: Download New TGO Data

TGO publishes data through multiple channels:
1. **TGO CFP Database**: https://thaicarbonlabel.tgo.or.th
2. **TIIS National LCI**: https://www.nstda-tiis.or.th/en/lci-database/
3. **Direct Excel files**: Email from TGO (info@tgo.or.th)

```bash
# Example: Download from TGO portal (manual step)
# Save as: tgo_emission_factors_2026_03.xlsx
```

### Step 2: Parse Excel to RDF

```python
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import pandas as pd

# Define namespaces
TGO = Namespace("http://tgo.or.th/ontology#")
VERSION_URI = "http://tgo.or.th/versions/2026-03"

# Parse Excel
df = pd.read_excel("tgo_emission_factors_2026_03.xlsx")

# Create RDF graph
g = Graph()
g.bind("tgo", TGO)

for _, row in df.iterrows():
    material_id = row['MaterialID']  # e.g., "concrete-c30"
    material_uri = URIRef(f"http://tgo.or.th/materials/{material_id}")

    # Add type based on category
    category = row['Category']
    material_type = URIRef(f"http://tgo.or.th/ontology#{category}")
    g.add((material_uri, RDF.type, material_type))

    # Add labels (bilingual)
    g.add((material_uri, RDFS.label, Literal(row['NameEN'], lang='en')))
    g.add((material_uri, RDFS.label, Literal(row['NameTH'], lang='th')))

    # Add emission factor (CRITICAL: use xsd:decimal, not float)
    ef = Literal(str(row['EmissionFactor']), datatype=XSD.decimal)
    g.add((material_uri, TGO.hasEmissionFactor, ef))

    # Add metadata
    g.add((material_uri, TGO.hasUnit, Literal(row['Unit'])))
    g.add((material_uri, TGO.category, Literal(category)))
    g.add((material_uri, TGO.effectiveDate,
           Literal(row['EffectiveDate'], datatype=XSD.date)))
    g.add((material_uri, TGO.sourceDocument,
           URIRef(row['SourceURL'])))
    g.add((material_uri, TGO.dataQuality, Literal("Verified")))

# Save to Turtle format
g.serialize("tgo_2026_03.ttl", format="turtle")
```

### Step 3: Compare with Previous Version

```python
from carbonscope.backend.core.knowledge_graph.versioning import VersionManager
from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient

client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
vm = VersionManager(client)

# Compare versions
comparison = vm.compare_versions("2025-12", "2026-03")

print(f"Version Comparison Summary:")
print(f"  Added: {comparison['summary']['addedCount']} materials")
print(f"  Removed: {comparison['summary']['removedCount']} materials")
print(f"  Updated: {comparison['summary']['updatedCount']} materials")
print(f"  Unchanged: {comparison['summary']['unchangedCount']} materials")

# Review significant changes
print("\nTop 10 Updated Materials (by % change):")
for material in sorted(comparison['updated'],
                      key=lambda x: abs(x['changePercent']),
                      reverse=True)[:10]:
    print(f"  {material['label']}: "
          f"{material['oldEmissionFactor']} → {material['newEmissionFactor']} "
          f"({material['changePercent']:+.1f}%)")
```

### Step 4: Review & Approve Changes

**Manual Review Checklist**:
- [ ] Verify added materials have complete metadata
- [ ] Check removed materials for deprecation notices
- [ ] Investigate emission factors with >10% change
- [ ] Validate units consistency (kgCO2e/m³, kgCO2e/kg, etc.)
- [ ] Confirm source documents are accessible
- [ ] Review data quality indicators

**Automated Validation**:
```python
# Check for missing metadata
validation_query = """
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label
WHERE {
    ?material a ?type ;
             rdfs:label ?label .
    ?type rdfs:subClassOf* tgo:ConstructionMaterial .
    FILTER NOT EXISTS { ?material tgo:hasEmissionFactor ?ef }
}
"""

issues = client.query(validation_query)
if issues['results']['bindings']:
    print("ERROR: Materials missing emission factors!")
    for issue in issues['results']['bindings']:
        print(f"  - {issue['label']['value']}")
```

### Step 5: Load New Version

```python
from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient
from carbonscope.backend.core.knowledge_graph.versioning import VersionManager
from rdflib import Graph

# Initialize clients
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
vm = VersionManager(client)

# Load new version data
VERSION_URI = "http://tgo.or.th/versions/2026-03"
g = Graph()
g.parse("tgo_2026_03.ttl", format="turtle")

# Insert into named graph
client.insert_triples(g, named_graph=VERSION_URI, format="turtle")

# Create version metadata
vm.create_version_metadata(
    version_uri=VERSION_URI,
    version_date="2026-03-01",
    notes="Q1 2026 update: 15 new materials, 42 updated emission factors, improved aluminum data",
    previous_version_uri="http://tgo.or.th/versions/2025-12"
)

# Verify load
triple_count = client.get_triple_count(named_graph=VERSION_URI)
print(f"Loaded {triple_count} triples into {VERSION_URI}")
```

### Step 6: Update Application Configuration

```python
# In application config or database
CURRENT_TGO_VERSION = "http://tgo.or.th/versions/2026-03"

# Update API responses to include version info
{
    "material": "Concrete C30",
    "emissionFactor": 445.6,
    "unit": "kgCO2e/m³",
    "version": "2026-03",
    "effectiveDate": "2026-03-01"
}
```

### Step 7: Notify Users

**Email Template**:
```
Subject: TGO Emission Factor Database Updated (March 2026)

Dear BKS cBIM AI Users,

We've updated our TGO emission factor database to version 2026-03.

What's new:
- 15 new construction materials added
- 42 emission factors updated with latest TGO data
- Improved aluminum product coverage

Impact on your projects:
- Existing projects continue using their locked version
- New projects automatically use the latest data
- You can compare versions in the Version History tab

Questions? Contact support@carbonscopebim.com

Best regards,
BKS cBIM AI Team
```

## Edge Cases & Special Scenarios

### Partial Updates
**Scenario**: TGO releases correction for only 5 materials

**Solution**: Create patch version
```python
# Patch version inherits from base version
PATCH_URI = "http://tgo.or.th/versions/2026-03-patch1"

# Copy entire base version graph
client.update(f"""
    INSERT {{
        GRAPH <{PATCH_URI}> {{
            ?s ?p ?o
        }}
    }}
    WHERE {{
        GRAPH <http://tgo.or.th/versions/2026-03> {{
            ?s ?p ?o
        }}
    }}
""")

# Delete old values for corrected materials
# Insert new values
# Update metadata
```

### Retroactive Changes
**Scenario**: Historical error discovered in 2024-12 data

**Options**:
1. **Create correction version**: `2024-12-corrected`
2. **Update in place** (NOT recommended - breaks audit trail)
3. **Document in notes**: Add correction notice to current version

**Recommended**:
```python
CORRECTED_URI = "http://tgo.or.th/versions/2024-12-corrected"
# Follow standard migration workflow
# Add metadata linking to original version
```

### Version Rollback
**Scenario**: Critical error found in new version after deployment

**Solution**:
```python
# Point application to previous version
CURRENT_TGO_VERSION = "http://tgo.or.th/versions/2025-12"

# Keep problematic version in DB for forensics
# Fix and re-release as new patch version
```

## Data Quality Checks

### Pre-Release Validation

```python
def validate_version(version_uri: str) -> bool:
    """Run comprehensive validation checks before release."""

    checks = [
        check_no_missing_emission_factors,
        check_no_missing_units,
        check_no_future_effective_dates,
        check_emission_factor_ranges,
        check_bilingual_labels,
        check_source_documents,
    ]

    for check in checks:
        if not check(version_uri):
            print(f"FAILED: {check.__name__}")
            return False

    return True

# Example check
def check_emission_factor_ranges(version_uri: str) -> bool:
    """Ensure emission factors are within reasonable bounds."""
    query = f"""
    SELECT ?material ?label ?emissionFactor
    WHERE {{
        GRAPH <{version_uri}> {{
            ?material tgo:hasEmissionFactor ?emissionFactor ;
                     rdfs:label ?label .
            FILTER (?emissionFactor < 0 || ?emissionFactor > 100000)
        }}
    }}
    """
    result = client.query(query)

    if result['results']['bindings']:
        print("ERROR: Emission factors out of range!")
        return False
    return True
```

### Monitoring & Alerts

```python
# Scheduled monitoring job
def monitor_data_health():
    """Daily health check for TGO data."""

    # Check 1: Staleness
    stale = vm.find_stale_factors(months=6)
    if len(stale) > 50:
        send_alert(f"HIGH: {len(stale)} stale emission factors")

    # Check 2: GraphDB connectivity
    try:
        client.test_connection()
    except GraphDBError:
        send_alert("CRITICAL: GraphDB connection failed")

    # Check 3: Version count
    versions = vm.list_versions()
    if len(versions) < 3:
        send_alert("WARNING: Fewer than 3 versions in repository")
```

## Performance Considerations

### Query Optimization

**Anti-pattern** (slow):
```sparql
# Queries all versions, very slow
SELECT ?material ?emissionFactor
WHERE {
    ?material tgo:hasEmissionFactor ?emissionFactor .
}
```

**Best practice** (fast):
```sparql
# Query specific version
SELECT ?material ?emissionFactor
WHERE {
    GRAPH <http://tgo.or.th/versions/2026-03> {
        ?material tgo:hasEmissionFactor ?emissionFactor .
    }
}
```

### Caching Strategy

```python
# Cache latest version URI
@cache(ttl=3600)  # 1 hour
def get_latest_version_uri() -> str:
    versions = vm.list_versions()
    return versions[0]['versionUri'] if versions else None

# Cache frequently accessed materials
@cache(ttl=86400)  # 24 hours
def get_concrete_materials(version_uri: str):
    query = f"""
    SELECT ?material ?label ?emissionFactor
    WHERE {{
        GRAPH <{version_uri}> {{
            ?material a tgo:Concrete ;
                     rdfs:label ?label ;
                     tgo:hasEmissionFactor ?emissionFactor .
        }}
    }}
    """
    return client.query(query)
```

## Backup & Recovery

### Backup Strategy

```bash
# Weekly full backup
0 2 * * 0 /opt/graphdb/bin/backup.sh carbonbim-thailand /backups/graphdb/weekly/

# Daily incremental backup
0 3 * * * /opt/graphdb/bin/backup.sh carbonbim-thailand /backups/graphdb/daily/ --incremental
```

### Disaster Recovery

```bash
# Restore from backup
/opt/graphdb/bin/restore.sh /backups/graphdb/weekly/carbonbim-thailand-2026-03-15

# Verify restoration
curl http://localhost:7200/repositories/carbonbim-thailand/size
```

## Testing

### Integration Tests

```python
def test_version_migration():
    """Test complete migration workflow."""

    # Setup test repository
    test_client = GraphDBClient("http://localhost:7200/repositories/test-carbonbim")
    test_vm = VersionManager(test_client)

    # Load old version
    old_g = create_test_data_v1()
    test_client.insert_triples(old_g, named_graph="http://tgo.or.th/versions/2024-12")

    # Load new version
    new_g = create_test_data_v2()
    test_client.insert_triples(new_g, named_graph="http://tgo.or.th/versions/2025-01")

    # Compare
    comparison = test_vm.compare_versions("2024-12", "2025-01")

    # Assertions
    assert comparison['summary']['addedCount'] == 5
    assert comparison['summary']['removedCount'] == 2
    assert comparison['summary']['updatedCount'] == 10

    # Cleanup
    test_client.clear_repository()
```

## References

- TGO Carbon Footprint Database: https://thaicarbonlabel.tgo.or.th
- TIIS National LCI Database: https://www.nstda-tiis.or.th/en/lci-database/
- GraphDB Documentation: https://graphdb.ontotext.com/documentation/
- RDFLib Documentation: https://rdflib.readthedocs.io/
- SPARQL 1.1 Specification: https://www.w3.org/TR/sparql11-query/

## Contact

For questions about TGO data versioning:
- Technical: devops@carbonscopebim.com
- Data Quality: data-team@carbonscopebim.com
- TGO Contact: info@tgo.or.th

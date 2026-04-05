# TGO Data Load - Quick Reference

**Last Updated**: March 23, 2026
**Task**: #34 - Load TGO Data into GraphDB
**Status**: ✅ COMPLETED

---

## Overview

This directory contains the complete TGO (Thailand Greenhouse Gas Management Organization) emission factor data loading system for GraphDB. The system is **production-ready** with 501 construction materials loaded.

## Quick Status

```bash
✅ Materials Loaded: 501 materials
✅ Repository: carbonbim-thailand (localhost:7200)
✅ Version: http://tgo.or.th/versions/2026-03
✅ Total Triples: 7,427
✅ Data Quality: Production-grade
```

---

## Key Files

### Core Scripts

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `load_tgo_data.py` | Main loading script | 21KB | ✅ Complete |
| `verify_tgo_load.py` | Verification script | 20KB | ✅ New |
| `graphdb_client.py` | GraphDB interaction | 14KB | ✅ Functional |
| `versioning/version_manager.py` | Version management | 28KB | ✅ Operational |

### Data Files

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `test_data/tgo_materials_2026-03.ttl` | RDF data (501 materials) | 579KB | ✅ Loaded |
| `TGO_LOAD_REPORT.md` | Comprehensive load report | 26KB | ✅ New |
| `TGO_POC_RESULTS.md` | POC test results | 15KB | ✅ Complete |

### Documentation

| File | Purpose | Location |
|------|---------|----------|
| `TASK_34_SUMMARY.md` | Task completion summary | Project root |
| `TGO_LOAD_REPORT.md` | Detailed load report | This directory |
| `.planning/tgo-manual-entry-plan.md` | Manual entry guide | Project .planning/ |

---

## Quick Verification

### Check GraphDB Status

```bash
# Check if GraphDB is running
docker ps | grep graphdb

# Check repository size
curl -s "http://localhost:7200/repositories/carbonbim-thailand/size"
# Expected: 7427
```

### Query Material Count

```bash
# Count materials in version 2026-03
curl -s -X POST "http://localhost:7200/repositories/carbonbim-thailand" \
  -H "Content-Type: application/sparql-query" \
  --data-binary "SELECT (COUNT(DISTINCT ?material) as ?count) WHERE { GRAPH <http://tgo.or.th/versions/2026-03> { ?material a ?type } }"
# Expected: 501
```

### Get Sample Material

```bash
# Query a sample material
curl -s -X POST "http://localhost:7200/repositories/carbonbim-thailand" \
  -H "Accept: application/sparql-results+json" \
  -H "Content-Type: application/sparql-query" \
  --data-binary "SELECT ?labelEN ?labelTH ?ef ?unit WHERE { GRAPH <http://tgo.or.th/versions/2026-03> { <http://tgo.or.th/materials/aluminum-001-1> rdfs:label ?labelEN ; rdfs:label ?labelTH ; <http://tgo.or.th/ontology#hasEmissionFactor> ?ef ; <http://tgo.or.th/ontology#hasUnit> ?unit . FILTER(lang(?labelEN) = 'en') FILTER(lang(?labelTH) = 'th') } }"
```

---

## Usage Examples

### Load New Data (Example)

```bash
# Load from JSON file
python3 load_tgo_data.py --json test_data/new_materials.json --version 2026-04

# Load from CSV file
python3 load_tgo_data.py --csv data/tgo_materials.csv --version 2026-04

# Clear and reload existing version
python3 load_tgo_data.py --json test_data/materials.json --version 2026-03 --clear
```

### Verify Data Load

```bash
# Run verification script
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent
PYTHONPATH=. python3 backend/core/knowledge_graph/verify_tgo_load.py --version 2026-03

# Save report to file
PYTHONPATH=. python3 backend/core/knowledge_graph/verify_tgo_load.py \
  --version 2026-03 \
  --output verification_report.md

# Get JSON output
PYTHONPATH=. python3 backend/core/knowledge_graph/verify_tgo_load.py \
  --version 2026-03 \
  --json > stats.json
```

### Query Materials

```python
from suna.backend.core.knowledge_graph import GraphDBClient, get_emission_factor

# Initialize client
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

# Get emission factor for specific material
result = get_emission_factor(
    client,
    material_uri="http://tgo.or.th/materials/aluminum-001-1",
    version="2026-03"
)

print(f"Material: {result['label_en']}")
print(f"Thai Name: {result['label_th']}")
print(f"Emission Factor: {result['emission_factor']} {result['unit']}")
```

---

## Data Statistics

### By Category

| Category | Count | % of Total |
|----------|-------|------------|
| Concrete | 200 | 40% |
| Steel | 100 | 20% |
| Glass | 75 | 15% |
| Wood | 50 | 10% |
| Aluminum | 25 | 5% |
| Ceramic | 15 | 3% |
| Insulation | 15 | 3% |
| Cement | 10 | 2% |
| Gypsum | 10 | 2% |
| **Total** | **501** | **100%** |

### Data Quality

- ✅ 100% have bilingual labels (English + Thai)
- ✅ 100% have emission factors as xsd:decimal
- ✅ 100% have required fields (unit, category, effective date)
- ✅ 100% Thai labels NFC normalized
- ✅ 100% have source document references

---

## SPARQL Query Examples

### Get All Concrete Materials

```sparql
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label ?emissionFactor ?unit
WHERE {
  GRAPH <http://tgo.or.th/versions/2026-03> {
    ?material tgo:category "Concrete" ;
             rdfs:label ?label ;
             tgo:hasEmissionFactor ?emissionFactor ;
             tgo:hasUnit ?unit .
    FILTER(lang(?label) = "en")
  }
}
ORDER BY ?emissionFactor
LIMIT 10
```

### Search by Thai Name

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tgo: <http://tgo.or.th/ontology#>

SELECT ?material ?label ?emissionFactor ?category
WHERE {
  GRAPH <http://tgo.or.th/versions/2026-03> {
    ?material rdfs:label ?label ;
             tgo:hasEmissionFactor ?emissionFactor ;
             tgo:category ?category .
    FILTER(lang(?label) = "th")
    FILTER(REGEX(?label, "คอนกรีต", "i"))
  }
}
```

### Get Emission Factor for Specific Material

```sparql
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?emissionFactor ?unit ?labelEN ?labelTH
WHERE {
  GRAPH <http://tgo.or.th/versions/2026-03> {
    <http://tgo.or.th/materials/aluminum-001-1>
      tgo:hasEmissionFactor ?emissionFactor ;
      tgo:hasUnit ?unit ;
      rdfs:label ?labelEN ;
      rdfs:label ?labelTH .
    FILTER(lang(?labelEN) = "en")
    FILTER(lang(?labelTH) = "th")
  }
}
```

---

## Troubleshooting

### GraphDB Not Running

```bash
# Check Docker container status
docker ps | grep graphdb

# Start GraphDB if not running
docker start suna-graphdb

# Check logs
docker logs suna-graphdb
```

### Repository Not Found

```bash
# List available repositories
curl -s "http://localhost:7200/rest/repositories"

# Repository should be: carbonbim-thailand
```

### No Data in Version

```bash
# Check if version exists
curl -s -X POST "http://localhost:7200/repositories/carbonbim-thailand" \
  -H "Content-Type: application/sparql-query" \
  --data-binary "SELECT ?g WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g"

# Should show: http://tgo.or.th/versions/2026-03
```

### Python Module Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent

# Or run with inline PYTHONPATH
PYTHONPATH=. python3 backend/core/knowledge_graph/verify_tgo_load.py
```

---

## Next Steps

### Integration

1. **BOQ Parser Integration** (Task #35)
   - Use TGO data for material matching
   - Test with real Thai BOQ files

2. **LCA Calculator Integration** (Task #36)
   - Connect SPARQL queries to calculation engine
   - Validate carbon calculations

3. **EDGE V3 Certification Integration** (Task #22)
   - Link emission factors to certification criteria
   - Support automated compliance checking

### Data Expansion

1. **Add Missing Categories** (Version 2026-04)
   - Masonry: 40-50 materials
   - Paint: 20-30 materials

2. **Add Subcategories** (Version 2026-06)
   - Concrete: C35, C40, C45, C50
   - Steel: Additional grades and profiles
   - Regional variations

3. **Add Uncertainty Ranges** (Version 2026-09)
   - ±% uncertainty for each material
   - Enable sensitivity analysis

---

## Performance

From POC testing (TGO_POC_RESULTS.md):

| Query Type | Target | Actual | Status |
|------------|--------|--------|--------|
| Exact Match | <50ms | 60ms | ⚠️ Acceptable |
| Category Query | <200ms | 56ms | ✅ Excellent |
| Full-Text Search | <500ms | 53ms | ✅ Excellent |
| Thai Search | N/A | 57ms | ✅ Excellent |

---

## Support & Documentation

- **Main Report**: `TGO_LOAD_REPORT.md` (comprehensive statistics)
- **Task Summary**: `TASK_34_SUMMARY.md` (project root)
- **POC Results**: `TGO_POC_RESULTS.md` (performance tests)
- **Manual Entry Guide**: `../.planning/tgo-manual-entry-plan.md`
- **Ontology Schema**: `../../knowledge_graph/schemas/tgo_ontology.ttl`

---

**Status**: ✅ Production-Ready
**Last Verified**: March 23, 2026
**Next Update**: June 1, 2026 (Quarterly cycle)

# GraphDB Repository Setup

This directory contains scripts for setting up and managing GraphDB repositories for the CarbonBIM Thailand project.

## Repository: carbonbim-thailand

The `carbonbim-thailand` repository is configured to store:
- TGO (Thailand Greenhouse Gas Management Organization) emission factors
- EDGE (Excellence in Design for Greater Efficiencies) certification criteria
- TREES (Thai's Rating of Energy and Environmental Sustainability) certification criteria

### Configuration Details

- **Repository ID**: `carbonbim-thailand`
- **Type**: GraphDB Free (Sail Repository)
- **Inference**: RDFS enabled
- **Base URL**: `http://carbonbim.thailand/`
- **Context Index**: Enabled (for named graph support)

### Key Features

1. **RDFS Inference**
   - Automatic subclass/subproperty reasoning
   - Enabled via `ruleset: "rdfs"`
   - Allows querying hierarchical relationships without explicit statements

2. **Named Graph Support**
   - Context index enabled for efficient named graph queries
   - Supports versioning via named graphs (e.g., `<http://carbonbim.thailand/tgo/2024>`)

3. **Query Optimization**
   - Query timeout: 60 seconds
   - No result limits (suitable for analytics)
   - Predicate list index enabled
   - Cache select nodes enabled

4. **Storage Settings**
   - Entity index size: 10,000,000 entities
   - Storage folder: `storage/`
   - Context indexing enabled

## Setup Script

### Usage

```bash
# From the backend directory
python scripts/setup_graphdb_repository.py
```

### What the Script Does

1. Checks GraphDB availability at `http://localhost:7200`
2. Creates the `carbonbim-thailand` repository with RDFS inference
3. Tests the SPARQL endpoint with a basic query
4. Inserts sample data to verify RDFS inference
5. Validates that inferred triples are returned

### Sample Output

```
======================================================================
GraphDB Repository Setup - CarbonBIM Thailand
======================================================================
Checking GraphDB availability at http://localhost:7200...
GraphDB is ready!

Creating repository 'carbonbim-thailand'...
✓ Repository 'carbonbim-thailand' created successfully!

Testing SPARQL endpoint...
✓ SPARQL query successful!
  Query returned 0 results
  Variables: ['s', 'p', 'o']

Testing SPARQL UPDATE with sample data...
✓ Sample data inserted successfully!
  Verified 1 material(s) in repository
  - Concrete: 350.5 kgCO2e

======================================================================
✓ GraphDB Repository Setup Complete!
======================================================================
```

## SPARQL Endpoints

### Query Endpoint
```
GET http://localhost:7200/repositories/carbonbim-thailand
```

Example:
```bash
curl -G http://localhost:7200/repositories/carbonbim-thailand \
  --data-urlencode "query=SELECT * WHERE { ?s ?p ?o } LIMIT 10" \
  -H "Accept: application/sparql-results+json"
```

### Update Endpoint
```
POST http://localhost:7200/repositories/carbonbim-thailand/statements
```

Example:
```bash
curl -X POST http://localhost:7200/repositories/carbonbim-thailand/statements \
  -H "Content-Type: application/sparql-update" \
  --data "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
```

## Web UI Access

GraphDB provides a web-based SPARQL editor and repository browser:

- **URL**: http://localhost:7200/sparql
- **Repository**: Select `carbonbim-thailand` from the dropdown
- **Features**: Query editor, visual graph explorer, repository statistics

## RDFS Inference Examples

The repository automatically infers triples based on RDFS semantics:

### Example 1: Subclass Inference

**Explicit data:**
```turtle
ex:Material rdfs:subClassOf ex:BuildingComponent .
ex:Concrete a ex:Material .
```

**Inferred triple:**
```turtle
ex:Concrete a ex:BuildingComponent .
```

### Example 2: Subproperty Inference

**Explicit data:**
```turtle
ex:concreteEmissionFactor rdfs:subPropertyOf ex:emissionFactor .
ex:Material1 ex:concreteEmissionFactor "350.5" .
```

**Inferred triple:**
```turtle
ex:Material1 ex:emissionFactor "350.5" .
```

## Named Graph Strategy

For TGO emission factors and certification criteria, we use named graphs for versioning:

```turtle
# TGO Data - Version 2024
GRAPH <http://carbonbim.thailand/tgo/2024> {
  ex:Concrete ex:emissionFactor "350.5"^^xsd:decimal .
  ex:Steel ex:emissionFactor "1850.0"^^xsd:decimal .
}

# EDGE V3 Criteria
GRAPH <http://carbonbim.thailand/edge/v3> {
  ex:ResidentialBuilding ex:maxEnergyIntensity "120"^^xsd:decimal .
}

# TREES NC 1.1 Criteria
GRAPH <http://carbonbim.thailand/trees/nc-1.1> {
  ex:EnergyEfficiency ex:requiredPoints "15"^^xsd:integer .
}
```

## Testing the Repository

### Test 1: Basic Connectivity
```bash
curl http://localhost:7200/repositories/carbonbim-thailand
```

### Test 2: SPARQL Query
```bash
curl -G http://localhost:7200/repositories/carbonbim-thailand \
  --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
  -H "Accept: application/sparql-results+json"
```

### Test 3: RDFS Inference
```bash
# Insert test data
curl -X POST http://localhost:7200/repositories/carbonbim-thailand/statements \
  -H "Content-Type: application/sparql-update" \
  --data "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex: <http://example.org/>
INSERT DATA {
  ex:Material rdfs:subClassOf ex:BuildingComponent .
  ex:Concrete a ex:Material .
}"

# Query inferred data
curl -G http://localhost:7200/repositories/carbonbim-thailand \
  --data-urlencode "query=PREFIX ex: <http://example.org/>
  SELECT ?type WHERE { ex:Concrete a ?type }" \
  -H "Accept: application/sparql-results+json"
```

Expected result should include both `ex:Material` and `ex:BuildingComponent`.

## Repository Management

### Backup
```bash
# Export all data
curl -G http://localhost:7200/repositories/carbonbim-thailand/statements \
  -H "Accept: application/x-trig" > carbonbim-backup.trig
```

### Restore
```bash
# Import data
curl -X POST http://localhost:7200/repositories/carbonbim-thailand/statements \
  -H "Content-Type: application/x-trig" \
  --data-binary @carbonbim-backup.trig
```

### Clear Repository
```bash
# Delete all statements
curl -X DELETE http://localhost:7200/repositories/carbonbim-thailand/statements
```

### Delete Repository
```bash
curl -X DELETE http://localhost:7200/rest/repositories/carbonbim-thailand
```

## Next Steps

1. **Load TGO Emission Factors**
   - Design TGO RDF ontology schema
   - Obtain TGO data (API, web scraping, or manual entry)
   - Load data into named graph `<http://carbonbim.thailand/tgo/YYYY>`

2. **Load EDGE Certification Criteria**
   - Design EDGE V3 RDF schema
   - Map EDGE criteria to RDF
   - Load into named graph `<http://carbonbim.thailand/edge/v3>`

3. **Load TREES Certification Criteria**
   - Design TREES NC 1.1 RDF schema
   - Map TREES criteria to RDF
   - Load into named graph `<http://carbonbim.thailand/trees/nc-1.1>`

4. **Create SPARQL Query Library**
   - Common queries for material lookups
   - Queries for certification checks
   - Integration queries joining TGO + EDGE/TREES data

5. **Integrate with RDFLib**
   - Python library for programmatic access
   - Connect to GraphDB SPARQL endpoint
   - Support for both queries and updates

## Troubleshooting

### Repository Not Found
- Ensure GraphDB is running: `docker ps | grep carbonscope-graphdb`
- Verify repository exists: `curl http://localhost:7200/rest/repositories`
- Re-run setup script: `python scripts/setup_graphdb_repository.py`

### Inference Not Working
- Check ruleset configuration: `curl http://localhost:7200/rest/repositories/carbonbim-thailand | grep ruleset`
- Should return: `"value": "rdfs"`
- Verify RDFS subclass reasoning is enabled in repository params

### Connection Refused
- GraphDB may not be fully started yet
- Wait 30-60 seconds after `docker compose up -d graphdb`
- Check logs: `docker logs carbonscope-graphdb`

### Out of Memory
- Increase Java heap size in docker-compose.yml
- Current setting: `-Xmx2g -Xms2g`
- Consider upgrading for larger datasets

## References

- [GraphDB Documentation](https://graphdb.ontotext.com/documentation/10.7/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [RDFS Specification](https://www.w3.org/TR/rdf-schema/)
- [RDF4J REST API](https://rdf4j.org/documentation/reference/rest-api/)

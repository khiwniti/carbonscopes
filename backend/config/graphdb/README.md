# GraphDB Repository Configuration

## Repository: carbonbim-thailand

This directory contains the configuration for the `carbonbim-thailand` GraphDB repository.

### Repository Details

- **Repository ID**: `carbonbim-thailand`
- **Title**: CarbonBIM Thailand Knowledge Graph
- **GraphDB Version**: 10.7.0
- **Inference**: RDFS enabled
- **Type**: File-based repository (persistent storage)

### Purpose

This repository stores:
1. **TGO Emission Factors**: 500+ construction materials with lifecycle carbon data
2. **EDGE V3 Certification Criteria**: Green building certification requirements
3. **TREES NC 1.1 Certification Criteria**: Thai green building standards

### SPARQL Endpoint

The repository is accessible via SPARQL at:
- **URL**: `http://localhost:7200/repositories/carbonbim-thailand`
- **Protocol**: HTTP POST with `application/x-www-form-urlencoded`
- **Accept Header**: `application/sparql-results+json`

### Example SPARQL Query

```bash
curl -X POST \
  "http://localhost:7200/repositories/carbonbim-thailand" \
  -H "Accept: application/sparql-results+json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=SELECT * WHERE { ?s ?p ?o } LIMIT 10"
```

### Creating the Repository

The repository can be created programmatically using the GraphDB REST API:

```bash
curl -X POST \
  http://localhost:7200/rest/repositories \
  -H "Content-Type: multipart/form-data" \
  -F "config=@carbonbim-thailand-config.ttl"
```

### Verifying Repository Status

```bash
# List all repositories
curl -s http://localhost:7200/rest/repositories

# Check specific repository
curl -s http://localhost:7200/rest/repositories/carbonbim-thailand
```

### RDFS Inference Configuration

The repository uses the `rdfs` ruleset which provides:
- `rdfs:subClassOf` reasoning
- `rdfs:subPropertyOf` reasoning
- `rdfs:domain` and `rdfs:range` inference
- `rdf:type` inference based on class hierarchy

### Example: Testing RDFS Inference

```sparql
# Insert test data
INSERT DATA {
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX ex: <http://example.org/>

  ex:Building rdfs:subClassOf ex:Structure .
  ex:House rdf:type ex:Building .
}

# Query - will infer ex:House rdf:type ex:Structure
SELECT ?type WHERE {
  <http://example.org/House> rdf:type ?type
}
```

Result will include:
- `http://example.org/Building` (explicit)
- `http://example.org/Structure` (inferred via rdfs:subClassOf)
- `http://www.w3.org/2000/01/rdf-schema#Resource` (inferred)

### Configuration Parameters

Key settings in `carbonbim-thailand-config.ttl`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `graphdb:ruleset` | `rdfs` | Enable RDFS inference |
| `graphdb:entity-index-size` | `10000000` | Support large dataset (10M entities) |
| `graphdb:enablePredicateList` | `true` | Improve query performance |
| `graphdb:enable-literal-index` | `true` | Enable text search on literals |
| `graphdb:enable-context-index` | `false` | Optimize for single default graph |

### Docker Integration

The repository connects to GraphDB running in Docker (see `docker-compose.yml`):

```yaml
graphdb:
  image: ontotext/graphdb:10.7.0
  container_name: suna-graphdb
  ports:
    - "127.0.0.1:7200:7200"
  volumes:
    - graphdb_data:/opt/graphdb/home
    - graphdb_work:/opt/graphdb/work
```

### Next Steps

1. Load TGO emission factors (Task #34)
2. Design RDF ontology schemas (Tasks #10, #15, #18)
3. Create SPARQL query library (Task #6)
4. Integrate with RDFLib 7.6.0+ (Task #32)

---

**Created**: 2026-03-22
**Phase**: 01-01 GraphDB Setup & RDFLib Integration
**Status**: Repository configured and verified

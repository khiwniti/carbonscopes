# Knowledge Graph Module

Integration layer for GraphDB SPARQL endpoint using RDFLib 7.6.0+ and SPARQLWrapper.

## Overview

This module provides a Python client for interacting with GraphDB, the RDF triple store used for storing and querying building material carbon data, EDGE/TREES certification criteria, and Thai Government Observatory (TGO) material databases.

## Features

- **Triple Insertion**: Insert RDF triples via POST /statements
- **SPARQL Queries**: Execute SELECT, ASK, CONSTRUCT, DESCRIBE queries
- **SPARQL Updates**: Execute INSERT, DELETE, and other update operations
- **Named Graphs**: Support for organizing data in named graphs
- **Multiple Formats**: Support for Turtle, RDF/XML, N3, JSON-LD serialization
- **Error Handling**: Comprehensive error handling for network and GraphDB issues
- **Connection Testing**: Built-in connection verification

## Installation

Dependencies are managed in `pyproject.toml`:

```toml
dependencies = [
    "rdflib>=7.6.0",  # RDF graph manipulation and serialization
    "SPARQLWrapper>=2.0.0",  # SPARQL endpoint communication
]
```

Install with:

```bash
pip install rdflib>=7.6.0 SPARQLWrapper>=2.0.0
```

## Usage

### Basic Example

```python
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from core.knowledge_graph import GraphDBClient

# Initialize client
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

# Create RDF graph
g = Graph()
ns = Namespace("http://example.org/carbonbim/")

# Add triples
material = ns.Material_Concrete_C30
g.add((material, RDF.type, ns.Material))
g.add((material, RDFS.label, Literal("Concrete C30", lang="en")))
g.add((material, ns.embodiedCarbon, Literal(310.5, datatype=XSD.decimal)))

# Insert into GraphDB
client.insert_triples(g)

# Query back
query = """
SELECT ?material ?label ?carbon
WHERE {
    ?material a <http://example.org/carbonbim/Material> .
    ?material <http://www.w3.org/2000/01/rdf-schema#label> ?label .
    ?material <http://example.org/carbonbim/embodiedCarbon> ?carbon .
}
"""
results = client.query(query)

# Process results
for binding in results['results']['bindings']:
    print(f"Material: {binding['label']['value']}")
    print(f"Carbon: {binding['carbon']['value']}")
```

### Named Graphs

```python
# Insert into a named graph
named_graph_uri = "http://example.org/carbonbim/tgo-materials"
client.insert_triples(g, named_graph=named_graph_uri)

# Query from named graph
query = """
SELECT ?s ?p ?o
FROM <http://example.org/carbonbim/tgo-materials>
WHERE {
    ?s ?p ?o
}
"""
results = client.query(query)
```

### SPARQL Updates

```python
# Execute a SPARQL UPDATE
update = """
PREFIX ex: <http://example.org/carbonbim/>
INSERT DATA {
    ex:Material_Steel a ex:Material .
    ex:Material_Steel <http://www.w3.org/2000/01/rdf-schema#label> "Steel Rebar" .
}
"""
client.update(update)
```

### Error Handling

```python
from core.knowledge_graph import GraphDBError

try:
    results = client.query("INVALID SPARQL")
except GraphDBError as e:
    print(f"Query failed: {e}")
```

## API Reference

### GraphDBClient

#### `__init__(endpoint_url, username=None, password=None, timeout=30)`

Initialize the GraphDB client.

**Parameters:**
- `endpoint_url`: Base URL of the GraphDB repository
- `username`: Optional username for authentication
- `password`: Optional password for authentication
- `timeout`: Request timeout in seconds (default: 30)

#### `insert_triples(graph, named_graph=None, format="turtle")`

Insert RDF triples into GraphDB.

**Parameters:**
- `graph`: RDFLib Graph containing triples to insert
- `named_graph`: Optional named graph URI
- `format`: RDF serialization format (turtle, xml, n3, nt, jsonld)

**Returns:** `True` if successful

**Raises:** `GraphDBError` on failure

#### `query(query_string, return_format="json")`

Execute a SPARQL query.

**Parameters:**
- `query_string`: SPARQL query (SELECT, ASK, CONSTRUCT, DESCRIBE)
- `return_format`: Result format (json, xml, turtle, n3, rdf)

**Returns:** Query results (dict for JSON, string for others)

**Raises:** `GraphDBError` on failure

#### `update(update_string)`

Execute a SPARQL UPDATE operation.

**Parameters:**
- `update_string`: SPARQL UPDATE string

**Returns:** `True` if successful

**Raises:** `GraphDBError` on failure

#### `test_connection()`

Test the connection to GraphDB.

**Returns:** `True` if successful

**Raises:** `GraphDBError` on failure

#### `get_triple_count(named_graph=None)`

Get the count of triples in the repository or named graph.

**Parameters:**
- `named_graph`: Optional named graph URI

**Returns:** Number of triples (int)

**Raises:** `GraphDBError` on failure

#### `clear_repository(named_graph=None)`

Clear all triples from the repository or named graph.

**WARNING:** This operation is destructive and cannot be undone.

**Parameters:**
- `named_graph`: Optional named graph URI to clear

**Returns:** `True` if successful

**Raises:** `GraphDBError` on failure

## Testing

Run the test suite:

```bash
pytest tests/core/knowledge_graph/ -v
```

Run specific test:

```bash
pytest tests/core/knowledge_graph/test_graphdb_client.py::TestRoundTrip::test_basic_roundtrip -v
```

## Architecture

- **RDFLib**: Used for in-memory RDF graph manipulation and serialization
- **SPARQLWrapper**: Used for communicating with remote SPARQL endpoints
- **GraphDB REST API**: Triple insertion via POST /statements, queries via GET

## GraphDB Configuration

The client connects to:
- **Endpoint**: `http://localhost:7200/repositories/carbonbim-thailand`
- **Repository**: `carbonbim-thailand`
- **Inference**: RDFS inference enabled

## Related Documentation

- [GraphDB Documentation](http://graphdb.ontotext.com/documentation/)
- [RDFLib Documentation](https://rdflib.readthedocs.io/)
- [SPARQL 1.1 Specification](https://www.w3.org/TR/sparql11-query/)

## Development

See `example_usage.py` for a complete working example.

## License

Apache-2.0

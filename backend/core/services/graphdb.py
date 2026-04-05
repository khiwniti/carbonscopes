import os
from typing import Any, Dict, List
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import urljoin

# Load configuration from environment variables
GRAPHDB_HOST = os.getenv("GRAPHDB_HOST", "graphdb")
GRAPHDB_PORT = os.getenv("GRAPHDB_PORT", "7200")
GRAPHDB_REPOSITORY = os.getenv("GRAPHDB_REPOSITORY", "thai-carbon-standards")
GRAPHDB_TIMEOUT = float(os.getenv("GRAPHDB_TIMEOUT", "5.0"))
GRAPHDB_POOL_SIZE = int(os.getenv("GRAPHDB_POOL_SIZE", "20"))

# Simple singleton pool (list of Graph instances)
_pool: List[Graph] = []


def _create_graph() -> Graph:
    """Create a new RDFLib Graph bound to the GraphDB SPARQL endpoint."""
    endpoint = f"http://{GRAPHDB_HOST}:{GRAPHDB_PORT}/repositories/{GRAPHDB_REPOSITORY}"
    g = Graph(store="SPARQLStore")
    g.open(endpoint)
    return g


def get_graph() -> Graph:
    """Return a GraphDB‑connected RDFLib Graph if the server is reachable,
    otherwise fall back to an in‑memory Graph. This enables write‑able graphs
    for unit tests without requiring a running GraphDB instance.
    """
    # Try to obtain a pooled Graph first
    if _pool:
        return _pool.pop()
    # Attempt to create a connection to the external GraphDB endpoint
    try:
        g = _create_graph()
        # Perform a lightweight query to verify connectivity
        test_query = "ASK { }"
        wrapper = SPARQLWrapper(
            urljoin(
                f"http://{GRAPHDB_HOST}:{GRAPHDB_PORT}/repositories/",
                GRAPHDB_REPOSITORY,
            )
        )
        wrapper.setReturnFormat(JSON)
        wrapper.setQuery(test_query)
        wrapper.setTimeout(GRAPHDB_TIMEOUT)
        wrapper.query()
        return g
    except Exception:
        # If any error occurs (e.g., server unavailable), fall back to in‑memory Graph
        return Graph()


# Optional bulk upsert utility for adding many triples efficiently
from typing import Tuple


def bulk_upsert(triples: List[Tuple[Any, Any, Any]]) -> Graph:
    """Create a Graph (connected or in‑memory) and add a list of triples.

    Args:
        triples: Iterable of (subject, predicate, object) RDF terms (as strings or rdflib.URIRefs).
    Returns:
        Graph instance containing the added triples.
    """
    g = get_graph()
    for s, p, o in triples:
        g.add((s, p, o))
    return g


def release_graph(g: Graph) -> None:
    """Return a Graph instance to the pool for reuse."""
    if len(_pool) < GRAPHDB_POOL_SIZE:
        _pool.append(g)


def sparql_query(query: str) -> List[Dict[str, Any]]:
    """Execute a SPARQL SELECT query and return results as list of bindings.

    Args:
        query: SPARQL SELECT query string.
    Returns:
        List of dictionaries where keys are variable names.
    """
    endpoint = f"http://{GRAPHDB_HOST}:{GRAPHDB_PORT}/repositories/{GRAPHDB_REPOSITORY}"
    wrapper = SPARQLWrapper(endpoint)
    wrapper.setReturnFormat(JSON)
    wrapper.setQuery(query)
    wrapper.setTimeout(GRAPHDB_TIMEOUT)
    try:
        results = wrapper.query().convert()
        return results.get("results", {}).get("bindings", [])
    except Exception as e:
        raise RuntimeError(f"SPARQL query failed: {e}")

import pytest
from pathlib import Path
from rdflib import Graph


@pytest.fixture
def edge_graph():
    g = Graph()
    ontology_path = (
        Path(__file__).parents[2] / "knowledge_graph" / "ontologies" / "edge-v3.ttl"
    )
    g.parse(str(ontology_path), format="turtle")
    return g


def test_edge_certification_query(edge_graph):
    query_path = (
        Path(__file__).parents[2]
        / "knowledge_graph"
        / "queries"
        / "edge_certification.sparql"
    )
    q = query_path.read_text()
    res = edge_graph.query(q)
    rows = list(res)
    assert len(rows) == 1
    # Expect PASS because bound 0.25 >= threshold 0.20
    assert rows[0].status.toPython() == "PASS"

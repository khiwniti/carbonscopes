import pytest
from pathlib import Path
from rdflib import Graph


@pytest.fixture
def trees_graph():
    g = Graph()
    # Load TGO ontology with sample material data (use sample JSON loader)
    ontology_path = (
        Path(__file__).parents[2]
        / "knowledge_graph"
        / "ontologies"
        / "trees-nc-1.1.ttl"
    )
    g.parse(str(ontology_path), format="turtle")
    # Load sample TGO materials to provide data for query
    from core.knowledge_graph.tgo_loader import load_from_json_file

    sample_file = Path(__file__).parent / "sample_data" / "tgo_materials_sample.json"
    # Need a graph bound to a SPARQL store for load? For test we just add triples directly
    # We'll use the same loader but with a plain Graph (no endpoint)
    load_from_json_file(sample_file, g)
    return g


def test_trees_compliance_query(trees_graph):
    query_path = (
        Path(__file__).parents[2]
        / "knowledge_graph"
        / "queries"
        / "trees_compliance.sparql"
    )
    q = query_path.read_text()
    res = trees_graph.query(q)
    rows = list(res)
    assert len(rows) == 1
    # greenPercentage will be 0 or low; ensure returned status matches expectation (likely FAIL)
    # Since sample data has no trees:hasGreenLabel property, expect 0 greenPercentage and FAIL
    assert rows[0].mr1Status.toPython() == "FAIL"

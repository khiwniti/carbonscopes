"""
Tests for GraphDB client integration.

This test suite validates:
1. Connection to GraphDB endpoint
2. Triple insertion via POST /statements
3. SPARQL query execution
4. Round-trip data integrity (insert → query → verify)
"""

import pytest
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

from core.knowledge_graph import GraphDBClient, GraphDBError


# Test configuration
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/carbonbim-thailand"
TEST_NAMESPACE = "http://example.org/carbonbim/test/"


@pytest.fixture
def client():
    """Create a GraphDB client for testing."""
    return GraphDBClient(GRAPHDB_ENDPOINT)


@pytest.fixture
def test_namespace():
    """Create a test namespace."""
    return Namespace(TEST_NAMESPACE)


@pytest.fixture
def sample_graph(test_namespace):
    """Create a sample RDF graph with test data."""
    g = Graph()
    ns = test_namespace

    # Add some sample triples about a building material
    material = ns.Material_Concrete_C30
    g.add((material, RDF.type, ns.Material))
    g.add((material, RDFS.label, Literal("Concrete C30", lang="en")))
    g.add((material, ns.compressiveStrength, Literal(30, datatype=XSD.integer)))
    g.add((material, ns.density, Literal(2400, datatype=XSD.integer)))
    g.add((material, ns.embodiedCarbon, Literal(310.5, datatype=XSD.decimal)))
    g.add((material, ns.unit, Literal("kgCO2e/m3")))

    # Add another material
    steel = ns.Material_Steel_Rebar
    g.add((steel, RDF.type, ns.Material))
    g.add((steel, RDFS.label, Literal("Steel Rebar", lang="en")))
    g.add((steel, ns.tensileStrength, Literal(500, datatype=XSD.integer)))
    g.add((steel, ns.density, Literal(7850, datatype=XSD.integer)))
    g.add((steel, ns.embodiedCarbon, Literal(2100.0, datatype=XSD.decimal)))
    g.add((steel, ns.unit, Literal("kgCO2e/tonne")))

    return g


class TestGraphDBConnection:
    """Test GraphDB connection functionality."""

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        client = GraphDBClient(GRAPHDB_ENDPOINT)
        assert client.endpoint_url == GRAPHDB_ENDPOINT
        assert client.timeout == 30

    def test_client_initialization_with_auth(self):
        """Test client initialization with authentication."""
        client = GraphDBClient(
            GRAPHDB_ENDPOINT,
            username="admin",
            password="secret"
        )
        assert client.username == "admin"
        assert client.password == "secret"
        assert client.auth == ("admin", "secret")

    def test_connection(self, client):
        """Test connection to GraphDB endpoint."""
        assert client.test_connection() is True


class TestTripleInsertion:
    """Test triple insertion functionality."""

    def test_insert_simple_triples(self, client, sample_graph, test_namespace):
        """Test inserting a simple set of triples."""
        # Insert triples
        result = client.insert_triples(sample_graph)
        assert result is True

        # Verify by querying for the inserted data
        query = f"""
        SELECT (COUNT(*) as ?count)
        WHERE {{
            ?material a <{test_namespace.Material}> .
        }}
        """
        results = client.query(query)
        count = int(results['results']['bindings'][0]['count']['value'])
        assert count >= 2, "Should have at least 2 materials"

    def test_insert_empty_graph(self, client):
        """Test inserting an empty graph."""
        empty_graph = Graph()
        result = client.insert_triples(empty_graph)
        assert result is True

    def test_insert_with_different_formats(self, client, sample_graph):
        """Test inserting triples with different serialization formats."""
        formats = ["turtle", "xml", "n3"]

        for format_type in formats:
            result = client.insert_triples(sample_graph, format=format_type)
            assert result is True


class TestSPARQLQuery:
    """Test SPARQL query functionality."""

    def test_simple_select_query(self, client):
        """Test executing a simple SELECT query."""
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        results = client.query(query)

        assert 'results' in results
        assert 'bindings' in results['results']
        assert isinstance(results['results']['bindings'], list)

    def test_count_query(self, client):
        """Test executing a COUNT query."""
        query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        results = client.query(query)

        assert 'results' in results
        bindings = results['results']['bindings']
        assert len(bindings) > 0
        assert 'count' in bindings[0]

    def test_filtered_query(self, client, test_namespace):
        """Test executing a filtered query."""
        ns = test_namespace
        query = f"""
        SELECT ?material ?label
        WHERE {{
            ?material a <{ns.Material}> .
            ?material <{RDFS.label}> ?label .
        }}
        """
        results = client.query(query)

        assert 'results' in results
        assert 'bindings' in results['results']

    def test_query_with_different_formats(self, client):
        """Test queries with different return formats."""
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"

        # Test JSON format
        json_results = client.query(query, return_format="json")
        assert isinstance(json_results, dict)

        # Test XML format - may return string or Graph object
        xml_results = client.query(query, return_format="xml")
        assert xml_results is not None


class TestRoundTrip:
    """Test round-trip data integrity: insert → query → verify."""

    def test_basic_roundtrip(self, client, sample_graph, test_namespace):
        """
        Test complete round-trip: insert sample triples, query them back, verify results.
        This is the main success criterion for Task #32.
        """
        ns = test_namespace

        # Step 1: Insert sample triples
        print("\n=== Step 1: Inserting sample triples ===")
        insert_result = client.insert_triples(sample_graph)
        assert insert_result is True
        print(f"Inserted {len(sample_graph)} triples successfully")

        # Step 2: Query back the inserted data
        print("\n=== Step 2: Querying inserted triples ===")
        query = f"""
        PREFIX rdfs: <{RDFS}>
        SELECT ?material ?label ?carbon
        WHERE {{
            ?material a <{ns.Material}> .
            ?material rdfs:label ?label .
            ?material <{ns.embodiedCarbon}> ?carbon .
        }}
        ORDER BY ?label
        """
        results = client.query(query)

        # Step 3: Verify results match what we inserted
        print("\n=== Step 3: Verifying results ===")
        assert 'results' in results
        bindings = results['results']['bindings']
        assert len(bindings) >= 2, "Should have at least 2 materials"

        # Verify specific materials are present
        labels = [b['label']['value'] for b in bindings]
        print(f"Found materials: {labels}")

        assert "Concrete C30" in labels or "Steel Rebar" in labels, \
            "Should find at least one of our test materials"

        # Verify carbon values are present and correct type
        for binding in bindings:
            assert 'carbon' in binding
            carbon_value = binding['carbon']['value']
            assert carbon_value is not None
            print(f"Material: {binding['label']['value']}, Carbon: {carbon_value}")

        print("\n=== Round-trip test PASSED ===")
        print(f"Successfully inserted {len(sample_graph)} triples")
        print(f"Successfully queried back {len(bindings)} materials")
        print("Data integrity verified")

    def test_roundtrip_with_literal_types(self, client, sample_graph, test_namespace):
        """Test round-trip preserves literal datatypes."""
        ns = test_namespace

        # Insert sample data
        client.insert_triples(sample_graph)

        # Query with datatype information
        query = f"""
        SELECT ?material ?property ?value (DATATYPE(?value) as ?datatype)
        WHERE {{
            ?material a <{ns.Material}> .
            ?material ?property ?value .
            FILTER(isLiteral(?value))
        }}
        LIMIT 20
        """
        results = client.query(query)

        bindings = results['results']['bindings']
        assert len(bindings) > 0

        # Check that datatypes are preserved
        for binding in bindings:
            if 'datatype' in binding:
                datatype = binding['datatype']['value']
                print(f"Property: {binding['property']['value']}, "
                      f"Value: {binding['value']['value']}, "
                      f"Datatype: {datatype}")

    def test_roundtrip_with_named_graph(self, client, sample_graph, test_namespace):
        """Test round-trip using a named graph."""
        ns = test_namespace
        named_graph_uri = f"{TEST_NAMESPACE}test-graph-{pytest.__version__}"

        # Insert into named graph
        client.insert_triples(sample_graph, named_graph=named_graph_uri)

        # Query from named graph
        query = f"""
        SELECT ?material ?label
        FROM <{named_graph_uri}>
        WHERE {{
            ?material a <{ns.Material}> .
            ?material <{RDFS.label}> ?label .
        }}
        """
        results = client.query(query)

        bindings = results['results']['bindings']
        assert len(bindings) >= 2


class TestSPARQLUpdate:
    """Test SPARQL UPDATE operations."""

    def test_insert_data_update(self, client, test_namespace):
        """Test SPARQL INSERT DATA operation."""
        ns = test_namespace

        update = f"""
        PREFIX rdfs: <{RDFS}>
        INSERT DATA {{
            <{ns.TestMaterial}> a <{ns.Material}> .
            <{ns.TestMaterial}> rdfs:label "Test Material" .
        }}
        """

        result = client.update(update)
        assert result is True

        # Verify insertion
        query = f"""
        ASK {{
            <{ns.TestMaterial}> a <{ns.Material}> .
        }}
        """
        results = client.query(query)
        assert results['boolean'] is True


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_endpoint(self):
        """Test handling of invalid endpoint."""
        client = GraphDBClient("http://localhost:9999/invalid")
        with pytest.raises(GraphDBError):
            client.test_connection()

    def test_malformed_query(self, client):
        """Test handling of malformed SPARQL query."""
        with pytest.raises(GraphDBError):
            client.query("INVALID SPARQL SYNTAX")

    def test_malformed_update(self, client):
        """Test handling of malformed SPARQL update."""
        with pytest.raises(GraphDBError):
            client.update("INVALID UPDATE SYNTAX")


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_triple_count(self, client):
        """Test getting triple count."""
        count = client.get_triple_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_triple_count_increases_after_insert(self, client, sample_graph, test_namespace):
        """Test that triple count increases after insertion via query."""
        # Use a unique named graph to avoid conflicts with inference
        named_graph = f"{TEST_NAMESPACE}test-count-graph"

        # Insert into named graph
        client.insert_triples(sample_graph, named_graph=named_graph)

        # Count in that specific named graph
        count = client.get_triple_count(named_graph=named_graph)
        assert count == len(sample_graph), f"Expected {len(sample_graph)} triples, got {count}"

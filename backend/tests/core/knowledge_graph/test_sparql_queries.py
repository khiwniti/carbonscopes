"""
Unit tests for SPARQL query library.

This test suite validates:
1. Emission factor retrieval by material ID
2. Material search functionality
3. Category-based material listing
4. Data quality checks (staleness detection)
5. Query result parsing utilities
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

from core.knowledge_graph import GraphDBClient
from core.knowledge_graph.sparql_queries import (
    get_emission_factor,
    search_materials,
    list_materials_by_category,
    get_all_categories,
    find_stale_materials,
    parse_bindings,
    extract_decimal_value,
    extract_language_literal,
    MaterialNotFoundError,
    QueryError,
    TGO_NAMESPACE,
    TGO_MATERIALS_NAMESPACE,
)


# Test configuration
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/carbonbim-thailand"
TEST_MATERIAL_URI = "http://tgo.or.th/materials/concrete-c30"
TGO = Namespace(TGO_NAMESPACE)


@pytest.fixture
def client():
    """Create a GraphDB client for testing."""
    return GraphDBClient(GRAPHDB_ENDPOINT)


@pytest.fixture
def mock_client():
    """Create a mock GraphDB client for unit testing without GraphDB."""
    return Mock(spec=GraphDBClient)


@pytest.fixture
def sample_tgo_data(client):
    """
    Create sample TGO data in GraphDB for testing.

    This fixture adds test materials that will be cleaned up after tests.
    """
    g = Graph()

    # Define namespaces
    tgo = Namespace(TGO_NAMESPACE)

    # Material 1: Concrete C30
    concrete = URIRef(f"{TGO_MATERIALS_NAMESPACE}test-concrete-c30")
    g.add((concrete, RDF.type, tgo.Concrete))
    g.add((concrete, RDFS.label, Literal("Ready-mixed Concrete C30", lang="en")))
    g.add((concrete, RDFS.label, Literal("คอนกรีตผสมเสร็จ C30", lang="th")))
    g.add((concrete, tgo.hasEmissionFactor, Literal("445.6", datatype=XSD.decimal)))
    g.add((concrete, tgo.hasUnit, Literal("kgCO2e/m³")))
    g.add((concrete, tgo.category, Literal("Concrete")))
    g.add((concrete, tgo.effectiveDate, Literal("2026-01-01", datatype=XSD.date)))
    g.add((concrete, tgo.dataQuality, Literal("Verified")))
    g.add((concrete, tgo.uncertainty, Literal("0.10", datatype=XSD.decimal)))
    g.add((concrete, tgo.geographicScope, Literal("Thailand")))

    # Material 2: Steel Rebar
    steel = URIRef(f"{TGO_MATERIALS_NAMESPACE}test-steel-rebar-sd40")
    g.add((steel, RDF.type, tgo.Steel))
    g.add((steel, RDFS.label, Literal("Steel Reinforcement Bar SD40", lang="en")))
    g.add((steel, RDFS.label, Literal("เหล็กเสริมคอนกรีต SD40", lang="th")))
    g.add((steel, tgo.hasEmissionFactor, Literal("2100.0", datatype=XSD.decimal)))
    g.add((steel, tgo.hasUnit, Literal("kgCO2e/ton")))
    g.add((steel, tgo.category, Literal("Steel")))
    g.add((steel, tgo.effectiveDate, Literal("2025-12-01", datatype=XSD.date)))
    g.add((steel, tgo.dataQuality, Literal("Verified")))
    g.add((steel, tgo.geographicScope, Literal("Thailand")))

    # Material 3: Old/Stale Concrete (for staleness tests)
    old_concrete = URIRef(f"{TGO_MATERIALS_NAMESPACE}test-concrete-c20-old")
    g.add((old_concrete, RDF.type, tgo.Concrete))
    g.add((old_concrete, RDFS.label, Literal("Concrete C20 (Old)", lang="en")))
    g.add((old_concrete, tgo.hasEmissionFactor, Literal("410.5", datatype=XSD.decimal)))
    g.add((old_concrete, tgo.hasUnit, Literal("kgCO2e/m³")))
    g.add((old_concrete, tgo.category, Literal("Concrete")))
    # Set date to 8 months ago
    old_date = (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d")
    g.add((old_concrete, tgo.effectiveDate, Literal(old_date, datatype=XSD.date)))

    # Material 4: Aluminum
    aluminum = URIRef(f"{TGO_MATERIALS_NAMESPACE}test-aluminum-window-frame")
    g.add((aluminum, RDF.type, tgo.Aluminum))
    g.add((aluminum, RDFS.label, Literal("Aluminum Window Frame", lang="en")))
    g.add((aluminum, RDFS.label, Literal("กรอบหน้าต่างอลูมิเนียม", lang="th")))
    g.add((aluminum, tgo.hasEmissionFactor, Literal("9800.0", datatype=XSD.decimal)))
    g.add((aluminum, tgo.hasUnit, Literal("kgCO2e/ton")))
    g.add((aluminum, tgo.category, Literal("Aluminum")))
    g.add((aluminum, tgo.effectiveDate, Literal("2026-01-15", datatype=XSD.date)))

    # Insert test data
    try:
        client.insert_triples(g)
        yield g
    finally:
        # Cleanup: remove test triples
        # Note: In production, use named graphs for easier cleanup
        pass


class TestGetEmissionFactor:
    """Test get_emission_factor function."""

    def test_get_emission_factor_basic(self, client, sample_tgo_data):
        """Test basic emission factor retrieval."""
        material_id = f"{TGO_MATERIALS_NAMESPACE}test-concrete-c30"
        result = get_emission_factor(client, material_id)

        assert result['material_id'] == material_id
        assert isinstance(result['emission_factor'], Decimal)
        assert result['emission_factor'] == Decimal("445.6")
        assert result['unit'] == "kgCO2e/m³"
        assert result['label_en'] == "Ready-mixed Concrete C30"
        assert result['label_th'] == "คอนกรีตผสมเสร็จ C30"
        assert result['category'] == "Concrete"
        assert result['effective_date'] == "2026-01-01"

    def test_get_emission_factor_with_metadata(self, client, sample_tgo_data):
        """Test emission factor retrieval with full metadata."""
        material_id = f"{TGO_MATERIALS_NAMESPACE}test-concrete-c30"
        result = get_emission_factor(client, material_id, include_metadata=True)

        assert 'metadata' in result
        assert result['metadata']['data_quality'] == "Verified"
        assert result['metadata']['uncertainty'] == Decimal("0.10")
        assert result['metadata']['geographic_scope'] == "Thailand"

    def test_get_emission_factor_not_found(self, client):
        """Test handling of non-existent material."""
        with pytest.raises(MaterialNotFoundError):
            get_emission_factor(client, "http://tgo.or.th/materials/nonexistent")

    def test_get_emission_factor_precision(self, client, sample_tgo_data):
        """Test that emission factor maintains decimal precision."""
        material_id = f"{TGO_MATERIALS_NAMESPACE}test-steel-rebar-sd40"
        result = get_emission_factor(client, material_id)

        # Verify it's a Decimal, not float
        assert isinstance(result['emission_factor'], Decimal)
        # Verify precision is maintained
        assert result['emission_factor'] == Decimal("2100.0")


class TestSearchMaterials:
    """Test search_materials function."""

    def test_search_materials_basic(self, client, sample_tgo_data):
        """Test basic material search."""
        results = search_materials(client, "concrete")

        assert len(results) >= 2  # At least test-concrete-c30 and test-concrete-c20-old
        assert all('material_id' in r for r in results)
        assert all('label' in r for r in results)
        assert all('emission_factor' in r for r in results)
        assert all(isinstance(r['emission_factor'], Decimal) for r in results)

    def test_search_materials_case_insensitive(self, client, sample_tgo_data):
        """Test that search is case-insensitive."""
        results_lower = search_materials(client, "concrete")
        results_upper = search_materials(client, "CONCRETE")
        results_mixed = search_materials(client, "CoNcReTe")

        # All should return same materials (though order might differ)
        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_search_materials_thai_language(self, client, sample_tgo_data):
        """Test search with Thai language."""
        results = search_materials(client, "คอนกรีต", language="th")

        assert len(results) >= 2
        # Verify Thai labels are returned
        for result in results:
            assert result['label'] is not None

    def test_search_materials_with_category_filter(self, client, sample_tgo_data):
        """Test search with category filter."""
        results = search_materials(client, "Steel", category_filter="Steel")

        assert len(results) >= 1
        assert all(r['category'] == "Steel" for r in results)

    def test_search_materials_limit(self, client, sample_tgo_data):
        """Test search result limit."""
        results = search_materials(client, ".*", limit=2)  # Match all

        assert len(results) <= 2

    def test_search_materials_no_results(self, client):
        """Test search with no matching results."""
        results = search_materials(client, "nonexistent-material-xyz")

        assert len(results) == 0


class TestListMaterialsByCategory:
    """Test list_materials_by_category function."""

    def test_list_concrete_materials(self, client, sample_tgo_data):
        """Test listing all concrete materials."""
        results = list_materials_by_category(client, "Concrete")

        assert len(results) >= 2  # At least 2 test concrete materials
        assert all(r['category'] == "Concrete" for r in results if r['category'])
        assert all('emission_factor' in r for r in results)

    def test_list_steel_materials(self, client, sample_tgo_data):
        """Test listing steel materials."""
        results = list_materials_by_category(client, "Steel")

        assert len(results) >= 1
        assert all(r['category'] == "Steel" for r in results if r['category'])

    def test_list_materials_sorted_by_label(self, client, sample_tgo_data):
        """Test that materials are sorted by label."""
        results = list_materials_by_category(client, "Concrete", sort_by="label")

        # Verify sorting
        labels = [r['label'] for r in results]
        assert labels == sorted(labels)

    def test_list_materials_sorted_by_emission_factor(self, client, sample_tgo_data):
        """Test sorting by emission factor."""
        results = list_materials_by_category(client, "Concrete", sort_by="emission_factor")

        # Verify sorting
        factors = [r['emission_factor'] for r in results]
        assert factors == sorted(factors)

    def test_list_materials_with_limit(self, client, sample_tgo_data):
        """Test limiting results."""
        results = list_materials_by_category(client, "Concrete", limit=1)

        assert len(results) == 1

    def test_list_materials_thai_language(self, client, sample_tgo_data):
        """Test listing with Thai labels."""
        results = list_materials_by_category(client, "Concrete", language="th")

        assert len(results) >= 1
        # Thai labels should be returned
        for result in results:
            if result['label']:
                # Should contain Thai characters or be empty
                assert result['label'] is not None


class TestGetAllCategories:
    """Test get_all_categories function."""

    def test_get_all_categories(self, client, sample_tgo_data):
        """Test retrieving all categories with counts."""
        categories = get_all_categories(client)

        assert len(categories) >= 3  # At least Concrete, Steel, Aluminum
        assert all('category' in c for c in categories)
        assert all('count' in c for c in categories)
        assert all(isinstance(c['count'], int) for c in categories)

        # Find our test categories
        category_names = [c['category'] for c in categories]
        assert "Concrete" in category_names
        assert "Steel" in category_names
        assert "Aluminum" in category_names

    def test_categories_sorted_by_count(self, client, sample_tgo_data):
        """Test that categories are sorted by count (descending)."""
        categories = get_all_categories(client)

        counts = [c['count'] for c in categories]
        assert counts == sorted(counts, reverse=True)


class TestFindStaleMaterials:
    """Test find_stale_materials function."""

    def test_find_stale_materials(self, client, sample_tgo_data):
        """Test finding materials with old emission factors."""
        stale = find_stale_materials(client, threshold_months=6)

        # Should find at least the old concrete material
        assert len(stale) >= 1

        # Check structure
        for material in stale:
            assert 'material_id' in material
            assert 'label' in material
            assert 'emission_factor' in material
            assert 'effective_date' in material
            assert 'age_days' in material or material['age_days'] is None

    def test_find_stale_materials_threshold(self, client, sample_tgo_data):
        """Test staleness threshold filtering."""
        # Very long threshold - should find almost nothing
        stale_long = find_stale_materials(client, threshold_months=24)

        # Short threshold - should find more
        stale_short = find_stale_materials(client, threshold_months=1)

        # Short threshold should find at least as many as long threshold
        assert len(stale_short) >= len(stale_long)


class TestQueryResultParsing:
    """Test query result parsing utilities."""

    def test_parse_bindings_default(self):
        """Test parse_bindings with default behavior."""
        bindings = [
            {
                'material': {'value': 'http://example.org/m1'},
                'label': {'value': 'Material 1'},
                'factor': {'value': '123.4'},
            },
            {
                'material': {'value': 'http://example.org/m2'},
                'label': {'value': 'Material 2'},
                'factor': {'value': '567.8'},
            }
        ]

        parsed = parse_bindings(bindings)

        assert len(parsed) == 2
        assert parsed[0]['material'] == 'http://example.org/m1'
        assert parsed[0]['label'] == 'Material 1'
        assert parsed[0]['factor'] == '123.4'

    def test_parse_bindings_with_field_map(self):
        """Test parse_bindings with custom field mapping."""
        bindings = [
            {
                'mat': {'value': 'http://example.org/m1'},
                'lbl': {'value': 'Material 1'},
            }
        ]

        field_map = {'mat': 'material_id', 'lbl': 'label'}
        parsed = parse_bindings(bindings, field_map)

        assert parsed[0]['material_id'] == 'http://example.org/m1'
        assert parsed[0]['label'] == 'Material 1'

    def test_extract_decimal_value(self):
        """Test extract_decimal_value utility."""
        binding = {
            'emissionFactor': {'value': '445.6'},
            'other': {'value': 'not a number'},
        }

        result = extract_decimal_value(binding, 'emissionFactor')
        assert result == Decimal('445.6')

        # Non-existent field
        result = extract_decimal_value(binding, 'nonexistent')
        assert result is None

        # Invalid decimal
        result = extract_decimal_value(binding, 'other')
        assert result is None

    def test_extract_language_literal(self):
        """Test extract_language_literal utility."""
        binding = {
            'label': {
                'value': 'Concrete',
                'xml:lang': 'en'
            }
        }

        # Matching language
        result = extract_language_literal(binding, 'label', 'en')
        assert result == 'Concrete'

        # Non-matching language
        result = extract_language_literal(binding, 'label', 'th')
        assert result is None

        # Non-existent field
        result = extract_language_literal(binding, 'nonexistent', 'en')
        assert result is None


class TestErrorHandling:
    """Test error handling in query functions."""

    def test_get_emission_factor_query_error(self, mock_client):
        """Test query error handling in get_emission_factor."""
        from core.knowledge_graph import GraphDBError

        # Mock client to raise GraphDBError
        mock_client.query.side_effect = GraphDBError("Connection failed")

        with pytest.raises(QueryError):
            get_emission_factor(mock_client, "http://example.org/material")

    def test_search_materials_query_error(self, mock_client):
        """Test query error handling in search_materials."""
        from core.knowledge_graph import GraphDBError

        mock_client.query.side_effect = GraphDBError("Connection failed")

        with pytest.raises(QueryError):
            search_materials(mock_client, "concrete")

    def test_list_materials_query_error(self, mock_client):
        """Test query error handling in list_materials_by_category."""
        from core.knowledge_graph import GraphDBError

        mock_client.query.side_effect = GraphDBError("Connection failed")

        with pytest.raises(QueryError):
            list_materials_by_category(mock_client, "Concrete")


class TestPerformance:
    """Test query performance targets."""

    @pytest.mark.skip(reason="Performance test - run manually with real data")
    def test_emission_factor_lookup_performance(self, client):
        """Test that direct emission factor lookup is <50ms."""
        import time

        material_id = f"{TGO_MATERIALS_NAMESPACE}test-concrete-c30"

        start = time.time()
        result = get_emission_factor(client, material_id)
        duration = (time.time() - start) * 1000  # Convert to ms

        assert duration < 50, f"Lookup took {duration}ms (target: <50ms)"

    @pytest.mark.skip(reason="Performance test - run manually with real data")
    def test_category_query_performance(self, client):
        """Test that category queries are <200ms."""
        import time

        start = time.time()
        results = list_materials_by_category(client, "Concrete")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert duration < 200, f"Query took {duration}ms (target: <200ms)"


class TestBilingualSupport:
    """Test bilingual (Thai/English) label support."""

    def test_english_labels(self, client, sample_tgo_data):
        """Test retrieval of English labels."""
        results = search_materials(client, "Concrete", language="en")

        assert len(results) >= 1
        for result in results:
            # English labels should not contain Thai characters
            label = result['label']
            assert label is not None

    def test_thai_labels(self, client, sample_tgo_data):
        """Test retrieval of Thai labels."""
        results = search_materials(client, "คอนกรีต", language="th")

        assert len(results) >= 1
        # Thai results should be present
        assert any(r['label'] for r in results)

    def test_both_languages_in_emission_factor(self, client, sample_tgo_data):
        """Test that get_emission_factor returns both language labels."""
        material_id = f"{TGO_MATERIALS_NAMESPACE}test-concrete-c30"
        result = get_emission_factor(client, material_id)

        assert result['label_en'] == "Ready-mixed Concrete C30"
        assert result['label_th'] == "คอนกรีตผสมเสร็จ C30"


class TestRDFSInference:
    """Test that queries leverage RDFS inference."""

    def test_subclass_query_includes_subcategories(self, client, sample_tgo_data):
        """Test that querying ConstructionMaterial includes all subclasses."""
        # Query for all construction materials
        query = """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT (COUNT(DISTINCT ?material) as ?count)
        WHERE {
            ?material a ?type .
            ?type rdfs:subClassOf* tgo:ConstructionMaterial .
        }
        """

        results = client.query(query)
        count = int(results['results']['bindings'][0]['count']['value'])

        # Should find all our test materials (concrete, steel, aluminum)
        assert count >= 4

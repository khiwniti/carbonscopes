"""
SPARQL Query Library for TGO Construction Materials.

This module provides high-level functions for querying the TGO knowledge graph,
including:
- Material emission factor lookups
- Material search and filtering
- Category-based queries
- Bilingual label support (Thai + English)

All queries leverage GraphDB RDFS inference for automatic subclass handling.

Performance targets:
- Direct lookups: <50ms
- Category queries: <200ms
- Full-text search: <500ms

Example:
    >>> from core.knowledge_graph import GraphDBClient, get_emission_factor
    >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    >>> result = get_emission_factor(client, "http://tgo.or.th/materials/concrete-c30")
    >>> print(result['emission_factor'])
    445.6
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from .graphdb_client import GraphDBClient, GraphDBError


logger = logging.getLogger(__name__)


# TGO Ontology namespace
TGO_NAMESPACE = "http://tgo.or.th/ontology#"
TGO_MATERIALS_NAMESPACE = "http://tgo.or.th/materials/"


class MaterialNotFoundError(Exception):
    """Raised when a material cannot be found in the knowledge graph."""

    pass


class QueryError(Exception):
    """Raised when a SPARQL query fails."""

    pass


def get_emission_factor(
    client: GraphDBClient,
    material_id: str,
    version: Optional[str] = None,
    include_metadata: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve the emission factor for a specific material.

    Args:
        client: GraphDBClient instance
        material_id: Material URI (e.g., "http://tgo.or.th/materials/concrete-c30")
        version: Optional version URI (e.g., "http://tgo.or.th/versions/2026-03")
                If None, queries the latest version
        include_metadata: If True, includes full metadata (source, quality, uncertainty)

    Returns:
        Dictionary containing:
            - material_id: Material URI
            - emission_factor: Emission factor as Decimal
            - unit: Unit string (e.g., "kgCO2e/m³")
            - label_en: English label
            - label_th: Thai label
            - category: Material category
            - effective_date: Date when emission factor became effective
            - metadata: Additional metadata (if include_metadata=True)

    Raises:
        MaterialNotFoundError: If material is not found
        QueryError: If query execution fails

    Example:
        >>> result = get_emission_factor(client, "http://tgo.or.th/materials/concrete-c30")
        >>> print(f"Emission factor: {result['emission_factor']} {result['unit']}")
        Emission factor: 445.6 kgCO2e/m³
    """
    try:
        # Build the query based on whether version is specified
        if version:
            graph_clause = f"GRAPH <{version}> {{"
            graph_close = "}"
        else:
            graph_clause = ""
            graph_close = ""

        query = f"""
        PREFIX tgo: <{TGO_NAMESPACE}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?emissionFactor ?unit ?labelEN ?labelTH ?category ?effectiveDate
               ?sourceDocument ?dataQuality ?uncertainty ?geographicScope
        WHERE {{
            {graph_clause}
                <{material_id}> tgo:hasEmissionFactor ?emissionFactor ;
                                tgo:hasUnit ?unit .

                OPTIONAL {{ <{material_id}> rdfs:label ?labelEN FILTER(lang(?labelEN) = "en") }}
                OPTIONAL {{ <{material_id}> rdfs:label ?labelTH FILTER(lang(?labelTH) = "th") }}
                OPTIONAL {{ <{material_id}> tgo:category ?category }}
                OPTIONAL {{ <{material_id}> tgo:effectiveDate ?effectiveDate }}
                OPTIONAL {{ <{material_id}> tgo:sourceDocument ?sourceDocument }}
                OPTIONAL {{ <{material_id}> tgo:dataQuality ?dataQuality }}
                OPTIONAL {{ <{material_id}> tgo:uncertainty ?uncertainty }}
                OPTIONAL {{ <{material_id}> tgo:geographicScope ?geographicScope }}
            {graph_close}
        }}
        LIMIT 1
        """

        results = client.query(query)
        bindings = results.get("results", {}).get("bindings", [])

        if not bindings:
            raise MaterialNotFoundError(f"Material not found: {material_id}")

        binding = bindings[0]

        # Parse emission factor as Decimal for precision
        emission_factor = Decimal(binding["emissionFactor"]["value"])

        result = {
            "material_id": material_id,
            "emission_factor": emission_factor,
            "unit": binding["unit"]["value"],
            "label_en": binding.get("labelEN", {}).get("value"),
            "label_th": binding.get("labelTH", {}).get("value"),
            "category": binding.get("category", {}).get("value"),
            "effective_date": binding.get("effectiveDate", {}).get("value"),
        }

        if include_metadata:
            result["metadata"] = {
                "source_document": binding.get("sourceDocument", {}).get("value"),
                "data_quality": binding.get("dataQuality", {}).get("value"),
                "uncertainty": Decimal(binding["uncertainty"]["value"])
                if "uncertainty" in binding
                else None,
                "geographic_scope": binding.get("geographicScope", {}).get("value"),
            }

        logger.debug(
            f"Retrieved emission factor for {material_id}: {emission_factor} {result['unit']}"
        )
        return result

    except MaterialNotFoundError:
        raise
    except GraphDBError as e:
        raise QueryError(f"Failed to query emission factor: {str(e)}") from e
    except Exception as e:
        raise QueryError(f"Unexpected error querying emission factor: {str(e)}") from e


def search_materials(
    client: GraphDBClient,
    query_string: str,
    language: str = "en",
    limit: int = 20,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search for materials by name using full-text or regex matching.

    Args:
        client: GraphDBClient instance
        query_string: Search string (case-insensitive)
        language: Language for label matching ("en" or "th", default: "en")
        limit: Maximum number of results (default: 20)
        category_filter: Optional category to filter by (e.g., "Concrete", "Steel")

    Returns:
        List of dictionaries, each containing:
            - material_id: Material URI
            - label: Material label in requested language
            - category: Material category
            - emission_factor: Emission factor as Decimal
            - unit: Unit string
            - effective_date: Date when emission factor became effective

    Raises:
        QueryError: If query execution fails

    Example:
        >>> results = search_materials(client, "concrete", language="en")
        >>> for material in results:
        ...     print(f"{material['label']}: {material['emission_factor']} {material['unit']}")
        Ready-mixed Concrete C30: 445.6 kgCO2e/m³
        Concrete Block: 125.3 kgCO2e/piece
    """
    try:
        # Build category filter clause
        category_clause = ""
        if category_filter:
            category_clause = f'FILTER(?category = "{category_filter}")'

        # Use REGEX for flexible matching (case-insensitive)
        query = f"""
        PREFIX tgo: <{TGO_NAMESPACE}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?category ?emissionFactor ?unit ?effectiveDate
        WHERE {{
            ?material a ?type ;
                     rdfs:label ?label ;
                     tgo:hasEmissionFactor ?emissionFactor ;
                     tgo:hasUnit ?unit .

            ?type rdfs:subClassOf* tgo:ConstructionMaterial .

            OPTIONAL {{ ?material tgo:category ?category }}
            OPTIONAL {{ ?material tgo:effectiveDate ?effectiveDate }}

            FILTER(lang(?label) = "{language}" || lang(?label) = "")
            FILTER(REGEX(?label, "{query_string}", "i"))
            {category_clause}
        }}
        ORDER BY ?label
        LIMIT {limit}
        """

        results = client.query(query)
        bindings = results.get("results", {}).get("bindings", [])

        materials = []
        for binding in bindings:
            material = {
                "material_id": binding["material"]["value"],
                "label": binding["label"]["value"],
                "category": binding.get("category", {}).get("value"),
                "emission_factor": Decimal(binding["emissionFactor"]["value"]),
                "unit": binding["unit"]["value"],
                "effective_date": binding.get("effectiveDate", {}).get("value"),
            }
            materials.append(material)

        logger.debug(f"Search for '{query_string}' returned {len(materials)} results")
        return materials

    except GraphDBError as e:
        raise QueryError(f"Failed to search materials: {str(e)}") from e
    except Exception as e:
        raise QueryError(f"Unexpected error searching materials: {str(e)}") from e


def list_materials_by_category(
    client: GraphDBClient,
    category: str,
    language: str = "en",
    include_subcategories: bool = True,
    sort_by: str = "label",
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    List all materials in a specific category.

    Args:
        client: GraphDBClient instance
        category: Category name (e.g., "Concrete", "Steel", "Aluminum")
        language: Language for labels ("en" or "th", default: "en")
        include_subcategories: If True, includes materials from subclasses (via RDFS inference)
        sort_by: Sort field ("label", "emission_factor", "effective_date")
        limit: Optional maximum number of results

    Returns:
        List of dictionaries, each containing:
            - material_id: Material URI
            - label: Material label
            - type: RDF type URI
            - category: Material category
            - emission_factor: Emission factor as Decimal
            - unit: Unit string
            - effective_date: Date when emission factor became effective

    Raises:
        QueryError: If query execution fails

    Example:
        >>> concretes = list_materials_by_category(client, "Concrete")
        >>> for material in concretes:
        ...     print(f"{material['label']}: {material['emission_factor']}")
        Concrete C15: 380.2
        Concrete C20: 410.5
        Concrete C30: 445.6
    """
    try:
        # Map sort field
        sort_mapping = {
            "label": "?label",
            "emission_factor": "?emissionFactor",
            "effective_date": "DESC(?effectiveDate)",
        }
        order_by = sort_mapping.get(sort_by, "?label")

        # Build limit clause
        limit_clause = f"LIMIT {limit}" if limit else ""

        # Build the query
        if include_subcategories:
            # Use RDFS inference to get all materials in category and subcategories
            type_clause = f"?type rdfs:subClassOf* tgo:{category} ."
        else:
            # Direct type match only
            type_clause = f"?material a tgo:{category} ."

        query = f"""
        PREFIX tgo: <{TGO_NAMESPACE}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?type ?category ?emissionFactor ?unit ?effectiveDate
        WHERE {{
            ?material a ?type ;
                     rdfs:label ?label ;
                     tgo:hasEmissionFactor ?emissionFactor ;
                     tgo:hasUnit ?unit .

            {type_clause}

            OPTIONAL {{ ?material tgo:category ?category }}
            OPTIONAL {{ ?material tgo:effectiveDate ?effectiveDate }}

            FILTER(lang(?label) = "{language}" || lang(?label) = "")
        }}
        ORDER BY {order_by}
        {limit_clause}
        """

        results = client.query(query)
        bindings = results.get("results", {}).get("bindings", [])

        materials = []
        for binding in bindings:
            material = {
                "material_id": binding["material"]["value"],
                "label": binding["label"]["value"],
                "type": binding["type"]["value"],
                "category": binding.get("category", {}).get("value", category),
                "emission_factor": Decimal(binding["emissionFactor"]["value"]),
                "unit": binding["unit"]["value"],
                "effective_date": binding.get("effectiveDate", {}).get("value"),
            }
            materials.append(material)

        logger.debug(f"Listed {len(materials)} materials in category '{category}'")
        return materials

    except GraphDBError as e:
        raise QueryError(f"Failed to list materials by category: {str(e)}") from e
    except Exception as e:
        raise QueryError(
            f"Unexpected error listing materials by category: {str(e)}"
        ) from e


def get_all_categories(client: GraphDBClient) -> List[Dict[str, Any]]:
    """
    Retrieve all available material categories with counts.

    Args:
        client: GraphDBClient instance

    Returns:
        List of dictionaries, each containing:
            - category: Category name
            - count: Number of materials in category
            - label_en: English category label
            - label_th: Thai category label

    Raises:
        QueryError: If query execution fails

    Example:
        >>> categories = get_all_categories(client)
        >>> for cat in categories:
        ...     print(f"{cat['category']}: {cat['count']} materials")
        Concrete: 45 materials
        Steel: 23 materials
    """
    try:
        query = f"""
        PREFIX tgo: <{TGO_NAMESPACE}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?category (COUNT(DISTINCT ?material) as ?count)
        WHERE {{
            ?material a ?type ;
                     tgo:category ?category .
            ?type rdfs:subClassOf* tgo:ConstructionMaterial .
        }}
        GROUP BY ?category
        ORDER BY DESC(?count)
        """

        results = client.query(query)
        bindings = results.get("results", {}).get("bindings", [])

        categories = []
        for binding in bindings:
            category = {
                "category": binding["category"]["value"],
                "count": int(binding["count"]["value"]),
            }
            categories.append(category)

        logger.debug(f"Retrieved {len(categories)} categories")
        return categories

    except GraphDBError as e:
        raise QueryError(f"Failed to get categories: {str(e)}") from e
    except Exception as e:
        raise QueryError(f"Unexpected error getting categories: {str(e)}") from e


def find_stale_materials(
    client: GraphDBClient, threshold_months: int = 6
) -> List[Dict[str, Any]]:
    """
    Find materials with emission factors older than the threshold.

    This is used for data quality monitoring and staleness warnings.

    Args:
        client: GraphDBClient instance
        threshold_months: Age threshold in months (default: 6)

    Returns:
        List of dictionaries, each containing:
            - material_id: Material URI
            - label: Material label
            - category: Material category
            - emission_factor: Emission factor value
            - effective_date: Date when emission factor became effective
            - age_days: Age in days

    Raises:
        QueryError: If query execution fails

    Example:
        >>> stale = find_stale_materials(client, threshold_months=6)
        >>> print(f"Found {len(stale)} stale materials")
        Found 12 stale materials
    """
    try:
        # Calculate threshold date
        threshold_date = datetime.now() - timedelta(days=threshold_months * 30)
        threshold_str = threshold_date.strftime("%Y-%m-%d")

        query = f"""
        PREFIX tgo: <{TGO_NAMESPACE}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?material ?label ?category ?emissionFactor ?effectiveDate
               (xsd:integer((NOW() - ?effectiveDate) / 86400) as ?ageDays)
        WHERE {{
            ?material tgo:effectiveDate ?effectiveDate ;
                     rdfs:label ?label ;
                     tgo:hasEmissionFactor ?emissionFactor .

            OPTIONAL {{ ?material tgo:category ?category }}

            FILTER(?effectiveDate < "{threshold_str}"^^xsd:date)
            FILTER(lang(?label) = "en" || lang(?label) = "")
        }}
        ORDER BY ?effectiveDate
        """

        results = client.query(query)
        bindings = results.get("results", {}).get("bindings", [])

        materials = []
        for binding in bindings:
            material = {
                "material_id": binding["material"]["value"],
                "label": binding["label"]["value"],
                "category": binding.get("category", {}).get("value"),
                "emission_factor": Decimal(binding["emissionFactor"]["value"]),
                "effective_date": binding["effectiveDate"]["value"],
                "age_days": int(binding["ageDays"]["value"])
                if "ageDays" in binding
                else None,
            }
            materials.append(material)

        logger.debug(
            f"Found {len(materials)} stale materials (>{threshold_months} months old)"
        )
        return materials

    except GraphDBError as e:
        raise QueryError(f"Failed to find stale materials: {str(e)}") from e
    except Exception as e:
        raise QueryError(f"Unexpected error finding stale materials: {str(e)}") from e


def parse_bindings(
    bindings: List[Dict[str, Any]], field_map: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Parse SPARQL query result bindings into a more convenient format.

    This is a utility function for processing raw SPARQL JSON results.

    Args:
        bindings: List of SPARQL result bindings
        field_map: Optional mapping of result fields to output keys

    Returns:
        List of dictionaries with simplified structure

    Example:
        >>> results = client.query("SELECT ?material ?label WHERE { ... }")
        >>> parsed = parse_bindings(results['results']['bindings'])
        >>> for item in parsed:
        ...     print(item['material'], item['label'])
    """
    if not field_map:
        # Default: extract all fields
        parsed = []
        for binding in bindings:
            item = {}
            for key, value_obj in binding.items():
                item[key] = value_obj.get("value")
            parsed.append(item)
        return parsed
    else:
        # Use field map
        parsed = []
        for binding in bindings:
            item = {}
            for source_key, target_key in field_map.items():
                if source_key in binding:
                    item[target_key] = binding[source_key].get("value")
            parsed.append(item)
        return parsed


def extract_decimal_value(binding: Dict[str, Any], field: str) -> Optional[Decimal]:
    """
    Extract a decimal value from a SPARQL binding.

    Args:
        binding: SPARQL result binding
        field: Field name to extract

    Returns:
        Decimal value or None if field is not present

    Example:
        >>> emission_factor = extract_decimal_value(binding, 'emissionFactor')
    """
    if field in binding:
        try:
            return Decimal(binding[field]["value"])
        except (KeyError, ValueError, TypeError, Exception):
            return None
    return None


def extract_language_literal(
    binding: Dict[str, Any], field: str, language: str = "en"
) -> Optional[str]:
    """
    Extract a language-tagged literal from a SPARQL binding.

    Args:
        binding: SPARQL result binding
        field: Field name to extract
        language: Language tag to match (default: "en")

    Returns:
        String value or None if field is not present or language doesn't match

    Example:
        >>> label_en = extract_language_literal(binding, 'label', 'en')
        >>> label_th = extract_language_literal(binding, 'label', 'th')
    """
    if field in binding:
        value_obj = binding[field]
        if value_obj.get("xml:lang") == language:
            return value_obj.get("value")
    return None

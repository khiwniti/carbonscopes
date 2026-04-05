"""
Knowledge Graph module for RDF triple management and SPARQL query execution.

This module provides integration with GraphDB for storing and querying RDF triples,
as well as versioning support for TGO emission factor data and high-level SPARQL
query functions for material emission factor lookups.
"""

from .graphdb_client import GraphDBClient, GraphDBError
from .versioning import VersionManager, VersionManagerError
from .sparql_queries import (
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
)

__all__ = [
    "GraphDBClient",
    "GraphDBError",
    "VersionManager",
    "VersionManagerError",
    "get_emission_factor",
    "search_materials",
    "list_materials_by_category",
    "get_all_categories",
    "find_stale_materials",
    "parse_bindings",
    "extract_decimal_value",
    "extract_language_literal",
    "MaterialNotFoundError",
    "QueryError",
]

"""
Named Graph Versioning for TGO Emission Factor Data.

This package provides version management utilities for TGO (Thailand Greenhouse
Gas Management Organization) emission factor data stored in GraphDB.

Main Components:
    - VersionManager: Core versioning operations
    - SPARQL query templates: Reusable versioning queries
    - Migration workflow documentation

Example:
    >>> from suna.backend.core.knowledge_graph.versioning import VersionManager
    >>> from suna.backend.core.knowledge_graph.graphdb_client import GraphDBClient
    >>>
    >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    >>> vm = VersionManager(client)
    >>>
    >>> # Check for stale data
    >>> stale = vm.find_stale_factors()
    >>> print(f"Found {len(stale)} stale emission factors")
"""

from .version_manager import VersionManager, VersionManagerError

__version__ = "1.0.0"

__all__ = ['VersionManager', 'VersionManagerError']

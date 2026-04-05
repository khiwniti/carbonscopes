"""
Named Graph Versioning System for TGO Emission Factor Data.

This module implements the versioning strategy for TGO (Thailand Greenhouse Gas
Management Organization) emission factor data stored in GraphDB named graphs.

Version Naming Convention:
    http://tgo.or.th/versions/YYYY-MM

    Examples:
    - http://tgo.or.th/versions/2024-12
    - http://tgo.or.th/versions/2025-01
    - http://tgo.or.th/versions/2026-03

Key Features:
    - Automated staleness detection (>6 months old)
    - Version comparison queries
    - Migration workflow support
    - Version metadata management

Usage:
    >>> from suna.backend.core.knowledge_graph.versioning import VersionManager
    >>> from suna.backend.core.knowledge_graph.graphdb_client import GraphDBClient
    >>>
    >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    >>> vm = VersionManager(client)
    >>>
    >>> # Check for stale data
    >>> stale = vm.find_stale_factors(months=6)
    >>>
    >>> # List all versions
    >>> versions = vm.list_versions()
    >>>
    >>> # Compare versions
    >>> changes = vm.compare_versions("2024-12", "2025-01")
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dateutil.relativedelta import relativedelta

from ..graphdb_client import GraphDBClient, GraphDBError


logger = logging.getLogger(__name__)


class VersionManagerError(Exception):
    """Base exception for VersionManager errors."""
    pass


class VersionManager:
    """
    Manages versioned TGO emission factor data in GraphDB named graphs.

    This class provides utilities for:
    - Creating and validating version URIs
    - Finding stale emission factors
    - Listing available versions
    - Comparing differences between versions
    - Managing version metadata

    Args:
        client: GraphDBClient instance for SPARQL operations
        base_uri: Base URI for version named graphs (default: http://tgo.or.th/versions)
        staleness_threshold_months: Number of months before data is considered stale (default: 6)

    Example:
        >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
        >>> vm = VersionManager(client)
        >>> stale_factors = vm.find_stale_factors()
    """

    def __init__(
        self,
        client: GraphDBClient,
        base_uri: str = "http://tgo.or.th/versions",
        staleness_threshold_months: int = 6
    ):
        """Initialize the VersionManager."""
        self.client = client
        self.base_uri = base_uri.rstrip('/')
        self.staleness_threshold_months = staleness_threshold_months
        logger.info(f"Initialized VersionManager with base URI: {self.base_uri}")

    @staticmethod
    def _sanitize_uri(uri: str) -> str:
        """
        Sanitize a URI to prevent SPARQL injection.

        Args:
            uri: URI string to sanitize

        Returns:
            Sanitized URI

        Raises:
            ValueError: If URI contains invalid characters
        """
        # Only allow valid URI characters
        # Reject any URIs containing SPARQL special characters that could be injection attempts
        dangerous_chars = ['"', "'", '\\', '\n', '\r', '\t', '}', '{']
        for char in dangerous_chars:
            if char in uri:
                raise ValueError(f"URI contains invalid character: {char}")

        # Validate it's a proper URI format
        if not (uri.startswith('http://') or uri.startswith('https://')):
            raise ValueError("URI must start with http:// or https://")

        return uri

    def create_version_uri(self, year: int, month: int) -> str:
        """
        Create a version URI from year and month.

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Version URI string (e.g., http://tgo.or.th/versions/2024-12)

        Raises:
            ValueError: If month is not between 1 and 12

        Example:
            >>> vm.create_version_uri(2024, 12)
            'http://tgo.or.th/versions/2024-12'
        """
        if not 1 <= month <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {month}")

        return f"{self.base_uri}/{year:04d}-{month:02d}"

    def parse_version_uri(self, version_uri: str) -> Tuple[int, int]:
        """
        Parse a version URI to extract year and month.

        Args:
            version_uri: Version URI (e.g., http://tgo.or.th/versions/2024-12)

        Returns:
            Tuple of (year, month)

        Raises:
            ValueError: If URI format is invalid

        Example:
            >>> vm.parse_version_uri('http://tgo.or.th/versions/2024-12')
            (2024, 12)
        """
        if not version_uri.startswith(self.base_uri):
            raise ValueError(f"Version URI must start with {self.base_uri}")

        version_part = version_uri[len(self.base_uri)+1:]  # Skip base_uri and '/'

        try:
            year_str, month_str = version_part.split('-')
            year = int(year_str)
            month = int(month_str)

            if not 1 <= month <= 12:
                raise ValueError(f"Invalid month: {month}")

            return (year, month)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid version URI format: {version_uri}") from e

    def get_current_version_uri(self) -> str:
        """
        Get the version URI for the current month.

        Returns:
            Version URI for current year-month

        Example:
            >>> vm.get_current_version_uri()  # In March 2026
            'http://tgo.or.th/versions/2026-03'
        """
        now = datetime.now(timezone.utc)
        return self.create_version_uri(now.year, now.month)

    def find_stale_factors(
        self,
        months: Optional[int] = None,
        named_graph: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find emission factors that are older than the staleness threshold.

        Args:
            months: Number of months to use as threshold (overrides default)
            named_graph: Optional specific named graph to query (if None, queries all)

        Returns:
            List of dictionaries with stale factor information:
            [
                {
                    'material': 'http://tgo.or.th/materials/concrete-c30',
                    'label': 'Concrete C30',
                    'effectiveDate': '2024-01-15',
                    'ageInDays': 432,
                    'category': 'Concrete'
                },
                ...
            ]

        Example:
            >>> stale = vm.find_stale_factors(months=6)
            >>> for factor in stale:
            ...     print(f"{factor['label']}: {factor['ageInDays']} days old")
        """
        threshold_months = months if months is not None else self.staleness_threshold_months
        threshold_date = datetime.now(timezone.utc) - relativedelta(months=threshold_months)
        threshold_str = threshold_date.strftime("%Y-%m-%d")

        # Sanitize named_graph URI if provided
        graph_clause = ""
        if named_graph:
            safe_graph = self._sanitize_uri(named_graph)
            graph_clause = f"GRAPH <{safe_graph}> {{"
            graph_close = "}"
        else:
            graph_close = ""

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?material ?label ?effectiveDate ?category
        WHERE {{
            {graph_clause}
                ?material tgo:effectiveDate ?effectiveDate ;
                         rdfs:label ?label .
                OPTIONAL {{ ?material tgo:category ?category }}
                FILTER (?effectiveDate < "{threshold_str}"^^xsd:date)
                FILTER (lang(?label) = "en" || lang(?label) = "")
            {graph_close}
        }}
        ORDER BY ?effectiveDate
        """

        try:
            result = self.client.query(query)

            stale_factors = []
            for binding in result['results']['bindings']:
                material_uri = binding['material']['value']
                label = binding['label']['value']
                effective_date_str = binding['effectiveDate']['value']
                category = binding.get('category', {}).get('value', 'Unknown')

                # Calculate age in days
                effective_date = datetime.strptime(effective_date_str, "%Y-%m-%d")
                # Use timezone-aware datetime for comparison
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)  # Remove tzinfo for comparison with naive datetime
                age_in_days = (now_utc - effective_date).days

                stale_factors.append({
                    'material': material_uri,
                    'label': label,
                    'effectiveDate': effective_date_str,
                    'ageInDays': age_in_days,
                    'category': category
                })

            logger.info(f"Found {len(stale_factors)} stale factors (>{threshold_months} months old)")
            return stale_factors

        except GraphDBError as e:
            error_msg = f"Error finding stale factors: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def list_versions(self) -> List[Dict[str, Any]]:
        """
        List all available TGO data versions in the repository.

        Returns:
            List of version information dictionaries:
            [
                {
                    'versionUri': 'http://tgo.or.th/versions/2024-12',
                    'versionDate': '2024-12-01',
                    'tripleCount': 1523,
                    'materialCount': 147,
                    'notes': 'Annual update with new steel factors'
                },
                ...
            ]

        Example:
            >>> versions = vm.list_versions()
            >>> for v in versions:
            ...     print(f"{v['versionUri']}: {v['materialCount']} materials")
        """
        query = """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?graph ?versionDate ?notes
        WHERE {
            GRAPH ?graph {
                ?version a tgo:DataVersion .
                OPTIONAL { ?version tgo:versionDate ?versionDate }
                OPTIONAL { ?version tgo:versionNotes ?notes }
            }
            FILTER (STRSTARTS(STR(?graph), "http://tgo.or.th/versions/"))
        }
        ORDER BY DESC(?versionDate)
        """

        try:
            result = self.client.query(query)

            versions = []
            for binding in result['results']['bindings']:
                version_uri = binding['graph']['value']
                version_date = binding.get('versionDate', {}).get('value', 'Unknown')
                notes = binding.get('notes', {}).get('value', '')

                # Get triple count for this version
                try:
                    triple_count = self.client.get_triple_count(named_graph=version_uri)
                except Exception as e:
                    logger.warning(f"Error getting triple count for {version_uri}: {str(e)}")
                    triple_count = 0

                # Get material count for this version
                material_count = self._count_materials_in_version(version_uri)

                versions.append({
                    'versionUri': version_uri,
                    'versionDate': version_date,
                    'tripleCount': triple_count,
                    'materialCount': material_count,
                    'notes': notes
                })

            logger.info(f"Found {len(versions)} versions in repository")
            return versions

        except GraphDBError as e:
            error_msg = f"Error listing versions: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def _count_materials_in_version(self, version_uri: str) -> int:
        """
        Count the number of construction materials in a specific version.

        Args:
            version_uri: Version named graph URI

        Returns:
            Number of materials in the version
        """
        # Sanitize URI to prevent SPARQL injection
        safe_uri = self._sanitize_uri(version_uri)

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT (COUNT(DISTINCT ?material) as ?count)
        WHERE {{
            GRAPH <{safe_uri}> {{
                ?material a ?type ;
                         tgo:hasEmissionFactor ?ef .
            }}
        }}
        """

        try:
            result = self.client.query(query)
            count = int(result['results']['bindings'][0]['count']['value'])
            return count
        except Exception as e:
            logger.warning(f"Error counting materials in version {version_uri}: {str(e)}")
            return 0

    def compare_versions(
        self,
        old_version: str,
        new_version: str
    ) -> Dict[str, Any]:
        """
        Compare two TGO data versions to identify changes.

        Args:
            old_version: Old version identifier (YYYY-MM) or full URI
            new_version: New version identifier (YYYY-MM) or full URI

        Returns:
            Dictionary with comparison results:
            {
                'oldVersion': 'http://tgo.or.th/versions/2024-12',
                'newVersion': 'http://tgo.or.th/versions/2025-01',
                'added': [...],  # New materials
                'removed': [...],  # Removed materials
                'updated': [...],  # Materials with changed emission factors
                'unchanged': [...],  # Materials with no changes
                'summary': {
                    'addedCount': 5,
                    'removedCount': 2,
                    'updatedCount': 12,
                    'unchangedCount': 130
                }
            }

        Example:
            >>> changes = vm.compare_versions("2024-12", "2025-01")
            >>> print(f"Added: {changes['summary']['addedCount']}")
            >>> print(f"Updated: {changes['summary']['updatedCount']}")
        """
        # Convert version identifiers to full URIs if needed
        old_uri = self._normalize_version_uri(old_version)
        new_uri = self._normalize_version_uri(new_version)

        logger.info(f"Comparing versions: {old_uri} -> {new_uri}")

        # Find added materials (in new but not in old)
        added = self._find_added_materials(old_uri, new_uri)

        # Find removed materials (in old but not in new)
        removed = self._find_removed_materials(old_uri, new_uri)

        # Find updated materials (same URI but different emission factor)
        updated = self._find_updated_materials(old_uri, new_uri)

        # Find unchanged materials
        unchanged = self._find_unchanged_materials(old_uri, new_uri)

        summary = {
            'addedCount': len(added),
            'removedCount': len(removed),
            'updatedCount': len(updated),
            'unchangedCount': len(unchanged)
        }

        logger.info(f"Version comparison summary: {summary}")

        return {
            'oldVersion': old_uri,
            'newVersion': new_uri,
            'added': added,
            'removed': removed,
            'updated': updated,
            'unchanged': unchanged,
            'summary': summary
        }

    def _normalize_version_uri(self, version: str) -> str:
        """
        Normalize a version identifier to a full URI.

        Args:
            version: Version identifier (YYYY-MM) or full URI

        Returns:
            Full version URI
        """
        if version.startswith('http://') or version.startswith('https://'):
            return version

        # Assume it's YYYY-MM format
        try:
            year, month = version.split('-')
            return self.create_version_uri(int(year), int(month))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid version format: {version}. Expected YYYY-MM or full URI") from e

    def _find_added_materials(self, old_uri: str, new_uri: str) -> List[Dict[str, Any]]:
        """Find materials that exist in new version but not in old version."""
        # Sanitize URIs to prevent SPARQL injection
        safe_old_uri = self._sanitize_uri(old_uri)
        safe_new_uri = self._sanitize_uri(new_uri)

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?emissionFactor ?category
        WHERE {{
            GRAPH <{safe_new_uri}> {{
                ?material a ?type ;
                         rdfs:label ?label ;
                         tgo:hasEmissionFactor ?emissionFactor .
                OPTIONAL {{ ?material tgo:category ?category }}
                FILTER (lang(?label) = "en" || lang(?label) = "")
            }}
            FILTER NOT EXISTS {{
                GRAPH <{safe_old_uri}> {{
                    ?material a ?anyType .
                }}
            }}
        }}
        ORDER BY ?label
        """

        try:
            result = self.client.query(query)
            materials = []

            for binding in result['results']['bindings']:
                materials.append({
                    'material': binding['material']['value'],
                    'label': binding['label']['value'],
                    'emissionFactor': binding.get('emissionFactor', {}).get('value'),
                    'category': binding.get('category', {}).get('value', 'Unknown')
                })

            return materials
        except GraphDBError as e:
            error_msg = f"Error finding added materials: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def _find_removed_materials(self, old_uri: str, new_uri: str) -> List[Dict[str, Any]]:
        """Find materials that exist in old version but not in new version."""
        # Sanitize URIs to prevent SPARQL injection
        safe_old_uri = self._sanitize_uri(old_uri)
        safe_new_uri = self._sanitize_uri(new_uri)

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?emissionFactor ?category
        WHERE {{
            GRAPH <{safe_old_uri}> {{
                ?material a ?type ;
                         rdfs:label ?label ;
                         tgo:hasEmissionFactor ?emissionFactor .
                OPTIONAL {{ ?material tgo:category ?category }}
                FILTER (lang(?label) = "en" || lang(?label) = "")
            }}
            FILTER NOT EXISTS {{
                GRAPH <{safe_new_uri}> {{
                    ?material a ?anyType .
                }}
            }}
        }}
        ORDER BY ?label
        """

        try:
            result = self.client.query(query)
            materials = []

            for binding in result['results']['bindings']:
                materials.append({
                    'material': binding['material']['value'],
                    'label': binding['label']['value'],
                    'emissionFactor': binding.get('emissionFactor', {}).get('value'),
                    'category': binding.get('category', {}).get('value', 'Unknown')
                })

            return materials
        except GraphDBError as e:
            error_msg = f"Error finding removed materials: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def _find_updated_materials(self, old_uri: str, new_uri: str) -> List[Dict[str, Any]]:
        """Find materials where emission factor changed between versions."""
        # Sanitize URIs to prevent SPARQL injection
        safe_old_uri = self._sanitize_uri(old_uri)
        safe_new_uri = self._sanitize_uri(new_uri)

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?oldEmissionFactor ?newEmissionFactor ?category
        WHERE {{
            GRAPH <{safe_old_uri}> {{
                ?material a ?type ;
                         rdfs:label ?label ;
                         tgo:hasEmissionFactor ?oldEmissionFactor .
                OPTIONAL {{ ?material tgo:category ?category }}
                FILTER (lang(?label) = "en" || lang(?label) = "")
            }}
            GRAPH <{safe_new_uri}> {{
                ?material tgo:hasEmissionFactor ?newEmissionFactor .
            }}
            FILTER (?oldEmissionFactor != ?newEmissionFactor)
        }}
        ORDER BY ?label
        """

        try:
            result = self.client.query(query)
            materials = []

            for binding in result['results']['bindings']:
                old_ef = float(binding['oldEmissionFactor']['value'])
                new_ef = float(binding['newEmissionFactor']['value'])
                change_pct = ((new_ef - old_ef) / old_ef) * 100 if old_ef != 0 else 0

                materials.append({
                    'material': binding['material']['value'],
                    'label': binding['label']['value'],
                    'oldEmissionFactor': old_ef,
                    'newEmissionFactor': new_ef,
                    'changePercent': round(change_pct, 2),
                    'category': binding.get('category', {}).get('value', 'Unknown')
                })

            return materials
        except GraphDBError as e:
            error_msg = f"Error finding updated materials: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def _find_unchanged_materials(self, old_uri: str, new_uri: str) -> List[Dict[str, Any]]:
        """Find materials where emission factor is the same in both versions."""
        # Sanitize URIs to prevent SPARQL injection
        safe_old_uri = self._sanitize_uri(old_uri)
        safe_new_uri = self._sanitize_uri(new_uri)

        query = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?material ?label ?emissionFactor ?category
        WHERE {{
            GRAPH <{safe_old_uri}> {{
                ?material a ?type ;
                         rdfs:label ?label ;
                         tgo:hasEmissionFactor ?emissionFactor .
                ?type rdfs:subClassOf* tgo:ConstructionMaterial .
                OPTIONAL {{ ?material tgo:category ?category }}
                FILTER (lang(?label) = "en" || lang(?label) = "")
            }}
            GRAPH <{safe_new_uri}> {{
                ?material tgo:hasEmissionFactor ?emissionFactor .
            }}
        }}
        ORDER BY ?label
        """

        try:
            result = self.client.query(query)
            materials = []

            for binding in result['results']['bindings']:
                materials.append({
                    'material': binding['material']['value'],
                    'label': binding['label']['value'],
                    'emissionFactor': binding['emissionFactor']['value'],
                    'category': binding.get('category', {}).get('value', 'Unknown')
                })

            return materials
        except GraphDBError as e:
            error_msg = f"Error finding unchanged materials: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

    def create_version_metadata(
        self,
        version_uri: str,
        version_date: str,
        notes: str = "",
        previous_version_uri: Optional[str] = None
    ) -> bool:
        """
        Create metadata for a new version in the repository.

        Args:
            version_uri: URI of the version named graph
            version_date: Version date in YYYY-MM-DD format
            notes: Release notes describing changes
            previous_version_uri: Optional URI of the previous version

        Returns:
            True if metadata was created successfully

        Raises:
            ValueError: If version_date format is invalid

        Example:
            >>> vm.create_version_metadata(
            ...     "http://tgo.or.th/versions/2026-03",
            ...     "2026-03-01",
            ...     "Q1 2026 update with new aluminum factors"
            ... )
        """
        # Validate version_date format
        try:
            datetime.strptime(version_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid version_date format. Expected YYYY-MM-DD, got: {version_date}") from e

        # Sanitize URIs to prevent SPARQL injection
        safe_version_uri = self._sanitize_uri(version_uri)
        previous_version_clause = ""
        if previous_version_uri:
            safe_previous_uri = self._sanitize_uri(previous_version_uri)
            previous_version_clause = f'<{safe_version_uri}> tgo:previousVersion <{safe_previous_uri}> .'

        # Escape notes string to prevent injection
        safe_notes = notes.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

        update = f"""
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            GRAPH <{safe_version_uri}> {{
                <{safe_version_uri}> a tgo:DataVersion ;
                    tgo:versionDate "{version_date}"^^xsd:date ;
                    tgo:versionNotes "{safe_notes}" ;
                    dcterms:created "{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"^^xsd:dateTime .
                {previous_version_clause}
            }}
        }}
        """

        try:
            self.client.update(update)
            logger.info(f"Created version metadata for {version_uri}")
            return True
        except GraphDBError as e:
            error_msg = f"Error creating version metadata: {str(e)}"
            logger.error(error_msg)
            raise VersionManagerError(error_msg) from e

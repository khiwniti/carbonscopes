"""
GraphDB Client for RDF triple management and SPARQL query execution.

This module provides a client for interacting with GraphDB, including:
- Triple insertion via POST /statements
- SPARQL query execution
- Error handling for network and GraphDB issues
- Support for multiple RDF serialization formats
"""

import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, TURTLE, RDFXML, GET


logger = logging.getLogger(__name__)


class GraphDBError(Exception):
    """Base exception for GraphDB client errors."""
    pass


class GraphDBClient:
    """
    Client for interacting with GraphDB SPARQL endpoint.

    This client provides methods for:
    - Inserting RDF triples into GraphDB
    - Executing SPARQL queries
    - Managing named graphs
    - Handling different RDF serialization formats

    Args:
        endpoint_url: Base URL of the GraphDB repository (e.g., http://localhost:7200/repositories/carbonbim-thailand)
        username: Optional username for authentication
        password: Optional password for authentication
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
        >>> client.insert_triples(graph)
        >>> results = client.query("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
    """

    def __init__(
        self,
        endpoint_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """Initialize the GraphDB client."""
        self.endpoint_url = endpoint_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout

        # Set up authentication if provided
        self.auth = (username, password) if username and password else None

        # Initialize SPARQL wrapper for queries
        self.sparql = SPARQLWrapper(self.endpoint_url)
        if self.auth:
            self.sparql.setCredentials(username, password)
        self.sparql.setTimeout(timeout)

        logger.info(f"Initialized GraphDB client for endpoint: {self.endpoint_url}")

    def insert_triples(
        self,
        graph: Graph,
        named_graph: Optional[str] = None,
        format: str = "turtle"
    ) -> bool:
        """
        Insert RDF triples into GraphDB via POST /statements.

        Args:
            graph: RDFLib Graph containing triples to insert
            named_graph: Optional named graph URI to insert into
            format: RDF serialization format (turtle, xml, n3, nt, etc.)

        Returns:
            True if insertion was successful

        Raises:
            GraphDBError: If insertion fails

        Example:
            >>> g = Graph()
            >>> g.add((URIRef("http://example.org/subject"),
            ...        RDF.type,
            ...        URIRef("http://example.org/Type")))
            >>> client.insert_triples(g)
        """
        try:
            # Serialize the graph to the specified format
            serialized_data = graph.serialize(format=format)

            # Prepare the POST request to /statements endpoint
            statements_url = urljoin(self.endpoint_url + '/', 'statements')

            # Set content type based on format
            content_type_map = {
                "turtle": "text/turtle",
                "ttl": "text/turtle",
                "xml": "application/rdf+xml",
                "rdf": "application/rdf+xml",
                "n3": "text/n3",
                "nt": "application/n-triples",
                "ntriples": "application/n-triples",
                "jsonld": "application/ld+json",
            }
            content_type = content_type_map.get(format.lower(), "text/turtle")

            headers = {
                "Content-Type": content_type
            }

            # Add named graph parameter if specified
            params = {}
            if named_graph:
                params['context'] = f"<{named_graph}>"

            # Send POST request
            response = requests.post(
                statements_url,
                data=serialized_data,
                headers=headers,
                params=params,
                auth=self.auth,
                timeout=self.timeout
            )

            # Check for errors
            if response.status_code not in (200, 204):
                error_msg = f"Failed to insert triples. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise GraphDBError(error_msg)

            triple_count = len(graph)
            logger.info(f"Successfully inserted {triple_count} triples into GraphDB")
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while inserting triples: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e
        except Exception as e:
            error_msg = f"Error inserting triples: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e

    def query(
        self,
        query_string: str,
        return_format: str = "json"
    ) -> Union[Dict[str, Any], str]:
        """
        Execute a SPARQL query against GraphDB.

        Args:
            query_string: SPARQL query string (SELECT, ASK, CONSTRUCT, DESCRIBE)
            return_format: Result format (json, xml, turtle, n3, rdf)

        Returns:
            Query results in the specified format (dict for JSON, string for others)

        Raises:
            GraphDBError: If query execution fails

        Example:
            >>> results = client.query("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
            >>> for binding in results['results']['bindings']:
            ...     print(binding)
        """
        try:
            self.sparql.setQuery(query_string)

            # Set return format
            format_map = {
                "json": JSON,
                "xml": XML,
                "turtle": TURTLE,
                "ttl": TURTLE,
                "n3": N3,
                "rdf": RDFXML,
                "rdfxml": RDFXML,
            }
            sparql_format = format_map.get(return_format.lower(), JSON)
            self.sparql.setReturnFormat(sparql_format)

            # Set method to GET for queries
            self.sparql.setMethod(GET)

            # Execute query
            response = self.sparql.query()

            # Convert response based on format
            if return_format.lower() == "json":
                return response.convert()
            else:
                result = response.convert()
                if isinstance(result, bytes):
                    return result.decode('utf-8')
                elif hasattr(result, 'serialize'):
                    # RDFLib Graph object
                    return result.serialize(format=return_format)
                else:
                    return str(result)

        except Exception as e:
            error_msg = f"Error executing SPARQL query: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Query was: {query_string}")
            raise GraphDBError(error_msg) from e

    def update(self, update_string: str) -> bool:
        """
        Execute a SPARQL UPDATE operation (INSERT, DELETE, etc.).

        Args:
            update_string: SPARQL UPDATE string

        Returns:
            True if update was successful

        Raises:
            GraphDBError: If update execution fails

        Example:
            >>> update = '''
            ... INSERT DATA {
            ...     <http://example.org/subject> <http://example.org/predicate> "value" .
            ... }
            ... '''
            >>> client.update(update)
        """
        try:
            # SPARQL UPDATE uses the /statements endpoint with POST
            statements_url = urljoin(self.endpoint_url + '/', 'statements')

            headers = {
                "Content-Type": "application/sparql-update"
            }

            response = requests.post(
                statements_url,
                data=update_string,
                headers=headers,
                auth=self.auth,
                timeout=self.timeout
            )

            if response.status_code not in (200, 204):
                error_msg = f"Failed to execute update. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise GraphDBError(error_msg)

            logger.info("Successfully executed SPARQL UPDATE")
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while executing update: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e
        except Exception as e:
            error_msg = f"Error executing update: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e

    def clear_repository(self, named_graph: Optional[str] = None) -> bool:
        """
        Clear all triples from the repository or a specific named graph.

        WARNING: This operation is destructive and cannot be undone.

        Args:
            named_graph: Optional named graph URI to clear (if None, clears entire repository)

        Returns:
            True if clearing was successful

        Raises:
            GraphDBError: If clearing fails
        """
        try:
            statements_url = urljoin(self.endpoint_url + '/', 'statements')

            params = {}
            if named_graph:
                params['context'] = f"<{named_graph}>"
                logger.warning(f"Clearing named graph: {named_graph}")
            else:
                logger.warning("Clearing entire repository")

            response = requests.delete(
                statements_url,
                params=params,
                auth=self.auth,
                timeout=self.timeout
            )

            if response.status_code not in (200, 204):
                error_msg = f"Failed to clear repository. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                raise GraphDBError(error_msg)

            logger.info("Successfully cleared repository/graph")
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while clearing repository: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e
        except Exception as e:
            error_msg = f"Error clearing repository: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e

    def test_connection(self) -> bool:
        """
        Test the connection to GraphDB.

        Returns:
            True if connection is successful

        Raises:
            GraphDBError: If connection test fails
        """
        try:
            # Execute a simple query to test connectivity
            result = self.query("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
            logger.info("GraphDB connection test successful")
            return True
        except Exception as e:
            error_msg = f"GraphDB connection test failed: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e

    def get_triple_count(self, named_graph: Optional[str] = None) -> int:
        """
        Get the count of triples in the repository or a specific named graph.

        Args:
            named_graph: Optional named graph URI to count triples in

        Returns:
            Number of triples

        Raises:
            GraphDBError: If count query fails
        """
        try:
            if named_graph:
                query = f"""
                SELECT (COUNT(*) as ?count)
                WHERE {{
                    GRAPH <{named_graph}> {{
                        ?s ?p ?o
                    }}
                }}
                """
            else:
                query = """
                SELECT (COUNT(*) as ?count)
                WHERE {
                    ?s ?p ?o
                }
                """

            result = self.query(query)
            count = int(result['results']['bindings'][0]['count']['value'])
            return count

        except Exception as e:
            error_msg = f"Error getting triple count: {str(e)}"
            logger.error(error_msg)
            raise GraphDBError(error_msg) from e

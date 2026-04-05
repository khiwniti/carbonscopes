#!/usr/bin/env python3
"""
GraphDB Repository Setup Script

Creates and configures the 'carbonbim-thailand' repository in GraphDB.
Enables RDFS inference for emission factors and certification criteria.

Usage:
    python scripts/setup_graphdb_repository.py

Environment:
    GRAPHDB_URL: GraphDB endpoint (default: http://localhost:7200)
"""

import requests
import sys
import time
from typing import Dict, Any


# Configuration
GRAPHDB_URL = "http://localhost:7200"
REPOSITORY_ID = "carbonbim-thailand"
REPOSITORY_LABEL = "CarbonBIM Thailand - TGO Emission Factors & EDGE/TREES Certification"


def get_repository_config() -> str:
    """
    Generate GraphDB repository configuration in Turtle format.

    This configuration:
    - Creates a GraphDB Free repository
    - Enables RDFS inference for ontology reasoning
    - Optimizes for read-heavy workloads (SPARQL queries)
    - Sets appropriate storage and query limits
    """
    return f"""#
# RDF4J configuration template for a GraphDB Free repository
#
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rep: <http://www.openrdf.org/config/repository#>.
@prefix sr: <http://www.openrdf.org/config/repository/sail#>.
@prefix sail: <http://www.openrdf.org/config/sail#>.
@prefix graphdb: <http://www.ontotext.com/config/graphdb#>.

[] a rep:Repository ;
    rep:repositoryID "{REPOSITORY_ID}" ;
    rdfs:label "{REPOSITORY_LABEL}" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;

            # Repository ID
            graphdb:repositoryId "{REPOSITORY_ID}" ;

            # Enable RDFS inference for ontology reasoning
            # This allows automatic inference of subclass/subproperty relationships
            graphdb:ruleset "rdfs" ;

            # Disable OWL reasoning (RDFS is sufficient for our use case)
            graphdb:disable-sameAs "true" ;

            # Storage settings
            graphdb:storage-folder "storage" ;
            graphdb:entity-index-size "10000000" ;

            # Query settings - optimize for read-heavy workloads
            graphdb:query-timeout "60" ;
            graphdb:query-limit-results "0" ;
            graphdb:throw-query-evaluation-exception-on-timeout "false" ;

            # Enable context indexing for named graphs
            graphdb:enable-context-index "true" ;

            # Consistency settings
            graphdb:check-for-inconsistencies "false" ;

            # Performance settings
            graphdb:tuple-index-memory "1g" ;
            graphdb:base-URL "http://carbonbim.thailand/" ;

            # Transaction settings
            graphdb:defaultNS "" ;
        ]
    ].
"""


def check_graphdb_ready(max_retries: int = 30, delay: int = 2) -> bool:
    """Check if GraphDB is ready to accept requests."""
    print(f"Checking GraphDB availability at {GRAPHDB_URL}...")

    for i in range(max_retries):
        try:
            response = requests.get(f"{GRAPHDB_URL}/rest/monitor/infrastructure", timeout=5)
            if response.status_code == 200:
                print("GraphDB is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        if i < max_retries - 1:
            print(f"Waiting for GraphDB... ({i+1}/{max_retries})")
            time.sleep(delay)

    print("ERROR: GraphDB is not responding")
    return False


def repository_exists() -> bool:
    """Check if the repository already exists."""
    try:
        response = requests.get(f"{GRAPHDB_URL}/rest/repositories/{REPOSITORY_ID}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error checking repository: {e}")
        return False


def create_repository() -> bool:
    """Create the GraphDB repository with RDFS inference enabled."""
    print(f"\nCreating repository '{REPOSITORY_ID}'...")

    config = get_repository_config()

    # GraphDB REST API requires multipart/form-data with 'config' field
    files = {
        'config': ('config.ttl', config, 'text/turtle')
    }

    try:
        response = requests.post(
            f"{GRAPHDB_URL}/rest/repositories",
            files=files,
            timeout=30
        )

        if response.status_code == 201:
            print(f"✓ Repository '{REPOSITORY_ID}' created successfully!")
            return True
        else:
            print(f"✗ Failed to create repository. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating repository: {e}")
        return False


def get_repository_info() -> Dict[str, Any]:
    """Get information about the created repository."""
    try:
        response = requests.get(f"{GRAPHDB_URL}/rest/repositories/{REPOSITORY_ID}")
        if response.status_code == 200:
            return response.json()
        return {}
    except requests.exceptions.RequestException:
        return {}


def test_sparql_query() -> bool:
    """Test the repository with a basic SPARQL query."""
    print("\nTesting SPARQL endpoint...")

    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"

    headers = {
        "Accept": "application/sparql-results+json"
    }

    try:
        response = requests.get(
            f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}",
            params={"query": query},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            results = response.json()
            print(f"✓ SPARQL query successful!")
            print(f"  Query returned {len(results.get('results', {}).get('bindings', []))} results")
            print(f"  Variables: {results.get('head', {}).get('vars', [])}")
            return True
        else:
            print(f"✗ SPARQL query failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error executing SPARQL query: {e}")
        return False


def test_sparql_update() -> bool:
    """Test SPARQL UPDATE to insert sample data."""
    print("\nTesting SPARQL UPDATE with sample data...")

    update = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ex: <http://carbonbim.thailand/example/>

    INSERT DATA {
        ex:Material rdfs:subClassOf ex:BuildingComponent .
        ex:Concrete a ex:Material ;
            rdfs:label "Concrete"@en ;
            ex:emissionFactor "350.5"^^<http://www.w3.org/2001/XMLSchema#decimal> .
    }
    """

    headers = {
        "Content-Type": "application/sparql-update"
    }

    try:
        response = requests.post(
            f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}/statements",
            data=update,
            headers=headers,
            timeout=10
        )

        if response.status_code == 204:
            print("✓ Sample data inserted successfully!")

            # Verify the data with inference
            verify_query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ex: <http://carbonbim.thailand/example/>

            SELECT ?material ?label ?emissionFactor WHERE {
                ?material a ex:Material ;
                    rdfs:label ?label ;
                    ex:emissionFactor ?emissionFactor .
            }
            """

            verify_response = requests.get(
                f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}",
                params={"query": verify_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=10
            )

            if verify_response.status_code == 200:
                results = verify_response.json()
                bindings = results.get('results', {}).get('bindings', [])
                print(f"  Verified {len(bindings)} material(s) in repository")
                for binding in bindings:
                    print(f"  - {binding.get('label', {}).get('value', 'N/A')}: "
                          f"{binding.get('emissionFactor', {}).get('value', 'N/A')} kgCO2e")

            return True
        else:
            print(f"✗ SPARQL UPDATE failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error executing SPARQL UPDATE: {e}")
        return False


def main():
    """Main setup routine."""
    print("=" * 70)
    print("GraphDB Repository Setup - CarbonBIM Thailand")
    print("=" * 70)

    # Check if GraphDB is ready
    if not check_graphdb_ready():
        print("\n✗ Setup failed: GraphDB is not available")
        sys.exit(1)

    # Check if repository already exists
    if repository_exists():
        print(f"\n⚠ Repository '{REPOSITORY_ID}' already exists!")
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(0)

    # Create repository
    if not create_repository():
        print("\n✗ Setup failed: Could not create repository")
        sys.exit(1)

    # Wait a moment for repository to initialize
    print("\nWaiting for repository to initialize...")
    time.sleep(2)

    # Get repository info
    info = get_repository_info()
    if info:
        print(f"\nRepository Information:")
        print(f"  ID: {info.get('id', 'N/A')}")
        print(f"  Title: {info.get('title', 'N/A')}")
        print(f"  Type: {info.get('type', 'N/A')}")
        print(f"  Location: {info.get('location', 'N/A')}")

    # Test SPARQL query
    if not test_sparql_query():
        print("\n⚠ Warning: SPARQL query test failed")

    # Test SPARQL update
    if not test_sparql_update():
        print("\n⚠ Warning: SPARQL UPDATE test failed")

    # Summary
    print("\n" + "=" * 70)
    print("✓ GraphDB Repository Setup Complete!")
    print("=" * 70)
    print(f"\nRepository Details:")
    print(f"  Name: {REPOSITORY_ID}")
    print(f"  Inference: RDFS enabled")
    print(f"  SPARQL Endpoint: {GRAPHDB_URL}/repositories/{REPOSITORY_ID}")
    print(f"  Web UI: {GRAPHDB_URL}/sparql")
    print(f"\nNext Steps:")
    print(f"  1. Load TGO emission factors into named graphs")
    print(f"  2. Load EDGE/TREES certification criteria")
    print(f"  3. Create SPARQL query library for common queries")
    print(f"  4. Integrate with RDFLib for Python access")
    print("=" * 70)


if __name__ == "__main__":
    main()

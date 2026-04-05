"""
Example usage of TGO Named Graph Versioning System.

This script demonstrates the key features of the versioning system:
- Creating version URIs
- Finding stale emission factors
- Listing available versions
- Comparing versions
- Creating version metadata

Prerequisites:
    - GraphDB running at http://localhost:7200
    - Repository 'carbonbim-thailand' exists
    - TGO ontology loaded
"""

import sys
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Add parent directory to path for imports
sys.path.insert(0, '/teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna/backend')

from core.knowledge_graph.graphdb_client import GraphDBClient, GraphDBError
from core.knowledge_graph.versioning import VersionManager, VersionManagerError


# Configuration
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/carbonbim-thailand"
TGO = Namespace("http://tgo.or.th/ontology#")


def create_sample_version_data(version_year: int, version_month: int) -> Graph:
    """
    Create sample TGO emission factor data for testing.

    Args:
        version_year: Year for the version
        version_month: Month for the version

    Returns:
        RDFLib Graph with sample data
    """
    g = Graph()
    g.bind("tgo", TGO)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # Sample materials with emission factors
    materials = [
        {
            "id": "concrete-c25",
            "type": TGO.Concrete,
            "labelEN": "Ready-mixed Concrete C25",
            "labelTH": "คอนกรีตผสมเสร็จ C25",
            "emissionFactor": "395.4",
            "unit": "kgCO2e/m³",
            "category": "Concrete"
        },
        {
            "id": "concrete-c30",
            "type": TGO.Concrete,
            "labelEN": "Ready-mixed Concrete C30",
            "labelTH": "คอนกรีตผสมเสร็จ C30",
            "emissionFactor": "445.6",
            "unit": "kgCO2e/m³",
            "category": "Concrete"
        },
        {
            "id": "steel-rebar-sd40",
            "type": TGO.Steel,
            "labelEN": "Steel Reinforcement Bar SD40",
            "labelTH": "เหล็กเสริมคอนกรีต SD40",
            "emissionFactor": "2150.0",
            "unit": "kgCO2e/ton",
            "category": "Steel"
        },
        {
            "id": "aluminum-profile",
            "type": TGO.Aluminum,
            "labelEN": "Aluminum Profile",
            "labelTH": "โปรไฟล์อลูมิเนียม",
            "emissionFactor": "8900.0",
            "unit": "kgCO2e/ton",
            "category": "Aluminum"
        },
        {
            "id": "glass-float-6mm",
            "type": TGO.Glass,
            "labelEN": "Float Glass 6mm",
            "labelTH": "กระจกใส 6มม.",
            "emissionFactor": "18.5",
            "unit": "kgCO2e/m²",
            "category": "Glass"
        }
    ]

    effective_date = f"{version_year:04d}-{version_month:02d}-01"

    for material in materials:
        material_uri = URIRef(f"http://tgo.or.th/materials/{material['id']}")

        # Type
        g.add((material_uri, RDF.type, material['type']))

        # Labels
        g.add((material_uri, RDFS.label, Literal(material['labelEN'], lang='en')))
        g.add((material_uri, RDFS.label, Literal(material['labelTH'], lang='th')))

        # Emission factor
        g.add((material_uri, TGO.hasEmissionFactor,
               Literal(material['emissionFactor'], datatype=XSD.decimal)))

        # Metadata
        g.add((material_uri, TGO.hasUnit, Literal(material['unit'])))
        g.add((material_uri, TGO.category, Literal(material['category'])))
        g.add((material_uri, TGO.effectiveDate,
               Literal(effective_date, datatype=XSD.date)))
        g.add((material_uri, TGO.dataQuality, Literal("Verified")))
        g.add((material_uri, TGO.geographicScope, Literal("Thailand")))

    return g


def example_1_create_version_uri():
    """Example 1: Create and parse version URIs."""
    print("\n" + "="*60)
    print("Example 1: Creating and Parsing Version URIs")
    print("="*60)

    client = GraphDBClient(GRAPHDB_ENDPOINT)
    vm = VersionManager(client)

    # Create version URI
    uri = vm.create_version_uri(2024, 12)
    print(f"Created version URI: {uri}")

    # Parse version URI
    year, month = vm.parse_version_uri(uri)
    print(f"Parsed: Year={year}, Month={month}")

    # Get current version URI
    current_uri = vm.get_current_version_uri()
    print(f"Current version URI: {current_uri}")


def example_2_load_test_data():
    """Example 2: Load sample data into test versions."""
    print("\n" + "="*60)
    print("Example 2: Loading Test Data")
    print("="*60)

    try:
        client = GraphDBClient(GRAPHDB_ENDPOINT)
        vm = VersionManager(client)

        # Create two versions for comparison
        versions = [
            (2024, 12),
            (2025, 1)
        ]

        for year, month in versions:
            version_uri = vm.create_version_uri(year, month)

            # Create sample data
            g = create_sample_version_data(year, month)

            # Load into GraphDB
            print(f"\nLoading version {year}-{month:02d}...")
            client.insert_triples(g, named_graph=version_uri, format="turtle")

            # Create version metadata
            vm.create_version_metadata(
                version_uri=version_uri,
                version_date=f"{year}-{month:02d}-01",
                notes=f"Test version {year}-{month:02d}"
            )

            # Verify
            count = client.get_triple_count(named_graph=version_uri)
            print(f"Loaded {count} triples into {version_uri}")

        print("\n✓ Test data loaded successfully!")

    except GraphDBError as e:
        print(f"✗ Error loading test data: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_3_list_versions():
    """Example 3: List all available versions."""
    print("\n" + "="*60)
    print("Example 3: Listing Available Versions")
    print("="*60)

    try:
        client = GraphDBClient(GRAPHDB_ENDPOINT)
        vm = VersionManager(client)

        versions = vm.list_versions()

        if not versions:
            print("No versions found in repository.")
            print("Run example_2_load_test_data() first to create test versions.")
            return

        print(f"\nFound {len(versions)} version(s):\n")
        for v in versions:
            print(f"  Version: {v['versionUri']}")
            print(f"    Date: {v['versionDate']}")
            print(f"    Materials: {v['materialCount']}")
            print(f"    Triples: {v['tripleCount']}")
            print(f"    Notes: {v['notes']}")
            print()

    except VersionManagerError as e:
        print(f"✗ Error listing versions: {e}")


def example_4_find_stale_factors():
    """Example 4: Find stale emission factors."""
    print("\n" + "="*60)
    print("Example 4: Finding Stale Emission Factors")
    print("="*60)

    try:
        client = GraphDBClient(GRAPHDB_ENDPOINT)
        vm = VersionManager(client)

        # Find factors older than 6 months
        stale = vm.find_stale_factors(months=6)

        if not stale:
            print("✓ No stale emission factors found!")
            return

        print(f"\nFound {len(stale)} stale emission factor(s):\n")
        for factor in stale[:10]:  # Show first 10
            print(f"  {factor['label']}")
            print(f"    Effective Date: {factor['effectiveDate']}")
            print(f"    Age: {factor['ageInDays']} days")
            print(f"    Category: {factor['category']}")
            print()

    except VersionManagerError as e:
        print(f"✗ Error finding stale factors: {e}")


def example_5_compare_versions():
    """Example 5: Compare two versions."""
    print("\n" + "="*60)
    print("Example 5: Comparing Versions")
    print("="*60)

    try:
        client = GraphDBClient(GRAPHDB_ENDPOINT)
        vm = VersionManager(client)

        # Compare 2024-12 vs 2025-01
        comparison = vm.compare_versions("2024-12", "2025-01")

        print(f"\nComparison: {comparison['oldVersion']} → {comparison['newVersion']}")
        print("\nSummary:")
        print(f"  Added: {comparison['summary']['addedCount']} materials")
        print(f"  Removed: {comparison['summary']['removedCount']} materials")
        print(f"  Updated: {comparison['summary']['updatedCount']} materials")
        print(f"  Unchanged: {comparison['summary']['unchangedCount']} materials")

        # Show added materials
        if comparison['added']:
            print("\nAdded Materials:")
            for material in comparison['added']:
                print(f"  + {material['label']} ({material['category']})")

        # Show removed materials
        if comparison['removed']:
            print("\nRemoved Materials:")
            for material in comparison['removed']:
                print(f"  - {material['label']} ({material['category']})")

        # Show updated materials
        if comparison['updated']:
            print("\nUpdated Materials:")
            for material in comparison['updated']:
                print(f"  ~ {material['label']}")
                print(f"    Old: {material['oldEmissionFactor']}")
                print(f"    New: {material['newEmissionFactor']}")
                print(f"    Change: {material['changePercent']:+.2f}%")

    except VersionManagerError as e:
        print(f"✗ Error comparing versions: {e}")


def example_6_test_connection():
    """Example 6: Test GraphDB connection."""
    print("\n" + "="*60)
    print("Example 6: Testing GraphDB Connection")
    print("="*60)

    try:
        client = GraphDBClient(GRAPHDB_ENDPOINT)

        # Test connection
        client.test_connection()
        print("✓ GraphDB connection successful!")

        # Get repository size
        count = client.get_triple_count()
        print(f"✓ Total triples in repository: {count}")

    except GraphDBError as e:
        print(f"✗ GraphDB connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure GraphDB is running: http://localhost:7200")
        print("  2. Verify repository 'carbonbim-thailand' exists")
        print("  3. Check firewall settings")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("TGO Named Graph Versioning - Example Usage")
    print("="*60)

    # Test connection first
    example_6_test_connection()

    # Run examples
    example_1_create_version_uri()
    # example_2_load_test_data()  # Uncomment to load test data
    example_3_list_versions()
    example_4_find_stale_factors()
    # example_5_compare_versions()  # Uncomment after loading test data

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run example_2_load_test_data() to create test versions")
    print("  2. Run example_5_compare_versions() to see version comparison")
    print("  3. Integrate versioning into your application")
    print()


if __name__ == "__main__":
    main()

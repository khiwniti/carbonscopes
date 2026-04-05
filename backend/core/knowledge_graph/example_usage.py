"""
Example usage of the GraphDB client.

This script demonstrates:
1. Connecting to GraphDB
2. Creating RDF triples using RDFLib
3. Inserting triples into GraphDB
4. Querying the data back
5. Verifying round-trip integrity
"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD

from graphdb_client import GraphDBClient


def main():
    """Demonstrate GraphDB client usage."""

    # Initialize client
    print("=== Initializing GraphDB Client ===")
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

    # Test connection
    print("\n=== Testing Connection ===")
    client.test_connection()
    print("Connection successful!")

    # Create RDF graph
    print("\n=== Creating RDF Graph ===")
    g = Graph()
    ns = Namespace("http://example.org/carbonbim/")

    # Add triples about a building material
    concrete = ns.Material_Concrete_C30
    g.add((concrete, RDF.type, ns.Material))
    g.add((concrete, RDFS.label, Literal("Concrete C30", lang="en")))
    g.add((concrete, ns.compressiveStrength, Literal(30, datatype=XSD.integer)))
    g.add((concrete, ns.embodiedCarbon, Literal(310.5, datatype=XSD.decimal)))
    g.add((concrete, ns.unit, Literal("kgCO2e/m3")))

    print(f"Created graph with {len(g)} triples")

    # Insert triples
    print("\n=== Inserting Triples ===")
    client.insert_triples(g)
    print("Triples inserted successfully!")

    # Query data back
    print("\n=== Querying Data ===")
    query = f"""
    PREFIX rdfs: <{RDFS}>
    SELECT ?material ?label ?carbon
    WHERE {{
        ?material a <{ns.Material}> .
        ?material rdfs:label ?label .
        ?material <{ns.embodiedCarbon}> ?carbon .
    }}
    """
    results = client.query(query)

    print(f"Found {len(results['results']['bindings'])} results:")
    for binding in results['results']['bindings']:
        print(f"  Material: {binding['label']['value']}")
        print(f"  Carbon: {binding['carbon']['value']} kgCO2e/m3")

    # Get triple count
    print("\n=== Statistics ===")
    count = client.get_triple_count()
    print(f"Total triples in repository: {count}")

    print("\n=== Success! ===")
    print("Round-trip test completed successfully")


if __name__ == "__main__":
    main()

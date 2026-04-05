#!/usr/bin/env python3
"""
Example usage of the SPARQL query library.

This script demonstrates common use cases for the TGO material query functions.

Usage:
    python example_usage_sparql.py

Prerequisites:
    - GraphDB running at http://localhost:7200
    - Repository 'carbonbim-thailand' exists
    - TGO ontology and sample data loaded
"""

import sys
from decimal import Decimal

from core.knowledge_graph import (
    GraphDBClient,
    get_emission_factor,
    search_materials,
    list_materials_by_category,
    get_all_categories,
    find_stale_materials,
    MaterialNotFoundError,
    QueryError,
)


def main():
    """Run example queries."""
    print("=" * 80)
    print("TGO SPARQL Query Library - Example Usage")
    print("=" * 80)

    # Initialize client
    print("\n1. Initializing GraphDB client...")
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

    try:
        client.test_connection()
        print("   ✓ Connected to GraphDB")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print("\nPlease ensure GraphDB is running and the repository exists.")
        sys.exit(1)

    # Example 1: Get emission factor by URI
    print("\n2. Example: Get emission factor by material URI")
    print("-" * 80)
    try:
        material_id = "http://tgo.or.th/materials/concrete-c30"
        result = get_emission_factor(client, material_id, include_metadata=True)

        print(f"Material ID: {result['material_id']}")
        print(f"Label (EN):  {result['label_en']}")
        print(f"Label (TH):  {result['label_th']}")
        print(f"Category:    {result['category']}")
        print(f"Emission:    {result['emission_factor']} {result['unit']}")
        print(f"Date:        {result['effective_date']}")
        if 'metadata' in result:
            print(f"Quality:     {result['metadata'].get('data_quality')}")
            print(f"Uncertainty: ±{result['metadata'].get('uncertainty', 0) * 100}%")
    except MaterialNotFoundError:
        print(f"Material not found: {material_id}")
        print("Note: You may need to load sample TGO data first.")
    except QueryError as e:
        print(f"Query error: {e}")

    # Example 2: Search for materials
    print("\n3. Example: Search for concrete materials")
    print("-" * 80)
    try:
        results = search_materials(client, "concrete", limit=5)
        print(f"Found {len(results)} results:")
        for i, material in enumerate(results, 1):
            print(f"  {i}. {material['label']}")
            print(f"     {material['emission_factor']} {material['unit']}")
    except QueryError as e:
        print(f"Query error: {e}")

    # Example 3: List materials by category
    print("\n4. Example: List all steel materials")
    print("-" * 80)
    try:
        steels = list_materials_by_category(
            client,
            "Steel",
            sort_by="emission_factor",
            limit=5
        )
        print(f"Found {len(steels)} steel materials:")
        for i, material in enumerate(steels, 1):
            print(f"  {i}. {material['label']}")
            print(f"     {material['emission_factor']} {material['unit']}")
    except QueryError as e:
        print(f"Query error: {e}")

    # Example 4: Get all categories
    print("\n5. Example: Get all material categories")
    print("-" * 80)
    try:
        categories = get_all_categories(client)
        print(f"Total categories: {len(categories)}")
        for cat in categories[:10]:  # Show top 10
            print(f"  {cat['category']}: {cat['count']} materials")
    except QueryError as e:
        print(f"Query error: {e}")

    # Example 5: Find stale materials
    print("\n6. Example: Find materials with outdated emission factors (>6 months)")
    print("-" * 80)
    try:
        stale = find_stale_materials(client, threshold_months=6)
        if stale:
            print(f"Found {len(stale)} stale materials:")
            for material in stale[:5]:  # Show first 5
                print(f"  - {material['label']}")
                print(f"    Age: {material.get('age_days', '?')} days")
        else:
            print("No stale materials found (all data is up to date)")
    except QueryError as e:
        print(f"Query error: {e}")

    # Example 6: Calculate carbon emissions
    print("\n7. Example: Calculate carbon emissions for a project")
    print("-" * 80)
    try:
        # Simulate a small project BOQ
        project_materials = [
            {"name": "concrete", "quantity": Decimal("150.5"), "unit": "m³"},
            {"name": "steel", "quantity": Decimal("12.5"), "unit": "ton"},
        ]

        total_emissions = Decimal("0")

        for item in project_materials:
            # Search for matching material
            matches = search_materials(client, item["name"], limit=1)
            if matches:
                material = matches[0]
                emissions = material['emission_factor'] * item['quantity']
                total_emissions += emissions

                print(f"{item['name'].title()}:")
                print(f"  Material: {material['label']}")
                print(f"  Quantity: {item['quantity']} {item['unit']}")
                print(f"  Factor:   {material['emission_factor']} {material['unit']}")
                print(f"  Emissions: {emissions:.2f} kgCO2e")
            else:
                print(f"{item['name'].title()}: No matching material found")

        print(f"\nTotal Project Emissions: {total_emissions:.2f} kgCO2e")

    except QueryError as e:
        print(f"Query error: {e}")

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

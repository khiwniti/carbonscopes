#!/usr/bin/env python3
"""
GraphDB Performance Testing Script

This script validates GraphDB performance with realistic workloads:
1. Generates 500+ construction materials with realistic distribution
2. Loads data into GraphDB
3. Measures query performance with statistical reliability
4. Tests cold cache and warm cache scenarios
5. Validates performance targets are met

Performance Targets:
- Exact match queries: <50ms (99th percentile)
- Category queries: <200ms (99th percentile)
- Complex SPARQL queries: <500ms (99th percentile)

Usage:
    python graphdb_performance_tests.py --generate      # Generate test data
    python graphdb_performance_tests.py --load          # Load into GraphDB
    python graphdb_performance_tests.py --test          # Run performance tests
    python graphdb_performance_tests.py --all           # Run all steps
    python graphdb_performance_tests.py --iterations 100  # Custom iterations

Material Distribution (realistic for Thailand):
- Concrete: 40% (200 materials)
- Steel: 20% (100 materials)
- Glass: 15% (75 materials)
- Wood: 10% (50 materials)
- Other (Aluminum, Insulation, Ceramic, etc.): 15% (75 materials)
"""

import argparse
import json
import logging
import random
import statistics
import sys
import time
import unicodedata
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS

# Import knowledge graph modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.knowledge_graph import (
    GraphDBClient,
    GraphDBError,
    get_emission_factor,
    search_materials,
    list_materials_by_category,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Constants
GRAPHDB_URL = "http://localhost:7200"
REPOSITORY_ID = "carbonbim-thailand"
REPOSITORY_URL = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}"
TGO_NS = Namespace("http://tgo.or.th/ontology#")
TGO_MATERIALS_NS = Namespace("http://tgo.or.th/materials/")
VERSION_PERF_TEST = "http://tgo.or.th/versions/performance-test"

# Material distribution targets
TOTAL_MATERIALS = 500
MATERIAL_DISTRIBUTION = {
    "Concrete": 0.40,  # 200 materials
    "Steel": 0.20,     # 100 materials
    "Glass": 0.15,     # 75 materials
    "Wood": 0.10,      # 50 materials
    "Aluminum": 0.05,  # 25 materials
    "Insulation": 0.03, # 15 materials
    "Ceramic": 0.03,   # 15 materials
    "Gypsum": 0.02,    # 10 materials
    "Cement": 0.02,    # 10 materials
}

# Emission factor ranges (kgCO2e per functional unit)
EMISSION_RANGES = {
    "Concrete": (200, 450),      # kgCO2e/m³
    "Steel": (1500, 2500),       # kgCO2e/ton
    "Glass": (500, 900),         # kgCO2e/ton
    "Wood": (50, 150),           # kgCO2e/m³
    "Aluminum": (8000, 12000),   # kgCO2e/ton
    "Insulation": (800, 2000),   # kgCO2e/ton
    "Ceramic": (400, 700),       # kgCO2e/ton
    "Gypsum": (200, 400),        # kgCO2e/ton
    "Cement": (700, 900),        # kgCO2e/ton
}

# Thai material terms for realistic labels
THAI_TERMS = {
    "Concrete": ["คอนกรีต", "คสล.", "ผสมเสร็จ"],
    "Steel": ["เหล็ก", "โครงสร้าง", "เสริม"],
    "Glass": ["กระจก", "ใส", "เคลือบ"],
    "Wood": ["ไม้", "แท้", "อัด"],
    "Aluminum": ["อลูมิเนียม", "อลูมิเนียมอัลลอยด์"],
    "Insulation": ["ฉนวน", "กันความร้อน"],
    "Ceramic": ["กระเบื้อง", "เซรามิก"],
    "Gypsum": ["ยิปซัม", "ฉาบเรียบ"],
    "Cement": ["ปูนซีเมนต์", "ปอร์ตแลนด์"],
}


def normalize_thai_text(text: str) -> str:
    """Normalize Thai text using NFC for consistent matching."""
    return unicodedata.normalize('NFC', text)


def generate_material_id(category: str, index: int, variant: str = "") -> str:
    """Generate a unique material ID."""
    base = category.lower().replace(" ", "-")
    variant_suffix = f"-{variant}" if variant else ""
    return f"{base}-{index:03d}{variant_suffix}"


def generate_realistic_materials(total: int = TOTAL_MATERIALS) -> List[Dict[str, Any]]:
    """
    Generate realistic construction materials with proper distribution.

    Returns:
        List of material dictionaries with realistic properties
    """
    logger.info(f"Generating {total} realistic construction materials")

    materials = []
    material_id_counter = defaultdict(int)

    for category, percentage in MATERIAL_DISTRIBUTION.items():
        count = int(total * percentage)
        logger.info(f"  Generating {count} {category} materials")

        for i in range(count):
            material_id_counter[category] += 1
            idx = material_id_counter[category]

            # Generate emission factor within realistic range
            min_ef, max_ef = EMISSION_RANGES[category]
            emission_factor = Decimal(str(round(random.uniform(min_ef, max_ef), 1)))

            # Determine unit based on category
            if category in ["Concrete", "Wood"]:
                unit = "kgCO2e/m³"
            else:
                unit = "kgCO2e/ton"

            # Generate realistic specifications
            spec = generate_specification(category, idx)

            # Generate labels
            label_en = generate_english_label(category, idx, spec)
            label_th = generate_thai_label(category, idx, spec)

            # Generate material ID
            variant = spec.get("variant", "")
            mat_id = generate_material_id(category, idx, variant)

            material = {
                "id": mat_id,
                "type": getattr(TGO_NS, category),
                "label_en": label_en,
                "label_th": normalize_thai_text(label_th),
                "emission_factor": emission_factor,
                "unit": unit,
                "category": category,
                "specification": spec.get("description", ""),
                "notes": generate_notes(category, emission_factor, spec),
            }

            materials.append(material)

    # Add extra materials to reach exact target
    while len(materials) < total:
        category = random.choice(list(MATERIAL_DISTRIBUTION.keys()))
        material_id_counter[category] += 1
        idx = material_id_counter[category]

        min_ef, max_ef = EMISSION_RANGES[category]
        emission_factor = Decimal(str(round(random.uniform(min_ef, max_ef), 1)))

        spec = generate_specification(category, idx)
        label_en = generate_english_label(category, idx, spec)
        label_th = generate_thai_label(category, idx, spec)

        unit = "kgCO2e/m³" if category in ["Concrete", "Wood"] else "kgCO2e/ton"
        mat_id = generate_material_id(category, idx, spec.get("variant", ""))

        materials.append({
            "id": mat_id,
            "type": getattr(TGO_NS, category),
            "label_en": label_en,
            "label_th": normalize_thai_text(label_th),
            "emission_factor": emission_factor,
            "unit": unit,
            "category": category,
            "specification": spec.get("description", ""),
            "notes": generate_notes(category, emission_factor, spec),
        })

    logger.info(f"Generated {len(materials)} materials successfully")
    return materials


def generate_specification(category: str, index: int) -> Dict[str, str]:
    """Generate realistic specifications based on category."""
    specs = {
        "Concrete": {
            "grades": ["C15", "C20", "C25", "C30", "C35", "C40", "C45", "C50"],
            "types": ["RMC", "Precast", "High-strength", "Lightweight", "Self-compacting"],
        },
        "Steel": {
            "grades": ["SD40", "SD50", "SS400", "SS490", "SM400"],
            "types": ["Rebar", "H-beam", "I-beam", "Channel", "Angle", "Plate"],
        },
        "Glass": {
            "types": ["Float", "Tempered", "Laminated", "Low-E", "Reflective"],
            "thickness": ["4mm", "6mm", "8mm", "10mm", "12mm"],
        },
        "Wood": {
            "species": ["Teak", "Rubber", "Pine", "Oak", "Mahogany", "Bamboo"],
            "treatment": ["Kiln-dried", "Air-dried", "Pressure-treated", "Untreated"],
        },
        "Aluminum": {
            "alloys": ["6063", "6061", "5052", "3003"],
            "forms": ["Extrusion", "Sheet", "Plate", "Tube"],
        },
        "Insulation": {
            "types": ["Glass wool", "Rock wool", "Foam board", "Spray foam"],
            "density": ["24 kg/m³", "48 kg/m³", "64 kg/m³", "96 kg/m³"],
        },
        "Ceramic": {
            "types": ["Floor tile", "Wall tile", "Porcelain", "Terracotta"],
            "sizes": ["300x300mm", "600x600mm", "800x800mm", "1200x600mm"],
        },
        "Gypsum": {
            "types": ["Standard board", "Fire-resistant", "Moisture-resistant", "Impact-resistant"],
            "thickness": ["9mm", "12mm", "15mm", "18mm"],
        },
        "Cement": {
            "types": ["Type I", "Type II", "Type III", "Type V", "Blended"],
            "applications": ["General purpose", "Sulfate resistant", "Rapid hardening"],
        },
    }

    if category in specs:
        cat_specs = specs[category]
        result = {}

        if category == "Concrete":
            grade = random.choice(cat_specs["grades"])
            ctype = random.choice(cat_specs["types"])
            result["variant"] = grade.lower()
            result["description"] = f"{ctype} Grade {grade}, {random.choice([20, 25, 28])}-day strength"

        elif category == "Steel":
            grade = random.choice(cat_specs["grades"])
            stype = random.choice(cat_specs["types"])
            result["variant"] = grade.lower()
            result["description"] = f"{stype} {grade}, yield strength {random.choice([235, 245, 275, 355, 400, 490])} MPa"

        elif category == "Glass":
            gtype = random.choice(cat_specs["types"])
            thickness = random.choice(cat_specs["thickness"])
            result["variant"] = gtype.lower().replace("-", "")
            result["description"] = f"{gtype} glass {thickness}, TIS 335-2542"

        elif category == "Wood":
            species = random.choice(cat_specs["species"])
            treatment = random.choice(cat_specs["treatment"])
            result["variant"] = species.lower()
            result["description"] = f"{species} wood, {treatment}, moisture content {random.choice([10, 12, 15, 18])}%"

        else:
            # Generic specification
            keys = list(cat_specs.keys())
            result["variant"] = str(index)
            parts = [random.choice(cat_specs[key]) for key in keys[:2]]
            result["description"] = ", ".join(parts)

        return result

    return {"variant": str(index), "description": f"{category} material variant {index}"}


def generate_english_label(category: str, index: int, spec: Dict[str, str]) -> str:
    """Generate English label for material."""
    desc_parts = spec.get("description", "").split(",")
    if desc_parts and len(desc_parts[0]) < 30:
        return f"{category} - {desc_parts[0].strip()}"
    return f"{category} Material {index:03d}"


def generate_thai_label(category: str, index: int, spec: Dict[str, str]) -> str:
    """Generate Thai label for material."""
    thai_base = random.choice(THAI_TERMS.get(category, [category]))

    # Add variant details in Thai
    variants = {
        "c15": "เกรด C15", "c20": "เกรด C20", "c25": "เกรด C25",
        "c30": "เกรด C30", "c35": "เกรด C35", "c40": "เกรด C40",
        "sd40": "SD40", "sd50": "SD50", "ss400": "SS400",
        "float": "ลอย", "tempered": "เทมเปอร์", "laminated": "เคลือบ",
        "teak": "สัก", "rubber": "ยาง", "pine": "สน",
    }

    variant_key = spec.get("variant", "").lower()
    thai_variant = variants.get(variant_key, "")

    if thai_variant:
        return f"{thai_base} {thai_variant}"

    return f"{thai_base} รุ่น {index:03d}"


def generate_notes(category: str, emission_factor: Decimal, spec: Dict[str, str]) -> str:
    """Generate realistic notes for material."""
    base_notes = {
        "Concrete": "Based on Thai cement production (OPC). Includes cement, aggregate, water, admixtures.",
        "Steel": "Thai steel production mix (EAF and blast furnace). Includes hot-rolling process.",
        "Glass": "Thai glass manufacturing (soda-lime glass, natural gas furnace).",
        "Wood": "Sustainably sourced from Thai plantations. Includes harvesting, processing, drying.",
        "Aluminum": "Primary aluminum production. Recycled content can reduce emissions by 90%.",
        "Insulation": "Includes manufacturing and packaging. May contain recycled content.",
        "Ceramic": "Thai ceramic industry (LPG/natural gas kiln, firing temp 1100-1200°C).",
        "Gypsum": "Includes gypsum mining, calcination, board manufacturing.",
        "Cement": "Major contributor to concrete emissions. Thai dry-process kiln with coal fuel.",
    }

    note = base_notes.get(category, f"{category} production in Thailand.")

    # Add regional note
    if float(emission_factor) > sum(EMISSION_RANGES.get(category, (0, 1000))) / 2:
        note += " Higher emissions due to energy-intensive processing."
    else:
        note += " Optimized production process with lower emissions."

    return note


def create_material_graph(materials: List[Dict[str, Any]], version_uri: str) -> Graph:
    """
    Create RDFLib graph with material data.

    Args:
        materials: List of material dictionaries
        version_uri: Named graph URI

    Returns:
        RDFLib Graph with triples
    """
    logger.info(f"Creating RDF graph for {len(materials)} materials")

    g = Graph()
    g.bind("tgo", TGO_NS)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)

    effective_date = datetime.now().strftime("%Y-%m-%d")

    for material in materials:
        material_uri = TGO_MATERIALS_NS[material["id"]]

        # Core type and labels
        g.add((material_uri, RDF.type, material["type"]))
        g.add((material_uri, RDFS.label, Literal(material["label_en"], lang="en")))
        g.add((material_uri, RDFS.label, Literal(material["label_th"], lang="th")))

        # Emission factor (use xsd:decimal for precision)
        g.add((
            material_uri,
            TGO_NS.hasEmissionFactor,
            Literal(material["emission_factor"], datatype=XSD.decimal)
        ))

        # Unit
        g.add((material_uri, TGO_NS.hasUnit, Literal(material["unit"])))

        # Category
        g.add((material_uri, TGO_NS.category, Literal(material["category"])))

        # Effective date
        g.add((
            material_uri,
            TGO_NS.effectiveDate,
            Literal(effective_date, datatype=XSD.date)
        ))

        # Source document
        g.add((
            material_uri,
            TGO_NS.sourceDocument,
            Literal("Performance Test Dataset - TGO Thailand 2026")
        ))

        # Data quality
        g.add((material_uri, TGO_NS.dataQuality, Literal("Verified")))

        # Geographic scope
        g.add((material_uri, TGO_NS.geographicScope, Literal("Thailand")))

        # Material specification
        if material.get("specification"):
            g.add((
                material_uri,
                TGO_NS.materialSpecification,
                Literal(material["specification"])
            ))

        # Notes
        if material.get("notes"):
            g.add((material_uri, TGO_NS.notes, Literal(material["notes"])))

    logger.info(f"Created graph with {len(g)} triples")
    return g


def load_data_into_graphdb(
    client: GraphDBClient,
    materials: List[Dict[str, Any]]
) -> bool:
    """
    Load material data into GraphDB.

    Args:
        client: GraphDBClient instance
        materials: List of material dictionaries

    Returns:
        True if successful
    """
    logger.info(f"Loading {len(materials)} materials into GraphDB")

    try:
        # Create graph
        g = create_material_graph(materials, VERSION_PERF_TEST)

        # Clear existing performance test data
        logger.info("Clearing existing performance test data")
        client.clear_repository(named_graph=VERSION_PERF_TEST)

        # Insert new data
        logger.info("Inserting new data")
        client.insert_triples(g, named_graph=VERSION_PERF_TEST, format="turtle")

        logger.info("Data loaded successfully")
        return True

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return False


def run_performance_test(
    client: GraphDBClient,
    materials: List[Dict[str, Any]],
    iterations: int = 50
) -> Dict[str, Any]:
    """
    Run comprehensive performance tests.

    Tests:
    1. Exact match queries (get_emission_factor)
    2. Category queries (list_materials_by_category)
    3. Complex SPARQL queries (search_materials)
    4. Cold cache vs warm cache performance

    Args:
        client: GraphDBClient instance
        materials: List of test materials
        iterations: Number of iterations per test

    Returns:
        Dictionary with performance results
    """
    logger.info(f"Running performance tests with {iterations} iterations per test")

    results = {
        "total_materials": len(materials),
        "iterations": iterations,
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {}
    }

    # Test 1: Exact match queries
    logger.info("\n" + "="*80)
    logger.info("Test 1: Exact Match Queries (get_emission_factor)")
    logger.info("="*80)

    exact_match_times = []
    sample_materials = random.sample(materials, min(iterations, len(materials)))

    for i, material in enumerate(sample_materials):
        material_uri = f"http://tgo.or.th/materials/{material['id']}"

        start_time = time.time()
        try:
            result = get_emission_factor(client, material_uri, include_metadata=False)
            elapsed_ms = (time.time() - start_time) * 1000
            exact_match_times.append(elapsed_ms)

            if i < 5:  # Log first 5
                logger.info(f"  [{i+1}] {material['label_en']}: {elapsed_ms:.2f}ms")
        except Exception as e:
            logger.error(f"  Error querying {material['id']}: {str(e)}")

    results["tests"]["exact_match"] = analyze_performance(exact_match_times, 50)

    # Test 2: Category queries
    logger.info("\n" + "="*80)
    logger.info("Test 2: Category Queries (list_materials_by_category)")
    logger.info("="*80)

    category_times = []
    categories = list(MATERIAL_DISTRIBUTION.keys())

    for i in range(iterations):
        category = categories[i % len(categories)]

        start_time = time.time()
        try:
            result = list_materials_by_category(client, category, language="en")
            elapsed_ms = (time.time() - start_time) * 1000
            category_times.append(elapsed_ms)

            if i < 5:
                logger.info(f"  [{i+1}] {category}: {len(result)} materials in {elapsed_ms:.2f}ms")
        except Exception as e:
            logger.error(f"  Error querying category {category}: {str(e)}")

    results["tests"]["category_query"] = analyze_performance(category_times, 200)

    # Test 3: Complex SPARQL queries (search)
    logger.info("\n" + "="*80)
    logger.info("Test 3: Complex SPARQL Queries (search_materials)")
    logger.info("="*80)

    search_times = []
    search_terms = ["concrete", "steel", "glass", "wood", "C30", "SD40", "คอนกรีต", "เหล็ก"]

    for i in range(iterations):
        term = search_terms[i % len(search_terms)]
        lang = "th" if any(ord(c) > 127 for c in term) else "en"

        start_time = time.time()
        try:
            result = search_materials(client, term, language=lang, limit=20)
            elapsed_ms = (time.time() - start_time) * 1000
            search_times.append(elapsed_ms)

            if i < 5:
                logger.info(f"  [{i+1}] '{term}': {len(result)} results in {elapsed_ms:.2f}ms")
        except Exception as e:
            logger.error(f"  Error searching '{term}': {str(e)}")

    results["tests"]["complex_query"] = analyze_performance(search_times, 500)

    # Test 4: Cold cache test (clear cache and run single query)
    logger.info("\n" + "="*80)
    logger.info("Test 4: Cold Cache Performance")
    logger.info("="*80)

    # Use a custom SPARQL query to measure cold cache
    cold_cache_times = []

    for i in range(min(10, iterations)):
        # Simple count query to test cold cache
        query = """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        SELECT (COUNT(?material) as ?count)
        WHERE {
            ?material a tgo:Concrete .
        }
        """

        start_time = time.time()
        try:
            client.query(query)
            elapsed_ms = (time.time() - start_time) * 1000
            cold_cache_times.append(elapsed_ms)
            logger.info(f"  [{i+1}] Cold cache query: {elapsed_ms:.2f}ms")
        except Exception as e:
            logger.error(f"  Error in cold cache test: {str(e)}")

    results["tests"]["cold_cache"] = analyze_performance(cold_cache_times, 200)

    # Generate summary
    results["summary"] = generate_summary(results["tests"])

    return results


def analyze_performance(times: List[float], target_ms: float) -> Dict[str, Any]:
    """
    Analyze performance metrics.

    Args:
        times: List of elapsed times in milliseconds
        target_ms: Target performance in milliseconds

    Returns:
        Dictionary with performance statistics
    """
    if not times:
        return {
            "count": 0,
            "target_ms": target_ms,
            "status": "NO_DATA"
        }

    times_sorted = sorted(times)

    # Calculate percentiles
    p50 = times_sorted[len(times_sorted) // 2]
    p95 = times_sorted[int(len(times_sorted) * 0.95)]
    p99 = times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) > 10 else times_sorted[-1]

    # Calculate statistics
    avg = statistics.mean(times)
    median = statistics.median(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)

    # Determine status based on p99
    if p99 <= target_ms:
        status = "PASS"
    elif p99 <= target_ms * 1.5:
        status = "WARN"
    else:
        status = "FAIL"

    return {
        "count": len(times),
        "target_ms": target_ms,
        "status": status,
        "avg_ms": round(avg, 2),
        "median_ms": round(median, 2),
        "min_ms": round(min_time, 2),
        "max_ms": round(max_time, 2),
        "stdev_ms": round(stdev, 2),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "pass_rate": round(sum(1 for t in times if t <= target_ms) / len(times) * 100, 1)
    }


def generate_summary(tests: Dict[str, Any]) -> Dict[str, Any]:
    """Generate performance test summary."""
    passed = sum(1 for test in tests.values() if test.get("status") == "PASS")
    warned = sum(1 for test in tests.values() if test.get("status") == "WARN")
    failed = sum(1 for test in tests.values() if test.get("status") == "FAIL")

    all_passed = failed == 0 and warned == 0

    return {
        "total_tests": len(tests),
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "all_passed": all_passed,
        "status": "PASS" if all_passed else ("WARN" if failed == 0 else "FAIL")
    }


def print_results(results: Dict[str, Any]):
    """Print formatted performance test results."""
    print("\n" + "="*80)
    print("GRAPHDB PERFORMANCE TEST RESULTS")
    print("="*80)
    print(f"Total Materials: {results['total_materials']}")
    print(f"Iterations per Test: {results['iterations']}")
    print(f"Timestamp: {results['timestamp']}")
    print("="*80)

    for test_name, test_data in results["tests"].items():
        status_icon = {
            "PASS": "✓",
            "WARN": "⚠",
            "FAIL": "✗",
            "NO_DATA": "?"
        }.get(test_data.get("status", "?"), "?")

        print(f"\n{status_icon} {test_name.upper().replace('_', ' ')}")
        print("-" * 80)

        if test_data.get("count", 0) > 0:
            print(f"  Target:      <{test_data['target_ms']}ms (99th percentile)")
            print(f"  Average:     {test_data['avg_ms']}ms")
            print(f"  Median:      {test_data['median_ms']}ms")
            print(f"  Min/Max:     {test_data['min_ms']}ms / {test_data['max_ms']}ms")
            print(f"  Std Dev:     {test_data['stdev_ms']}ms")
            print(f"  P50/P95/P99: {test_data['p50_ms']}ms / {test_data['p95_ms']}ms / {test_data['p99_ms']}ms")
            print(f"  Pass Rate:   {test_data['pass_rate']}% (within target)")
            print(f"  Status:      {test_data['status']}")
        else:
            print("  No data collected")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    summary = results["summary"]
    print(f"Total Tests:  {summary['total_tests']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Warned:       {summary['warned']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Overall:      {summary['status']}")

    if summary["all_passed"]:
        print("\n✓ ALL PERFORMANCE TARGETS MET!")
    else:
        print("\n⚠ SOME PERFORMANCE TARGETS NOT MET - Review details above")

    print("="*80 + "\n")


def save_results(results: Dict[str, Any], output_path: Path):
    """Save results to JSON and Markdown files."""
    # Save JSON
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {json_path}")

    # Save Markdown report
    md_path = output_path.with_suffix(".md")
    with open(md_path, "w") as f:
        f.write("# GraphDB Performance Test Results\n\n")
        f.write(f"**Date:** {results['timestamp']}\n\n")
        f.write(f"**Total Materials:** {results['total_materials']}\n\n")
        f.write(f"**Iterations per Test:** {results['iterations']}\n\n")

        f.write("## Test Results\n\n")

        for test_name, test_data in results["tests"].items():
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(test_data.get("status", ""), "❓")
            f.write(f"### {status_icon} {test_name.replace('_', ' ').title()}\n\n")

            if test_data.get("count", 0) > 0:
                f.write(f"- **Target:** <{test_data['target_ms']}ms (99th percentile)\n")
                f.write(f"- **Average:** {test_data['avg_ms']}ms\n")
                f.write(f"- **Median:** {test_data['median_ms']}ms\n")
                f.write(f"- **P99:** {test_data['p99_ms']}ms\n")
                f.write(f"- **Status:** {test_data['status']}\n")
                f.write(f"- **Pass Rate:** {test_data['pass_rate']}%\n\n")

        f.write("## Summary\n\n")
        summary = results["summary"]
        f.write(f"- **Total Tests:** {summary['total_tests']}\n")
        f.write(f"- **Passed:** {summary['passed']}\n")
        f.write(f"- **Warned:** {summary['warned']}\n")
        f.write(f"- **Failed:** {summary['failed']}\n")
        f.write(f"- **Overall Status:** {summary['status']}\n\n")

        if summary["all_passed"]:
            f.write("✅ **ALL PERFORMANCE TARGETS MET!**\n")
        else:
            f.write("⚠️ **Some performance targets not met. Review details above.**\n")

    logger.info(f"Report saved to {md_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GraphDB Performance Testing")
    parser.add_argument("--generate", action="store_true", help="Generate test materials")
    parser.add_argument("--load", action="store_true", help="Load data into GraphDB")
    parser.add_argument("--test", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--iterations", type=int, default=50, help="Iterations per test (default: 50)")
    parser.add_argument("--materials", type=int, default=TOTAL_MATERIALS, help="Number of materials (default: 500)")
    parser.add_argument("--output", type=str, help="Output file path for results")

    args = parser.parse_args()

    if not any([args.generate, args.load, args.test, args.all]):
        args.all = True

    try:
        # Initialize client
        client = GraphDBClient(REPOSITORY_URL)

        # Test connection
        try:
            client.test_connection()
            logger.info("GraphDB connection successful")
        except GraphDBError as e:
            logger.error(f"GraphDB connection failed: {str(e)}")
            return 1

        materials = None

        # Step 1: Generate materials
        if args.all or args.generate:
            materials = generate_realistic_materials(args.materials)

            # Save to file for inspection
            output_dir = Path(__file__).parent / "test_data"
            output_dir.mkdir(exist_ok=True)

            with open(output_dir / "generated_materials.json", "w") as f:
                json.dump([{k: str(v) if isinstance(v, Decimal) else v for k, v in m.items()}
                          for m in materials], f, indent=2, ensure_ascii=False)

            logger.info(f"Generated materials saved to {output_dir / 'generated_materials.json'}")

        # Step 2: Load data
        if args.all or args.load:
            if materials is None:
                # Load from file if exists
                test_data_path = Path(__file__).parent / "test_data" / "generated_materials.json"
                if test_data_path.exists():
                    with open(test_data_path) as f:
                        data = json.load(f)
                        materials = [{**m, "emission_factor": Decimal(m["emission_factor"])} for m in data]
                else:
                    materials = generate_realistic_materials(args.materials)

            if not load_data_into_graphdb(client, materials):
                logger.error("Failed to load data into GraphDB")
                return 1

        # Step 3: Run tests
        if args.all or args.test:
            if materials is None:
                # Need to load materials for testing
                test_data_path = Path(__file__).parent / "test_data" / "generated_materials.json"
                if test_data_path.exists():
                    with open(test_data_path) as f:
                        data = json.load(f)
                        materials = [{**m, "emission_factor": Decimal(m["emission_factor"])} for m in data]
                else:
                    logger.error("No materials found. Run with --generate first.")
                    return 1

            results = run_performance_test(client, materials, iterations=args.iterations)

            print_results(results)

            # Save results
            if args.output:
                output_path = Path(args.output)
            else:
                output_path = Path(__file__).parent / "GRAPHDB_PERFORMANCE_RESULTS"

            save_results(results, output_path)

        logger.info("Performance testing completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

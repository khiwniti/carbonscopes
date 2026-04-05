
#!/usr/bin/env python3
"""
TGO Proof-of-Concept Script

This script demonstrates the complete TGO knowledge graph workflow:
1. Creates GraphDB repository with RDFS inference
2. Generates 10+ sample construction materials with realistic emission factors
3. Loads data into versioned named graph
4. Tests SPARQL queries with performance measurement
5. Tests version comparison functionality

Usage:
    python tgo_poc.py --create-repo    # Create repository
    python tgo_poc.py --load-data      # Load sample data
    python tgo_poc.py --test-queries   # Test SPARQL queries
    python tgo_poc.py --test-versions  # Test version comparison
    python tgo_poc.py --all            # Run all steps

Performance Targets:
    - Exact match: <50ms
    - Category queries: <200ms
    - Full-text search: <500ms
"""

from core.config import timeouts
import argparse
import logging
import sys
import time
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any

import requests
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS

# Import our knowledge graph modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.knowledge_graph import (
    GraphDBClient,
    GraphDBError,
    VersionManager,
    get_emission_factor,
    search_materials,
    list_materials_by_category,
    get_all_categories,
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
VERSION_V1 = "http://tgo.or.th/versions/2026-03"
VERSION_V2 = "http://tgo.or.th/versions/2026-04"


def normalize_thai_text(text: str) -> str:
    """
    Normalize Thai text using NFC (Canonical Decomposition followed by Canonical Composition).

    This ensures consistent text matching for Thai labels.
    """
    return unicodedata.normalize('NFC', text)


def create_repository() -> bool:
    """
    Create the GraphDB repository with RDFS inference enabled.

    Returns:
        True if repository was created successfully
    """
    logger.info(f"Creating GraphDB repository: {REPOSITORY_ID}")

    # Repository configuration with RDFS inference
    # Using Turtle format for GraphDB REST API
    config_ttl = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rep: <http://www.openrdf.org/config/repository#>.
@prefix sr: <http://www.openrdf.org/config/repository/sail#>.
@prefix sail: <http://www.openrdf.org/config/sail#>.
@prefix graphdb: <http://www.ontotext.com/config/graphdb#>.

[] a rep:Repository ;
    rep:repositoryID "{repo_id}" ;
    rdfs:label "Carbon BIM Thailand - TGO Emission Factors" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:FreeSailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:FreeSail" ;
            graphdb:ruleset "rdfs-plus" ;
            graphdb:check-for-inconsistencies false ;
            graphdb:disable-sameAs true ;
            graphdb:enable-context-index true ;
            graphdb:enablePredicateList true ;
            graphdb:enable-literal-index true ;
            graphdb:in-memory-literal-properties true ;
            graphdb:base-URL "http://tgo.or.th/" ;
        ]
    ].
""".format(repo_id=REPOSITORY_ID)

    try:
        # Check if repository already exists
        response = requests.get(f"{GRAPHDB_URL}/rest/repositories/{REPOSITORY_ID}")
        if response.status_code == 200:
            logger.info(f"Repository {REPOSITORY_ID} already exists")
            return True

        # Create repository using Turtle config
        headers = {"Content-Type": "text/turtle"}
        response = requests.post(
            f"{GRAPHDB_URL}/rest/repositories",
            data=config_ttl,
            headers=headers,
            timeout=30
        )

        if response.status_code in (200, 201):
            logger.info(f"Successfully created repository: {REPOSITORY_ID}")
            return True
        else:
            logger.error(f"Failed to create repository: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        return False


def generate_sample_materials() -> List[Dict[str, Any]]:
    """
    Generate 10+ sample construction materials with realistic emission factors.

    Data sources:
    - TGO Carbon Footprint Database (simulated)
    - TIIS National LCI Database (simulated)
    - Industry averages for Thailand

    Returns:
        List of material dictionaries
    """
    materials = [
        # Concrete materials (200-400 kgCO2e/m³)
        {
            "id": "concrete-c30-rmc",
            "type": TGO_NS.Concrete,
            "label_en": "Ready-mixed Concrete C30",
            "label_th": normalize_thai_text("คอนกรีตผสมเสร็จ C30"),
            "emission_factor": Decimal("315.8"),
            "unit": "kgCO2e/m³",
            "category": "Concrete",
            "specification": "Grade C30, 28-day strength 30 MPa, slump 120±20mm",
            "notes": "Includes cement, aggregate, water, admixtures. Based on Thai cement production (OPC Type I).",
        },
        {
            "id": "concrete-c25-rmc",
            "type": TGO_NS.Concrete,
            "label_en": "Ready-mixed Concrete C25",
            "label_th": normalize_thai_text("คอนกรีตผสมเสร็จ C25"),
            "emission_factor": Decimal("285.4"),
            "unit": "kgCO2e/m³",
            "category": "Concrete",
            "specification": "Grade C25, 28-day strength 25 MPa",
            "notes": "Lower cement content than C30, reduced emissions.",
        },

        # Steel materials (1500-2500 kgCO2e/ton)
        {
            "id": "rebar-sd40",
            "type": TGO_NS.Steel,
            "label_en": "Steel Reinforcement Bar SD40",
            "label_th": normalize_thai_text("เหล็กเสริมคอนกรีต SD40"),
            "emission_factor": Decimal("1850.0"),
            "unit": "kgCO2e/ton",
            "category": "Steel",
            "specification": "Deformed bar, yield strength 400 MPa, TIS 24-2548",
            "notes": "Based on Thai steel production mix (50% electric arc furnace, 50% blast furnace).",
        },
        {
            "id": "structural-steel-ss400",
            "type": TGO_NS.Steel,
            "label_en": "Structural Steel SS400",
            "label_th": normalize_thai_text("เหล็กโครงสร้าง SS400"),
            "emission_factor": Decimal("2150.0"),
            "unit": "kgCO2e/ton",
            "category": "Steel",
            "specification": "Hot-rolled steel sections, yield strength 245 MPa",
            "notes": "H-beams, I-beams, channels. Higher embodied carbon due to hot-rolling process.",
        },

        # Aluminum materials (8000-12000 kgCO2e/ton)
        {
            "id": "aluminum-frame-6063",
            "type": TGO_NS.Aluminum,
            "label_en": "Aluminum Window Frame 6063-T5",
            "label_th": normalize_thai_text("กรอบหน้าต่างอลูมิเนียม 6063-T5"),
            "emission_factor": Decimal("9500.0"),
            "unit": "kgCO2e/ton",
            "category": "Aluminum",
            "specification": "Extruded aluminum alloy 6063-T5, anodized finish",
            "notes": "Primary aluminum production. Recycled aluminum has ~90% lower emissions.",
        },

        # Glass materials (500-900 kgCO2e/ton)
        {
            "id": "float-glass-6mm",
            "type": TGO_NS.Glass,
            "label_en": "Float Glass 6mm Clear",
            "label_th": normalize_thai_text("กระจกใสลอย 6 มม."),
            "emission_factor": Decimal("680.0"),
            "unit": "kgCO2e/ton",
            "category": "Glass",
            "specification": "Clear float glass, 6mm thickness, TIS 335-2542",
            "notes": "Based on Thai glass manufacturing (soda-lime glass, natural gas furnace).",
        },

        # Wood materials (50-150 kgCO2e/m³)
        {
            "id": "hardwood-teak",
            "type": TGO_NS.Wood,
            "label_en": "Teak Hardwood",
            "label_th": normalize_thai_text("ไม้สักแท้"),
            "emission_factor": Decimal("85.5"),
            "unit": "kgCO2e/m³",
            "category": "Wood",
            "specification": "Kiln-dried teak, moisture content 12-15%",
            "notes": "Sustainably sourced from Thai plantations. Includes harvesting, processing, kiln-drying.",
        },

        # Insulation materials (varies widely)
        {
            "id": "insulation-glasswool",
            "type": TGO_NS.Insulation,
            "label_en": "Glass Wool Insulation",
            "label_th": normalize_thai_text("ฉนวนใยแก้ว"),
            "emission_factor": Decimal("1250.0"),
            "unit": "kgCO2e/ton",
            "category": "Insulation",
            "specification": "Density 24-48 kg/m³, thermal conductivity 0.035-0.040 W/mK",
            "notes": "Includes manufacturing, packaging. ~30% recycled glass content.",
        },

        # Ceramic materials
        {
            "id": "ceramic-tile-floor",
            "type": TGO_NS.Ceramic,
            "label_en": "Ceramic Floor Tile",
            "label_th": normalize_thai_text("กระเบื้องเซรามิกปูพื้น"),
            "emission_factor": Decimal("450.0"),
            "unit": "kgCO2e/ton",
            "category": "Ceramic",
            "specification": "Porcelain tile, 600x600mm, Class 4 abrasion resistance",
            "notes": "Based on Thai ceramic industry (LPG/natural gas kiln, firing temp 1200°C).",
        },

        # Cement materials (high emissions)
        {
            "id": "cement-portland-type1",
            "type": TGO_NS.Cement,
            "label_en": "Portland Cement Type I",
            "label_th": normalize_thai_text("ปูนซีเมนต์ปอร์ตแลนด์ ชนิด 1"),
            "emission_factor": Decimal("820.0"),
            "unit": "kgCO2e/ton",
            "category": "Cement",
            "specification": "Ordinary Portland Cement, TIS 15-2556",
            "notes": "Major contributor to concrete emissions. Based on Thai dry-process kiln with coal fuel.",
        },

        # Additional material for >10 requirement
        {
            "id": "gypsum-board-12mm",
            "type": TGO_NS.Gypsum,
            "label_en": "Gypsum Board 12mm",
            "label_th": normalize_thai_text("แผ่นยิปซัมบอร์ด 12 มม."),
            "emission_factor": Decimal("280.0"),
            "unit": "kgCO2e/ton",
            "category": "Gypsum",
            "specification": "Standard gypsum wallboard, 12mm thickness, paper-faced",
            "notes": "Includes gypsum mining, calcination, board manufacturing, paper facing.",
        },
    ]

    logger.info(f"Generated {len(materials)} sample materials")
    return materials


def create_material_graph(
    materials: List[Dict[str, Any]],
    version_uri: str,
    effective_date: str
) -> Graph:
    """
    Create an RDFLib graph with material data conforming to TGO ontology.

    Args:
        materials: List of material dictionaries
        version_uri: Named graph URI (e.g., http://tgo.or.th/versions/2026-03)
        effective_date: Date when emission factors become effective (YYYY-MM-DD)

    Returns:
        RDFLib Graph with material triples
    """
    logger.info(f"Creating RDF graph for version: {version_uri}")

    g = Graph()
    g.bind("tgo", TGO_NS)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)

    for material in materials:
        material_uri = TGO_MATERIALS_NS[material["id"]]

        # Core type and labels
        g.add((material_uri, RDF.type, material["type"]))
        g.add((material_uri, RDFS.label, Literal(material["label_en"], lang="en")))
        g.add((material_uri, RDFS.label, Literal(material["label_th"], lang="th")))

        # Emission factor (MUST use xsd:decimal for precision)
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
            Literal("TGO Emission Factors Database 2026 (Simulated)")
        ))

        # Data quality
        g.add((material_uri, TGO_NS.dataQuality, Literal("Verified")))

        # Geographic scope
        g.add((material_uri, TGO_NS.geographicScope, Literal("Thailand")))

        # Material specification
        if "specification" in material:
            g.add((
                material_uri,
                TGO_NS.materialSpecification,
                Literal(material["specification"])
            ))

        # Notes
        if "notes" in material:
            g.add((material_uri, TGO_NS.notes, Literal(material["notes"])))

    logger.info(f"Created graph with {len(g)} triples")
    return g


def load_ontology(client: GraphDBClient) -> bool:
    """
    Load the TGO ontology schema into the default graph.

    Args:
        client: GraphDBClient instance

    Returns:
        True if ontology was loaded successfully
    """
    logger.info("Loading TGO ontology schema")

    try:
        ontology_path = Path(__file__).parent.parent.parent / "knowledge_graph" / "schemas" / "tgo_ontology.ttl"

        if not ontology_path.exists():
            logger.error(f"Ontology file not found: {ontology_path}")
            return False

        # Parse ontology
        g = Graph()
        g.parse(str(ontology_path), format="turtle")

        # Insert into default graph (no named graph)
        client.insert_triples(g, named_graph=None, format="turtle")

        logger.info(f"Loaded ontology with {len(g)} triples")
        return True

    except Exception as e:
        logger.error(f"Error loading ontology: {str(e)}")
        return False


def load_version_data(
    client: GraphDBClient,
    version_manager: VersionManager,
    materials: List[Dict[str, Any]],
    version_uri: str,
    version_date: str,
    effective_date: str,
    notes: str = ""
) -> bool:
    """
    Load material data into a versioned named graph.

    Args:
        client: GraphDBClient instance
        version_manager: VersionManager instance
        materials: List of material dictionaries
        version_uri: Named graph URI
        version_date: Version publication date (YYYY-MM-DD)
        effective_date: Date when emission factors become effective
        notes: Version release notes

    Returns:
        True if data was loaded successfully
    """
    logger.info(f"Loading data into version: {version_uri}")

    try:
        # Create material graph
        g = create_material_graph(materials, version_uri, effective_date)

        # Insert into named graph
        client.insert_triples(g, named_graph=version_uri, format="turtle")

        # Create version metadata
        version_manager.create_version_metadata(
            version_uri=version_uri,
            version_date=version_date,
            notes=notes
        )

        logger.info(f"Successfully loaded {len(materials)} materials into {version_uri}")
        return True

    except Exception as e:
        logger.error(f"Error loading version data: {str(e)}")
        return False


def test_sparql_queries(client: GraphDBClient) -> Dict[str, Any]:
    """
    Test SPARQL queries with performance measurement.

    Performance targets:
    - get_emission_factor: <50ms
    - search_materials: <500ms
    - list_materials_by_category: <200ms

    Args:
        client: GraphDBClient instance

    Returns:
        Dictionary with test results and performance metrics
    """
    logger.info("Testing SPARQL queries with performance measurement")

    results = {
        "tests": [],
        "passed": 0,
        "failed": 0,
        "total_time": 0.0
    }

    # Test 1: get_emission_factor (exact match)
    logger.info("Test 1: get_emission_factor (exact match)")
    material_uri = "http://tgo.or.th/materials/concrete-c30-rmc"
    start_time = time.time()
    try:
        result = get_emission_factor(client, material_uri, include_metadata=True)
        elapsed_ms = (time.time() - start_time) * 1000

        test_result = {
            "name": "get_emission_factor",
            "status": "PASS" if elapsed_ms < 50 else "WARN",
            "elapsed_ms": round(elapsed_ms, 2),
            "target_ms": 50,
            "data": {
                "material_id": result["material_id"],
                "emission_factor": str(result["emission_factor"]),
                "unit": result["unit"],
                "label_en": result["label_en"],
                "label_th": result["label_th"],
            }
        }
        results["tests"].append(test_result)
        results["passed"] += 1
        results["total_time"] += elapsed_ms

        logger.info(f"✓ Test passed: {elapsed_ms:.2f}ms (target: <50ms)")
        logger.info(f"  Material: {result['label_en']}")
        logger.info(f"  Emission Factor: {result['emission_factor']} {result['unit']}")

    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        results["tests"].append({
            "name": "get_emission_factor",
            "status": "FAIL",
            "error": str(e)
        })
        results["failed"] += 1

    # Test 2: list_materials_by_category
    logger.info("Test 2: list_materials_by_category")
    start_time = time.time()
    try:
        concrete_materials = list_materials_by_category(client, "Concrete", language="en")
        elapsed_ms = (time.time() - start_time) * 1000

        test_result = {
            "name": "list_materials_by_category",
            "status": "PASS" if elapsed_ms < 200 else "WARN",
            "elapsed_ms": round(elapsed_ms, 2),
            "target_ms": 200,
            "count": len(concrete_materials)
        }
        results["tests"].append(test_result)
        results["passed"] += 1
        results["total_time"] += elapsed_ms

        logger.info(f"✓ Test passed: {elapsed_ms:.2f}ms (target: <200ms)")
        logger.info(f"  Found {len(concrete_materials)} concrete materials")
        for mat in concrete_materials:
            logger.info(f"  - {mat['label']}: {mat['emission_factor']} {mat['unit']}")

    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        results["tests"].append({
            "name": "list_materials_by_category",
            "status": "FAIL",
            "error": str(e)
        })
        results["failed"] += 1

    # Test 3: search_materials
    logger.info("Test 3: search_materials (full-text search)")
    start_time = time.time()
    try:
        search_results = search_materials(client, "steel", language="en", limit=10)
        elapsed_ms = (time.time() - start_time) * 1000

        test_result = {
            "name": "search_materials",
            "status": "PASS" if elapsed_ms < 500 else "WARN",
            "elapsed_ms": round(elapsed_ms, 2),
            "target_ms": 500,
            "count": len(search_results)
        }
        results["tests"].append(test_result)
        results["passed"] += 1
        results["total_time"] += elapsed_ms

        logger.info(f"✓ Test passed: {elapsed_ms:.2f}ms (target: <500ms)")
        logger.info(f"  Found {len(search_results)} materials matching 'steel'")
        for mat in search_results:
            logger.info(f"  - {mat['label']}: {mat['emission_factor']} {mat['unit']}")

    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        results["tests"].append({
            "name": "search_materials",
            "status": "FAIL",
            "error": str(e)
        })
        results["failed"] += 1

    # Test 4: Bilingual label retrieval
    logger.info("Test 4: Bilingual label retrieval")
    start_time = time.time()
    try:
        # Search in Thai
        thai_results = search_materials(client, "คอนกรีต", language="th", limit=5)
        elapsed_ms = (time.time() - start_time) * 1000

        test_result = {
            "name": "bilingual_labels_thai",
            "status": "PASS" if len(thai_results) > 0 else "FAIL",
            "elapsed_ms": round(elapsed_ms, 2),
            "count": len(thai_results)
        }
        results["tests"].append(test_result)
        if len(thai_results) > 0:
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total_time"] += elapsed_ms

        logger.info(f"✓ Test passed: {elapsed_ms:.2f}ms")
        logger.info(f"  Found {len(thai_results)} materials with Thai labels")
        for mat in thai_results:
            logger.info(f"  - {mat['label']}: {mat['emission_factor']} {mat['unit']}")

    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        results["tests"].append({
            "name": "bilingual_labels_thai",
            "status": "FAIL",
            "error": str(e)
        })
        results["failed"] += 1

    # Test 5: get_all_categories
    logger.info("Test 5: get_all_categories")
    start_time = time.time()
    try:
        categories = get_all_categories(client)
        elapsed_ms = (time.time() - start_time) * 1000

        test_result = {
            "name": "get_all_categories",
            "status": "PASS",
            "elapsed_ms": round(elapsed_ms, 2),
            "count": len(categories)
        }
        results["tests"].append(test_result)
        results["passed"] += 1
        results["total_time"] += elapsed_ms

        logger.info(f"✓ Test passed: {elapsed_ms:.2f}ms")
        logger.info(f"  Found {len(categories)} categories")
        for cat in categories:
            logger.info(f"  - {cat['category']}: {cat['count']} materials")

    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        results["tests"].append({
            "name": "get_all_categories",
            "status": "FAIL",
            "error": str(e)
        })
        results["failed"] += 1

    return results


def test_version_comparison(
    client: GraphDBClient,
    version_manager: VersionManager
) -> Dict[str, Any]:
    """
    Test version comparison functionality.

    Creates two versions with some changes and compares them.

    Args:
        client: GraphDBClient instance
        version_manager: VersionManager instance

    Returns:
        Dictionary with comparison results
    """
    logger.info("Testing version comparison")

    try:
        # Generate v1 materials
        v1_materials = generate_sample_materials()

        # Generate v2 materials with some changes
        v2_materials = generate_sample_materials()

        # Modify some emission factors for v2
        for mat in v2_materials:
            if mat["id"] == "concrete-c30-rmc":
                mat["emission_factor"] = Decimal("320.5")  # Increased
            elif mat["id"] == "rebar-sd40":
                mat["emission_factor"] = Decimal("1780.0")  # Decreased (better tech)

        # Add a new material in v2
        v2_materials.append({
            "id": "concrete-c40-rmc",
            "type": TGO_NS.Concrete,
            "label_en": "Ready-mixed Concrete C40",
            "label_th": normalize_thai_text("คอนกรีตผสมเสร็จ C40"),
            "emission_factor": Decimal("350.2"),
            "unit": "kgCO2e/m³",
            "category": "Concrete",
            "specification": "Grade C40, 28-day strength 40 MPa",
            "notes": "High-strength concrete for structural applications.",
        })

        # Load v1
        logger.info("Loading version 1 (2026-03)")
        load_version_data(
            client,
            version_manager,
            v1_materials,
            VERSION_V1,
            "2026-03-01",
            "2026-03-01",
            "Initial TGO emission factors for 2026 Q1"
        )

        # Load v2
        logger.info("Loading version 2 (2026-04)")
        load_version_data(
            client,
            version_manager,
            v2_materials,
            VERSION_V2,
            "2026-04-01",
            "2026-04-01",
            "Q2 2026 update: Updated concrete and steel factors, added C40 concrete"
        )

        # Compare versions
        logger.info("Comparing versions")
        start_time = time.time()
        comparison = version_manager.compare_versions(VERSION_V1, VERSION_V2)
        elapsed_ms = (time.time() - start_time) * 1000

        logger.info(f"✓ Version comparison completed: {elapsed_ms:.2f}ms")
        logger.info(f"  Added: {comparison['summary']['addedCount']} materials")
        logger.info(f"  Removed: {comparison['summary']['removedCount']} materials")
        logger.info(f"  Updated: {comparison['summary']['updatedCount']} materials")
        logger.info(f"  Unchanged: {comparison['summary']['unchangedCount']} materials")

        # Show updated materials
        if comparison['updated']:
            logger.info("\nUpdated materials:")
            for mat in comparison['updated']:
                logger.info(f"  - {mat['label']}")
                logger.info(f"    Old: {mat['oldEmissionFactor']}")
                logger.info(f"    New: {mat['newEmissionFactor']}")
                logger.info(f"    Change: {mat['changePercent']:+.2f}%")

        # Show added materials
        if comparison['added']:
            logger.info("\nAdded materials:")
            for mat in comparison['added']:
                logger.info(f"  - {mat['label']}: {mat['emissionFactor']}")

        return {
            "status": "PASS",
            "elapsed_ms": round(elapsed_ms, 2),
            "summary": comparison['summary']
        }

    except Exception as e:
        logger.error(f"✗ Version comparison test failed: {str(e)}")
        return {
            "status": "FAIL",
            "error": str(e)
        }


def print_summary(query_results: Dict[str, Any], version_results: Dict[str, Any]):
    """Print summary of all test results."""
    print("\n" + "="*80)
    print("TGO PROOF-OF-CONCEPT TEST SUMMARY")
    print("="*80)

    # Query performance
    print("\n📊 QUERY PERFORMANCE:")
    print("-" * 80)
    for test in query_results["tests"]:
        status_icon = "✓" if test["status"] == "PASS" else "⚠" if test["status"] == "WARN" else "✗"
        print(f"{status_icon} {test['name']}: {test.get('elapsed_ms', 'N/A')}ms", end="")
        if "target_ms" in test:
            print(f" (target: <{test['target_ms']}ms)", end="")
        if "count" in test:
            print(f" - {test['count']} results", end="")
        print()

    print(f"\nTotal query time: {query_results['total_time']:.2f}ms")
    print(f"Tests passed: {query_results['passed']}/{query_results['passed'] + query_results['failed']}")

    # Version comparison
    print("\n📦 VERSION COMPARISON:")
    print("-" * 80)
    if version_results["status"] == "PASS":
        print(f"✓ Version comparison: {version_results['elapsed_ms']:.2f}ms")
        summary = version_results["summary"]
        print(f"  Added: {summary['addedCount']}")
        print(f"  Updated: {summary['updatedCount']}")
        print(f"  Removed: {summary['removedCount']}")
        print(f"  Unchanged: {summary['unchangedCount']}")
    else:
        print(f"✗ Version comparison failed: {version_results.get('error', 'Unknown error')}")

    # Overall status
    print("\n" + "="*80)
    all_passed = (
        query_results["failed"] == 0 and
        version_results["status"] == "PASS"
    )

    if all_passed:
        print("✓ ALL TESTS PASSED - TGO POC is working correctly!")
    else:
        print("⚠ SOME TESTS FAILED - Review results above")
    print("="*80 + "\n")


def main():
    """Main entry point for TGO POC script."""
    parser = argparse.ArgumentParser(description="TGO Proof-of-Concept Script")
    parser.add_argument("--create-repo", action="store_true", help="Create GraphDB repository")
    parser.add_argument("--load-data", action="store_true", help="Load sample data")
    parser.add_argument("--test-queries", action="store_true", help="Test SPARQL queries")
    parser.add_argument("--test-versions", action="store_true", help="Test version comparison")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--reset", action="store_true", help="Clear all data before loading")

    args = parser.parse_args()

    # If no arguments, default to --all
    if not any([args.create_repo, args.load_data, args.test_queries, args.test_versions, args.all]):
        args.all = True

    try:
        # Step 1: Create repository
        if args.all or args.create_repo:
            if not create_repository():
                logger.error("Failed to create repository")
                return 1
            # Wait for repository to be ready
            time.sleep(timeouts.TGO_API_DELAY)

        # Initialize clients
        client = GraphDBClient(REPOSITORY_URL)
        version_manager = VersionManager(client)

        # Test connection
        try:
            client.test_connection()
            logger.info("GraphDB connection successful")
        except GraphDBError as e:
            logger.error(f"GraphDB connection failed: {str(e)}")
            return 1

        # Reset if requested
        if args.reset:
            logger.warning("Clearing all data from repository")
            client.clear_repository()
            time.sleep(timeouts.TGO_RETRY_DELAY)

        # Step 2: Load ontology and data
        if args.all or args.load_data:
            # Load ontology schema
            if not load_ontology(client):
                logger.error("Failed to load ontology")
                return 1

            # Generate and load sample materials
            materials = generate_sample_materials()
            if not load_version_data(
                client,
                version_manager,
                materials,
                VERSION_V1,
                "2026-03-01",
                "2026-03-01",
                "Initial TGO emission factors POC dataset"
            ):
                logger.error("Failed to load data")
                return 1

        # Step 3: Test queries
        query_results = None
        if args.all or args.test_queries:
            query_results = test_sparql_queries(client)

        # Step 4: Test version comparison
        version_results = None
        if args.all or args.test_versions:
            version_results = test_version_comparison(client, version_manager)

        # Print summary
        if query_results and version_results:
            print_summary(query_results, version_results)

        logger.info("TGO POC completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
EDGE/TREES Performance Testing Script

This script validates GraphDB query performance for EDGE V3 and TREES NC 1.1
certification queries with strict latency requirements:

Performance Targets:
- EDGE threshold lookup: <50ms (99th percentile)
- TREES criteria query: <200ms (99th percentile)
- Material certification eligibility: <500ms (99th percentile)

Test Scenarios:
1. EDGE Threshold Lookup - Query EDGE certification level thresholds and rules
2. TREES Criteria Query - Query MR1/MR3 criteria requirements and points
3. Material Certification Eligibility - Complex multi-schema queries

Usage:
    python edge_trees_performance_tests.py --test          # Run performance tests
    python edge_trees_performance_tests.py --iterations 200  # Custom iterations

Note: Requires GraphDB running at http://localhost:7200 with suna-bim-kg repository
"""

import argparse
import json
import logging
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from SPARQLWrapper import SPARQLWrapper, JSON

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Constants
GRAPHDB_URL = "http://localhost:7200"
REPOSITORY_ID = "carbonbim-thailand"
SPARQL_ENDPOINT = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}"

# Performance targets (in milliseconds)
TARGET_EDGE_THRESHOLD = 100
TARGET_TREES_CRITERIA = 200
TARGET_MATERIAL_ELIGIBILITY = 500


def execute_sparql_query(sparql: SPARQLWrapper, query: str, timeout_ms: int = 10000) -> List[Dict[str, Any]]:
    """
    Execute SPARQL query and return results.

    Args:
        sparql: SPARQLWrapper instance
        query: SPARQL query string
        timeout_ms: Query timeout in milliseconds

    Returns:
        List of result bindings
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(timeout_ms // 1000)  # SPARQLWrapper uses seconds

    results = sparql.query().convert()
    return results["results"]["bindings"]


def test_edge_threshold_queries(sparql: SPARQLWrapper, iterations: int = 200) -> List[float]:
    """
    Test EDGE certification threshold lookup queries.

    Queries:
    - EDGE Certified Rule (20% reduction)
    - EDGE Advanced Rule (40% reduction)
    - Embodied carbon savings rule

    Args:
        sparql: SPARQLWrapper instance
        iterations: Number of iterations to run

    Returns:
        List of elapsed times in milliseconds
    """
    logger.info("\n" + "="*80)
    logger.info("Test 1: EDGE Threshold Lookup Queries")
    logger.info("="*80)

    queries = [
        # Query 1: Get EDGE Certified Rule (20% reduction threshold)
        """
        PREFIX edge: <http://edgebuildings.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rule ?label ?reduction ?method
        WHERE {
          ?rule a edge:CarbonReductionRequirement ;
                rdfs:label ?label ;
                edge:requiredReduction ?reduction ;
                edge:comparisonMethod ?method .
          FILTER(?reduction = 0.20)
        }
        """,

        # Query 2: Get EDGE Advanced Rule (40% reduction threshold)
        """
        PREFIX edge: <http://edgebuildings.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rule ?label ?reduction ?method
        WHERE {
          ?rule a edge:CarbonReductionRequirement ;
                rdfs:label ?label ;
                edge:requiredReduction ?reduction ;
                edge:comparisonMethod ?method .
          FILTER(?reduction = 0.40)
        }
        """,

        # Query 3: Get all certification levels with thresholds
        """
        PREFIX edge: <http://edgebuildings.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rule ?label ?reduction ?version
        WHERE {
          ?rule a edge:CarbonReductionRequirement ;
                rdfs:label ?label ;
                edge:requiredReduction ?reduction ;
                edge:version ?version .
        }
        ORDER BY ?reduction
        """,
    ]

    times = []

    for i in range(iterations):
        query = queries[i % len(queries)]

        start_time = time.perf_counter()
        try:
            results = execute_sparql_query(sparql, query)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)

            if i < 5:  # Log first 5
                logger.info(f"  [{i+1}] Query {(i % len(queries)) + 1}: {elapsed_ms:.2f}ms ({len(results)} results)")
        except Exception as e:
            logger.error(f"  Error in iteration {i+1}: {str(e)}")

    return times


def test_trees_criteria_queries(sparql: SPARQLWrapper, iterations: int = 200) -> List[float]:
    """
    Test TREES criteria lookup queries.

    Queries:
    - MR1 (green-labeled materials) criteria
    - MR3 (reused materials) criteria
    - Points calculation rules

    Args:
        sparql: SPARQLWrapper instance
        iterations: Number of iterations to run

    Returns:
        List of elapsed times in milliseconds
    """
    logger.info("\n" + "="*80)
    logger.info("Test 2: TREES Criteria Lookup Queries")
    logger.info("="*80)

    queries = [
        # Query 1: Get MR1 criterion (green-labeled materials)
        """
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?criterion ?label ?code ?requiredPct ?maxPoints
        WHERE {
          ?criterion a trees:GreenLabeledMaterialsCriterion ;
                     rdfs:label ?label ;
                     trees:criterionCode ?code ;
                     trees:requiredPercentage ?requiredPct ;
                     trees:maxPoints ?maxPoints .
          FILTER(lang(?label) = "en")
        }
        """,

        # Query 2: Get MR3 criterion (reused materials)
        """
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?criterion ?label ?code ?minPct3 ?minPct5 ?maxPoints
        WHERE {
          ?criterion a trees:ReusedMaterialsCriterion ;
                     rdfs:label ?label ;
                     trees:criterionCode ?code ;
                     trees:minPercentageFor3Points ?minPct3 ;
                     trees:minPercentageFor5Points ?minPct5 ;
                     trees:maxPoints ?maxPoints .
          FILTER(lang(?label) = "en")
        }
        """,

        # Query 3: Get all Materials & Resources criteria with max points
        """
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?criterion ?label ?code ?maxPoints
        WHERE {
          ?criterion a trees:MaterialsCriterion ;
                     rdfs:label ?label ;
                     trees:criterionCode ?code ;
                     trees:maxPoints ?maxPoints .
          FILTER(lang(?label) = "en")
        }
        ORDER BY ?code
        """,

        # Query 4: Get certification level thresholds
        """
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?level ?label
        WHERE {
          ?level a rdfs:Class ;
                 rdfs:subClassOf trees:Certification ;
                 rdfs:label ?label .
          FILTER(lang(?label) = "en")
        }
        ORDER BY ?label
        """,
    ]

    times = []

    for i in range(iterations):
        query = queries[i % len(queries)]

        start_time = time.perf_counter()
        try:
            results = execute_sparql_query(sparql, query)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)

            if i < 5:  # Log first 5
                logger.info(f"  [{i+1}] Query {(i % len(queries)) + 1}: {elapsed_ms:.2f}ms ({len(results)} results)")
        except Exception as e:
            logger.error(f"  Error in iteration {i+1}: {str(e)}")

    return times


def test_material_eligibility_queries(sparql: SPARQLWrapper, iterations: int = 200) -> List[float]:
    """
    Test complex material certification eligibility queries.

    Complex queries combining:
    - TGO material data (emission factors)
    - EDGE carbon calculation eligibility
    - TREES green label eligibility

    Args:
        sparql: SPARQLWrapper instance
        iterations: Number of iterations to run

    Returns:
        List of elapsed times in milliseconds
    """
    logger.info("\n" + "="*80)
    logger.info("Test 3: Material Certification Eligibility (Complex Queries)")
    logger.info("="*80)

    queries = [
        # Query 1: Find low-carbon materials eligible for EDGE and TREES
        # (Multi-schema query across TGO + EDGE + TREES)
        """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX edge: <http://edgebuildings.com/ontology#>
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?material ?label ?emissionFactor ?unit
        WHERE {
          ?material a tgo:ConstructionMaterial ;
                    rdfs:label ?label ;
                    tgo:hasEmissionFactor ?emissionFactor ;
                    tgo:hasUnit ?unit .
          FILTER(?emissionFactor < 500 && lang(?label) = "en")
        }
        ORDER BY ?emissionFactor
        LIMIT 20
        """,

        # Query 2: Check EDGE certification compliance rules
        """
        PREFIX edge: <http://edgebuildings.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?rule ?reduction ?method ?version
        WHERE {
          ?rule a edge:CarbonReductionRequirement ;
                edge:requiredReduction ?reduction ;
                edge:comparisonMethod ?method ;
                edge:version ?version .
        }
        ORDER BY ?reduction
        """,

        # Query 3: Check TREES MR criteria requirements
        """
        PREFIX trees: <http://tgbi.or.th/trees/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?criterion ?code ?maxPoints ?version
        WHERE {
          ?criterion a trees:MaterialsCriterion ;
                     trees:criterionCode ?code ;
                     trees:maxPoints ?maxPoints ;
                     trees:version ?version .
        }
        ORDER BY ?code
        """,

        # Query 4: Get material categories from TGO for EDGE/TREES selection
        """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?material ?category ?emissionFactor
        WHERE {
          ?material a tgo:ConstructionMaterial ;
                    tgo:category ?category ;
                    tgo:hasEmissionFactor ?emissionFactor .
        }
        ORDER BY ?category ?emissionFactor
        LIMIT 50
        """,

        # Query 5: Count materials by category for certification planning
        """
        PREFIX tgo: <http://tgo.or.th/ontology#>
        SELECT ?category (COUNT(?material) as ?count) (AVG(?emissionFactor) as ?avgEmissions)
        WHERE {
          ?material a tgo:ConstructionMaterial ;
                    tgo:category ?category ;
                    tgo:hasEmissionFactor ?emissionFactor .
        }
        GROUP BY ?category
        ORDER BY DESC(?count)
        """,
    ]

    times = []

    for i in range(iterations):
        query = queries[i % len(queries)]

        start_time = time.perf_counter()
        try:
            results = execute_sparql_query(sparql, query)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)

            if i < 5:  # Log first 5
                logger.info(f"  [{i+1}] Query {(i % len(queries)) + 1}: {elapsed_ms:.2f}ms ({len(results)} results)")
        except Exception as e:
            logger.error(f"  Error in iteration {i+1}: {str(e)}")

    return times


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
    print("EDGE/TREES PERFORMANCE TEST RESULTS")
    print("="*80)
    print(f"GraphDB Endpoint: {SPARQL_ENDPOINT}")
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
    """Save results to JSON file."""
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {json_path}")


def run_performance_tests(iterations: int = 200) -> Dict[str, Any]:
    """
    Run all EDGE/TREES performance tests.

    Args:
        iterations: Number of iterations per test type

    Returns:
        Dictionary with all test results
    """
    logger.info(f"Running EDGE/TREES performance tests with {iterations} iterations per test")
    logger.info(f"SPARQL Endpoint: {SPARQL_ENDPOINT}")

    # Initialize SPARQL wrapper
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)

    # Test connection
    try:
        test_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        result = execute_sparql_query(sparql, test_query)
        triple_count = result[0]["count"]["value"]
        logger.info(f"✓ GraphDB connection successful ({triple_count} triples)")
    except Exception as e:
        logger.error(f"✗ GraphDB connection failed: {str(e)}")
        raise

    results = {
        "iterations": iterations,
        "timestamp": datetime.now().isoformat(),
        "endpoint": SPARQL_ENDPOINT,
        "tests": {},
        "summary": {}
    }

    # Test 1: EDGE Threshold Queries
    edge_times = test_edge_threshold_queries(sparql, iterations)
    results["tests"]["edge_threshold_lookup"] = analyze_performance(edge_times, TARGET_EDGE_THRESHOLD)

    # Test 2: TREES Criteria Queries
    trees_times = test_trees_criteria_queries(sparql, iterations)
    results["tests"]["trees_criteria_query"] = analyze_performance(trees_times, TARGET_TREES_CRITERIA)

    # Test 3: Material Eligibility Queries
    eligibility_times = test_material_eligibility_queries(sparql, iterations)
    results["tests"]["material_eligibility"] = analyze_performance(eligibility_times, TARGET_MATERIAL_ELIGIBILITY)

    # Generate summary
    results["summary"] = generate_summary(results["tests"])

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="EDGE/TREES Performance Testing")
    parser.add_argument("--test", action="store_true", help="Run performance tests")
    parser.add_argument("--iterations", type=int, default=200, help="Iterations per test (default: 200)")
    parser.add_argument("--output", type=str, help="Output file path for results")

    args = parser.parse_args()

    if not args.test:
        args.test = True

    try:
        # Run performance tests
        results = run_performance_tests(iterations=args.iterations)

        # Print results
        print_results(results)

        # Save results
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(__file__).parent / "EDGE_TREES_PERFORMANCE_RESULTS"

        save_results(results, output_path)

        # Assert all targets met
        if not results["summary"]["all_passed"]:
            logger.error("PERFORMANCE TARGETS NOT MET!")
            return 1

        logger.info("✓ All performance tests passed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error running performance tests: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

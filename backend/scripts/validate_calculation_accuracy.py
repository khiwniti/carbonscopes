"""
Validate calculation accuracy against manual consultant assessments.

This script compares automated carbon calculations against manual assessments
to achieve ≤2% error threshold (REQ-CALC-002).

Requires:
- 10+ BOQ files with manual consultant carbon assessments
- Manual assessment data in JSON format

Usage:
    python validate_calculation_accuracy.py [assessment_directory]

Example assessment JSON format:
{
    "boq_file": "project-abc.xlsx",
    "consultant": "John Smith",
    "assessment_date": "2026-03-15",
    "total_carbon_kgco2e": 12450.5,
    "methodology": "ISO 14040/14044",
    "materials": [
        {
            "description": "Concrete C30",
            "quantity": 100.0,
            "unit": "m³",
            "carbon_kgco2e": 44560.0
        }
    ]
}
"""

import sys
import logging
import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Optional

# Adjust import path if running as script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from carbonscope.backend.boq.carbon_pipeline import CarbonCalculationPipeline
from carbonscope.backend.lca.carbon_calculator import CarbonCalculator
from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_manual_assessments(assessment_dir: str) -> List[Dict]:
    """
    Load manual consultant assessments from JSON files.

    Args:
        assessment_dir: Directory containing JSON assessment files

    Returns:
        List of assessment dictionaries

    Format: Each JSON file should contain:
    {
        "boq_file": "project-abc.xlsx",
        "consultant": "Name",
        "assessment_date": "2026-03-15",
        "total_carbon_kgco2e": 12450.5,
        "methodology": "ISO 14040/14044",
        "materials": [...]
    }
    """
    assessment_path = Path(assessment_dir)

    if not assessment_path.exists():
        logger.error(f"Assessment directory not found: {assessment_dir}")
        return []

    assessments = []

    for json_file in assessment_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                assessment = json.load(f)
                assessments.append(assessment)
                logger.info(f"Loaded assessment from: {json_file.name}")
        except Exception as e:
            logger.error(f"Failed to load {json_file.name}: {e}")

    logger.info(f"Loaded {len(assessments)} manual assessments")
    return assessments


def validate_accuracy(
    boq_file: str,
    manual_total: Decimal,
    pipeline: CarbonCalculationPipeline
) -> Dict:
    """
    Compare automated vs manual calculation.

    Args:
        boq_file: Path to BOQ Excel file
        manual_total: Manual consultant total carbon (kgCO2e)
        pipeline: Carbon calculation pipeline

    Returns:
        Validation result with error percentage
    """
    try:
        # Run automated calculation
        result = pipeline.calculate_boq_carbon(boq_file)
        automated_total = Decimal(result["total_carbon"])

        # Calculate error
        error = abs(automated_total - manual_total)
        error_percent = (error / manual_total * 100) if manual_total > 0 else Decimal("0")

        validation_result = {
            "boq_file": boq_file,
            "automated": float(automated_total),
            "manual": float(manual_total),
            "error": float(error),
            "error_percent": float(error_percent),
            "pass": error_percent <= Decimal("2.0"),
            "status": "PASS" if error_percent <= Decimal("2.0") else "FAIL"
        }

        logger.info(
            f"Validation: {boq_file} - "
            f"Automated: {automated_total:.2f} kgCO2e, "
            f"Manual: {manual_total:.2f} kgCO2e, "
            f"Error: {error_percent:.2f}% - "
            f"{validation_result['status']}"
        )

        return validation_result

    except Exception as e:
        logger.error(f"Validation failed for {boq_file}: {e}")
        return {
            "boq_file": boq_file,
            "automated": None,
            "manual": float(manual_total),
            "error": None,
            "error_percent": None,
            "pass": False,
            "status": "ERROR",
            "error_message": str(e)
        }


def generate_report(results: List[Dict]) -> None:
    """
    Generate validation report.

    Args:
        results: List of validation results
    """
    print("\n" + "="*80)
    print("CALCULATION ACCURACY VALIDATION REPORT")
    print("="*80)

    if not results:
        print("No validation results to report.")
        return

    # Filter out errors for statistics
    valid_results = [r for r in results if r["error_percent"] is not None]

    if not valid_results:
        print("All validations resulted in errors.")
        return

    total_tests = len(valid_results)
    passed = sum(1 for r in valid_results if r["pass"])
    failed = total_tests - passed
    average_error = sum(r["error_percent"] for r in valid_results) / total_tests
    max_error = max(r["error_percent"] for r in valid_results)
    min_error = min(r["error_percent"] for r in valid_results)

    print(f"\nSummary:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed (≤2% error): {passed}")
    print(f"  Failed (>2% error): {failed}")
    print(f"  Pass rate: {passed / total_tests * 100:.2f}%")
    print(f"  Average error: {average_error:.2f}%")
    print(f"  Min error: {min_error:.2f}%")
    print(f"  Max error: {max_error:.2f}%")

    print(f"\nDetailed Results:")
    print("-" * 80)
    print(f"{'BOQ File':<40} {'Auto':<12} {'Manual':<12} {'Error %':<10} {'Status':<8}")
    print("-" * 80)

    for result in valid_results:
        boq_file = Path(result["boq_file"]).name
        print(
            f"{boq_file:<40} "
            f"{result['automated']:>11.2f} "
            f"{result['manual']:>11.2f} "
            f"{result['error_percent']:>9.2f} "
            f"{result['status']:<8}"
        )

    # Show errors if any
    error_results = [r for r in results if r["error_percent"] is None]
    if error_results:
        print(f"\nErrors ({len(error_results)}):")
        print("-" * 80)
        for result in error_results:
            boq_file = Path(result["boq_file"]).name
            error_msg = result.get("error_message", "Unknown error")
            print(f"{boq_file}: {error_msg}")

    print("="*80)


def main():
    """Run validation suite."""
    # Get assessment directory from command line or use default
    if len(sys.argv) > 1:
        assessment_dir = sys.argv[1]
    else:
        # Default: tests/fixtures/manual_assessments/
        assessment_dir = Path(__file__).parent.parent / "tests" / "fixtures" / "manual_assessments"

    logger.info(f"Using assessment directory: {assessment_dir}")

    # Load manual assessments
    assessments = load_manual_assessments(str(assessment_dir))

    if not assessments:
        logger.error("No assessments found. Exiting.")
        sys.exit(1)

    # Initialize pipeline
    try:
        # TODO: Get GraphDB endpoint from config/environment
        graphdb_endpoint = "http://localhost:7200/repositories/carbonbim-thailand"
        graphdb_client = GraphDBClient(graphdb_endpoint)
        carbon_calculator = CarbonCalculator(graphdb_client)
        pipeline = CarbonCalculationPipeline(graphdb_client, carbon_calculator)
        logger.info("Initialized carbon calculation pipeline")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)

    # Validate each assessment
    results = []
    for assessment in assessments:
        boq_file = assessment["boq_file"]
        manual_total = Decimal(str(assessment["total_carbon_kgco2e"]))

        # Resolve BOQ file path (assume same directory as JSON or provided path)
        boq_path = Path(assessment_dir) / boq_file
        if not boq_path.exists():
            logger.warning(f"BOQ file not found: {boq_path}")
            continue

        result = validate_accuracy(
            str(boq_path),
            manual_total,
            pipeline
        )
        results.append(result)

    # Generate report
    generate_report(results)

    # Exit with error if any test failed
    valid_results = [r for r in results if r["error_percent"] is not None]
    passed = sum(1 for r in valid_results if r["pass"])
    if passed < len(valid_results):
        sys.exit(1)


if __name__ == "__main__":
    main()

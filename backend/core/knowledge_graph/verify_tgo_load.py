#!/usr/bin/env python3
"""
Verify TGO Data Load in GraphDB

This script verifies that TGO emission factor data has been successfully loaded
into GraphDB and generates a comprehensive validation report.

Usage:
    python verify_tgo_load.py --version 2026-03
    python verify_tgo_load.py --all-versions
    python verify_tgo_load.py --version 2026-03 --output report.md

Requirements:
    - GraphDB running on localhost:7200
    - Repository: carbonbim-thailand
    - TGO data loaded in versioned named graphs
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from core.knowledge_graph.graphdb_client import GraphDBClient, GraphDBError
from core.knowledge_graph.versioning.version_manager import VersionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TGODataVerifier:
    """Verifies TGO emission factor data in GraphDB."""

    def __init__(self, graphdb_url: str = "http://localhost:7200/repositories/carbonbim-thailand"):
        """Initialize the verifier."""
        self.client = GraphDBClient(graphdb_url)
        self.version_manager = VersionManager(self.client)
        self.validation_results = {
            'total_materials': 0,
            'total_triples': 0,
            'categories': {},
            'data_quality_checks': {},
            'issues': [],
            'warnings': []
        }

    def verify_connection(self) -> bool:
        """Verify connection to GraphDB."""
        try:
            self.client.test_connection()
            logger.info("✓ GraphDB connection successful")
            return True
        except GraphDBError as e:
            logger.error(f"✗ GraphDB connection failed: {e}")
            return False

    def get_version_statistics(self, version_uri: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a version."""
        stats = {
            'version_uri': version_uri,
            'total_triples': 0,
            'total_materials': 0,
            'categories': {},
            'data_quality': {},
            'units': {},
            'lifecycle_stages': {},
            'geographic_scopes': {},
            'emission_factor_stats': {}
        }

        try:
            # Total triples
            stats['total_triples'] = self.client.get_triple_count(named_graph=version_uri)

            # Total materials
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT (COUNT(DISTINCT ?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:hasEmissionFactor ?ef .
                }}
            }}
            """
            result = self.client.query(query)
            stats['total_materials'] = int(result['results']['bindings'][0]['count']['value'])

            # Category breakdown
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?category (COUNT(?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:category ?category .
                }}
            }}
            GROUP BY ?category
            ORDER BY DESC(?count)
            """
            result = self.client.query(query)
            for binding in result['results']['bindings']:
                category = binding['category']['value']
                count = int(binding['count']['value'])
                stats['categories'][category] = count

            # Data quality breakdown
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?quality (COUNT(?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:dataQuality ?quality .
                }}
            }}
            GROUP BY ?quality
            ORDER BY DESC(?count)
            """
            result = self.client.query(query)
            for binding in result['results']['bindings']:
                quality = binding['quality']['value']
                count = int(binding['count']['value'])
                stats['data_quality'][quality] = count

            # Unit distribution
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?unit (COUNT(?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:hasUnit ?unit .
                }}
            }}
            GROUP BY ?unit
            ORDER BY DESC(?count)
            """
            result = self.client.query(query)
            for binding in result['results']['bindings']:
                unit = binding['unit']['value']
                count = int(binding['count']['value'])
                stats['units'][unit] = count

            # Lifecycle stage distribution
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?stage (COUNT(?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:lifecycleStage ?stage .
                }}
            }}
            GROUP BY ?stage
            ORDER BY DESC(?count)
            """
            result = self.client.query(query)
            for binding in result['results']['bindings']:
                stage = binding['stage']['value']
                count = int(binding['count']['value'])
                stats['lifecycle_stages'][stage] = count

            # Geographic scope distribution
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?scope (COUNT(?material) as ?count)
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material tgo:geographicScope ?scope .
                }}
            }}
            GROUP BY ?scope
            ORDER BY DESC(?count)
            """
            result = self.client.query(query)
            for binding in result['results']['bindings']:
                scope = binding['scope']['value']
                count = int(binding['count']['value'])
                stats['geographic_scopes'][scope] = count

            # Emission factor statistics (min, max, avg by category)
            for category in stats['categories'].keys():
                query = f"""
                PREFIX tgo: <http://tgo.or.th/ontology#>
                SELECT (MIN(?ef) as ?min) (MAX(?ef) as ?max) (AVG(?ef) as ?avg)
                WHERE {{
                    GRAPH <{version_uri}> {{
                        ?material tgo:category "{category}" ;
                                tgo:hasEmissionFactor ?ef .
                    }}
                }}
                """
                result = self.client.query(query)
                if result['results']['bindings']:
                    binding = result['results']['bindings'][0]
                    stats['emission_factor_stats'][category] = {
                        'min': float(binding['min']['value']),
                        'max': float(binding['max']['value']),
                        'avg': float(binding['avg']['value'])
                    }

        except GraphDBError as e:
            logger.error(f"Error getting version statistics: {e}")
            raise

        return stats

    def validate_data_quality(self, version_uri: str) -> Dict[str, Any]:
        """Validate data quality for a version."""
        issues = []
        warnings = []

        try:
            # Check for materials with missing Thai labels
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?material ?labelEN
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material rdfs:label ?labelEN .
                    FILTER(lang(?labelEN) = "en")
                    FILTER NOT EXISTS {{
                        ?material rdfs:label ?labelTH .
                        FILTER(lang(?labelTH) = "th")
                    }}
                }}
            }}
            LIMIT 10
            """
            result = self.client.query(query)
            if result['results']['bindings']:
                count = len(result['results']['bindings'])
                warnings.append(f"Found {count} materials with missing Thai labels")

            # Check for materials with zero or negative emission factors
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?material ?label ?ef
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material rdfs:label ?label ;
                            tgo:hasEmissionFactor ?ef .
                    FILTER(?ef <= 0)
                    FILTER(lang(?label) = "en" || lang(?label) = "")
                }}
            }}
            """
            result = self.client.query(query)
            if result['results']['bindings']:
                for binding in result['results']['bindings']:
                    issues.append(f"Invalid emission factor (≤0) for {binding['label']['value']}: {binding['ef']['value']}")

            # Check for suspiciously high emission factors (>20,000 kgCO2e)
            query = f"""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?material ?label ?ef ?category
            WHERE {{
                GRAPH <{version_uri}> {{
                    ?material rdfs:label ?label ;
                            tgo:hasEmissionFactor ?ef ;
                            tgo:category ?category .
                    FILTER(?ef > 20000)
                    FILTER(lang(?label) = "en" || lang(?label) = "")
                }}
            }}
            LIMIT 5
            """
            result = self.client.query(query)
            if result['results']['bindings']:
                for binding in result['results']['bindings']:
                    warnings.append(f"High emission factor for {binding['label']['value']} ({binding['category']['value']}): {binding['ef']['value']}")

            # Check for materials without required properties
            required_props = ['hasEmissionFactor', 'hasUnit', 'category', 'effectiveDate', 'sourceDocument']
            for prop in required_props:
                query = f"""
                PREFIX tgo: <http://tgo.or.th/ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT (COUNT(?material) as ?count)
                WHERE {{
                    GRAPH <{version_uri}> {{
                        ?material a ?type .
                        FILTER NOT EXISTS {{ ?material tgo:{prop} ?value }}
                    }}
                }}
                """
                result = self.client.query(query)
                count = int(result['results']['bindings'][0]['count']['value'])
                if count > 0:
                    issues.append(f"Found {count} materials missing tgo:{prop}")

        except GraphDBError as e:
            logger.error(f"Error validating data quality: {e}")
            raise

        return {
            'issues': issues,
            'warnings': warnings
        }

    def generate_report(self, stats: Dict[str, Any], validation: Dict[str, Any]) -> str:
        """Generate a comprehensive verification report."""
        report = []
        report.append("=" * 80)
        report.append("TGO DATA VERIFICATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Version: {stats['version_uri']}")
        report.append("")

        # Overall statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 80)
        report.append(f"  Total Materials: {stats['total_materials']}")
        report.append(f"  Total Triples:   {stats['total_triples']}")
        report.append(f"  Avg Triples/Material: {stats['total_triples'] / stats['total_materials']:.1f}")
        report.append("")

        # Category breakdown
        report.append("MATERIALS BY CATEGORY")
        report.append("-" * 80)
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_materials']) * 100
            bar = "█" * int(percentage / 2)
            report.append(f"  {category:20s}: {count:4d} materials ({percentage:5.1f}%) {bar}")
        report.append("")

        # Emission factor ranges by category
        report.append("EMISSION FACTOR RANGES BY CATEGORY")
        report.append("-" * 80)
        for category, ef_stats in sorted(stats['emission_factor_stats'].items()):
            report.append(f"  {category:20s}: {ef_stats['min']:8.1f} - {ef_stats['max']:10.1f} kgCO2e (avg: {ef_stats['avg']:8.1f})")
        report.append("")

        # Data quality breakdown
        if stats['data_quality']:
            report.append("DATA QUALITY DISTRIBUTION")
            report.append("-" * 80)
            for quality, count in sorted(stats['data_quality'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_materials']) * 100
                report.append(f"  {quality:20s}: {count:4d} materials ({percentage:5.1f}%)")
            report.append("")

        # Unit distribution
        if stats['units']:
            report.append("UNIT DISTRIBUTION")
            report.append("-" * 80)
            for unit, count in sorted(stats['units'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_materials']) * 100
                report.append(f"  {unit:20s}: {count:4d} materials ({percentage:5.1f}%)")
            report.append("")

        # Lifecycle stage distribution
        if stats['lifecycle_stages']:
            report.append("LIFECYCLE STAGE DISTRIBUTION")
            report.append("-" * 80)
            for stage, count in sorted(stats['lifecycle_stages'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_materials']) * 100
                report.append(f"  {stage:20s}: {count:4d} materials ({percentage:5.1f}%)")
            report.append("")

        # Geographic scope distribution
        if stats['geographic_scopes']:
            report.append("GEOGRAPHIC SCOPE DISTRIBUTION")
            report.append("-" * 80)
            for scope, count in sorted(stats['geographic_scopes'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_materials']) * 100
                report.append(f"  {scope:20s}: {count:4d} materials ({percentage:5.1f}%)")
            report.append("")

        # Validation results
        report.append("DATA QUALITY VALIDATION")
        report.append("-" * 80)
        if validation['issues']:
            report.append("ISSUES:")
            for i, issue in enumerate(validation['issues'], 1):
                report.append(f"  {i}. ❌ {issue}")
            report.append("")

        if validation['warnings']:
            report.append("WARNINGS:")
            for i, warning in enumerate(validation['warnings'][:10], 1):
                report.append(f"  {i}. ⚠️  {warning}")
            if len(validation['warnings']) > 10:
                report.append(f"  ... and {len(validation['warnings']) - 10} more warnings")
            report.append("")

        if not validation['issues'] and not validation['warnings']:
            report.append("  ✅ No issues or warnings found")
            report.append("")

        # Success criteria check
        report.append("SUCCESS CRITERIA")
        report.append("-" * 80)
        criteria = [
            ("Minimum 500 materials", stats['total_materials'] >= 500),
            ("All categories represented", len(stats['categories']) >= 9),
            ("No invalid emission factors", len([i for i in validation['issues'] if 'Invalid emission factor' in i]) == 0),
            ("All materials have required fields", len([i for i in validation['issues'] if 'missing' in i]) == 0),
            ("Data quality indicators present", len(stats['data_quality']) > 0),
        ]

        all_passed = True
        for criterion, passed in criteria:
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"  {criterion:50s}: {status}")
            if not passed:
                all_passed = False

        report.append("")
        report.append("=" * 80)

        if all_passed and not validation['issues']:
            report.append("STATUS: ✅ ALL CHECKS PASSED - DATA READY FOR PRODUCTION")
        elif validation['issues']:
            report.append("STATUS: ❌ ISSUES FOUND - REQUIRES ATTENTION")
        else:
            report.append("STATUS: ⚠️  WARNINGS PRESENT - REVIEW RECOMMENDED")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify TGO data load in GraphDB',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--version',
        type=str,
        default='2026-03',
        help='Version to verify (YYYY-MM format or full URI)'
    )

    parser.add_argument(
        '--graphdb-url',
        type=str,
        default='http://localhost:7200/repositories/carbonbim-thailand',
        help='GraphDB repository URL'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Path to save verification report'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output statistics as JSON'
    )

    args = parser.parse_args()

    # Initialize verifier
    try:
        verifier = TGODataVerifier(graphdb_url=args.graphdb_url)
        logger.info("TGO Data Verifier initialized")
    except Exception as e:
        logger.error(f"Failed to initialize verifier: {e}")
        sys.exit(1)

    # Verify connection
    if not verifier.verify_connection():
        sys.exit(1)

    # Normalize version URI
    version_uri = args.version
    if not version_uri.startswith('http://'):
        try:
            year, month = version_uri.split('-')
            version_uri = f"http://tgo.or.th/versions/{year}-{month}"
        except ValueError:
            logger.error(f"Invalid version format: {args.version}. Expected YYYY-MM or full URI")
            sys.exit(1)

    logger.info(f"Verifying version: {version_uri}")

    # Get statistics
    try:
        stats = verifier.get_version_statistics(version_uri)
        logger.info(f"Retrieved statistics for {stats['total_materials']} materials")
    except Exception as e:
        logger.error(f"Failed to get version statistics: {e}")
        sys.exit(1)

    # Validate data quality
    try:
        validation = verifier.validate_data_quality(version_uri)
        logger.info(f"Validation complete: {len(validation['issues'])} issues, {len(validation['warnings'])} warnings")
    except Exception as e:
        logger.error(f"Failed to validate data quality: {e}")
        sys.exit(1)

    # Generate report
    if args.json:
        output_data = {
            'statistics': stats,
            'validation': validation,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        output = json.dumps(output_data, indent=2)
    else:
        output = verifier.generate_report(stats, validation)

    # Display report
    print(output)

    # Save report if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"Report saved to {args.output}")

    # Exit with appropriate code
    if validation['issues']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

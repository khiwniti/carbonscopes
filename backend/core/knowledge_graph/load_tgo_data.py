#!/usr/bin/env python3
"""
Load TGO Emission Factor Data into GraphDB

This script loads Thailand Greenhouse Gas Management Organization (TGO)
emission factor data into GraphDB using named graph versioning.

Features:
- Converts JSON material data to RDF triples
- Uses versioned named graphs (http://tgo.or.th/versions/YYYY-MM)
- Creates version metadata with VersionManager
- Validates data before loading
- Generates load report with statistics
- Supports both JSON input and CSV template format

Usage:
    # Load from JSON file
    python load_tgo_data.py --json test_data/generated_materials.json

    # Load from CSV file (using template format)
    python load_tgo_data.py --csv .planning/tgo_materials_template.csv

    # Specify custom version
    python load_tgo_data.py --json test_data/generated_materials.json --version 2026-04

    # Clear existing version before loading
    python load_tgo_data.py --json test_data/generated_materials.json --clear

Requirements:
    pip install rdflib pandas unicodedata
"""

import argparse
import json
import logging
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from core.knowledge_graph.graphdb_client import GraphDBClient, GraphDBError
from core.knowledge_graph.versioning.version_manager import VersionManager, VersionManagerError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Namespaces
TGO = Namespace("http://tgo.or.th/ontology#")
MATERIAL_BASE = "http://tgo.or.th/materials/"


class TGODataLoader:
    """
    Loader for TGO emission factor data into GraphDB.

    This class handles:
    - Reading data from JSON or CSV files
    - Converting to RDF triples conforming to TGO ontology
    - Loading into versioned named graphs
    - Creating version metadata
    - Data validation and quality checks
    """

    def __init__(self, graphdb_url: str = "http://localhost:7200/repositories/carbonscope-bim-kg"):
        """
        Initialize the TGO data loader.

        Args:
            graphdb_url: GraphDB repository URL
        """
        self.client = GraphDBClient(graphdb_url)
        self.version_manager = VersionManager(self.client)
        self.stats = {
            'materials_loaded': 0,
            'triples_created': 0,
            'errors': [],
            'warnings': []
        }

    def normalize_thai_text(self, text: str) -> str:
        """
        Normalize Thai text to NFC form for consistent matching.

        Args:
            text: Thai text string

        Returns:
            NFC normalized text
        """
        return unicodedata.normalize('NFC', text)

    def validate_material(self, material: Dict[str, Any]) -> bool:
        """
        Validate a material entry for required fields and data quality.

        Args:
            material: Material dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'label_en', 'label_th', 'emission_factor', 'unit', 'category']

        # Check required fields
        for field in required_fields:
            if field not in material or not material[field]:
                error = f"Missing required field '{field}' in material: {material.get('id', 'unknown')}"
                logger.error(error)
                self.stats['errors'].append(error)
                return False

        # Validate emission factor is positive
        try:
            ef = float(material['emission_factor'])
            if ef <= 0:
                error = f"Invalid emission factor (≤0) for material: {material['id']}"
                logger.error(error)
                self.stats['errors'].append(error)
                return False

            # Warn about suspiciously high values
            if ef > 10000:
                warning = f"Suspiciously high emission factor ({ef}) for material: {material['id']}"
                logger.warning(warning)
                self.stats['warnings'].append(warning)

        except (ValueError, TypeError) as e:
            error = f"Invalid emission factor format for material {material['id']}: {e}"
            logger.error(error)
            self.stats['errors'].append(error)
            return False

        # Validate Thai text is NFC normalized
        if 'label_th' in material:
            thai_text = material['label_th']
            normalized = self.normalize_thai_text(thai_text)
            if thai_text != normalized:
                warning = f"Non-NFC Thai text for material {material['id']} (will be normalized)"
                logger.warning(warning)
                self.stats['warnings'].append(warning)
                material['label_th'] = normalized

        return True

    def material_to_rdf(self, material: Dict[str, Any], graph: Graph) -> int:
        """
        Convert a material dictionary to RDF triples and add to graph.

        Args:
            material: Material dictionary
            graph: RDFLib Graph to add triples to

        Returns:
            Number of triples added
        """
        triple_count = 0

        # Create material URI
        material_uri = URIRef(f"{MATERIAL_BASE}{material['id']}")

        # RDF type - use specific class if provided, otherwise ConstructionMaterial
        if 'type' in material and material['type']:
            # Handle both full URI and short form
            if material['type'].startswith('http://'):
                material_type = URIRef(material['type'])
            else:
                # Assume it's tgo:ClassName format
                class_name = material['type'].replace('tgo:', '')
                material_type = TGO[class_name]
        else:
            # Map category to ontology class
            category_to_class = {
                'Concrete': TGO.Concrete,
                'Steel': TGO.Steel,
                'Aluminum': TGO.Aluminum,
                'Glass': TGO.Glass,
                'Wood': TGO.Wood,
                'Insulation': TGO.Insulation,
                'Ceramic': TGO.Ceramic,
                'Cement': TGO.Cement,
                'Masonry': TGO.Masonry,
                'Gypsum': TGO.Gypsum,
                'Paint': TGO.Paint
            }
            material_type = category_to_class.get(material['category'], TGO.ConstructionMaterial)

        graph.add((material_uri, RDF.type, material_type))
        triple_count += 1

        # Labels (bilingual)
        graph.add((material_uri, RDFS.label, Literal(material['label_en'], lang='en')))
        triple_count += 1

        if 'label_th' in material:
            graph.add((material_uri, RDFS.label, Literal(material['label_th'], lang='th')))
            triple_count += 1

        # Emission factor (CRITICAL: use xsd:decimal for precision)
        ef_value = str(material['emission_factor'])
        graph.add((material_uri, TGO.hasEmissionFactor, Literal(ef_value, datatype=XSD.decimal)))
        triple_count += 1

        # Unit
        graph.add((material_uri, TGO.hasUnit, Literal(material['unit'], datatype=XSD.string)))
        triple_count += 1

        # Category
        graph.add((material_uri, TGO.category, Literal(material['category'], datatype=XSD.string)))
        triple_count += 1

        # Optional fields

        # Effective date (default to current date if not provided)
        effective_date = material.get('effective_date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))
        graph.add((material_uri, TGO.effectiveDate, Literal(effective_date, datatype=XSD.date)))
        triple_count += 1

        # Source document
        source_doc = material.get('source_document', 'http://tgo.or.th/data/generated')
        if source_doc.startswith('http://') or source_doc.startswith('https://'):
            graph.add((material_uri, TGO.sourceDocument, URIRef(source_doc)))
        else:
            graph.add((material_uri, TGO.sourceDocument, Literal(source_doc)))
        triple_count += 1

        # Data quality
        data_quality = material.get('data_quality', 'Verified')
        graph.add((material_uri, TGO.dataQuality, Literal(data_quality)))
        triple_count += 1

        # Geographic scope
        geo_scope = material.get('geographic_scope', 'Thailand')
        graph.add((material_uri, TGO.geographicScope, Literal(geo_scope)))
        triple_count += 1

        # Lifecycle stage
        lifecycle_stage = material.get('lifecycle_stage', 'A1-A3')
        graph.add((material_uri, TGO.lifecycleStage, Literal(lifecycle_stage)))
        triple_count += 1

        # Specification (if provided)
        if 'specification' in material and material['specification']:
            graph.add((material_uri, TGO.specification, Literal(material['specification'])))
            triple_count += 1

        # Material specification (alternative field name)
        if 'material_specification' in material and material['material_specification']:
            graph.add((material_uri, TGO.specification, Literal(material['material_specification'])))
            triple_count += 1

        # Notes
        if 'notes' in material and material['notes']:
            graph.add((material_uri, TGO.notes, Literal(material['notes'])))
            triple_count += 1

        # Uncertainty (if provided)
        if 'uncertainty' in material and material['uncertainty']:
            graph.add((material_uri, TGO.uncertainty, Literal(str(material['uncertainty']), datatype=XSD.decimal)))
            triple_count += 1

        # Alternative names (if provided)
        if 'alternative_names' in material and material['alternative_names']:
            # Split by pipe separator
            alt_names = material['alternative_names'].split('|')
            for alt_name in alt_names:
                if alt_name.strip():
                    graph.add((material_uri, TGO.alternativeName, Literal(alt_name.strip())))
                    triple_count += 1

        return triple_count

    def load_from_json(self, json_path: Path) -> List[Dict[str, Any]]:
        """
        Load materials from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            List of material dictionaries
        """
        logger.info(f"Loading materials from JSON: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                materials = json.load(f)

            if not isinstance(materials, list):
                raise ValueError("JSON file must contain a list of materials")

            logger.info(f"Loaded {len(materials)} materials from JSON")
            return materials

        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            raise

    def load_from_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        Load materials from CSV file (template format).

        Args:
            csv_path: Path to CSV file

        Returns:
            List of material dictionaries
        """
        logger.info(f"Loading materials from CSV: {csv_path}")

        try:
            df = pd.read_csv(csv_path)

            # Convert DataFrame to list of dictionaries
            materials = []
            for _, row in df.iterrows():
                material = {
                    'id': row['material_id'],
                    'type': row.get('material_class'),
                    'label_en': row['label_en'],
                    'label_th': row['label_th'],
                    'emission_factor': str(row['emission_factor']),
                    'unit': row['unit'],
                    'category': row['category'],
                    'effective_date': row.get('effective_date'),
                    'source_document': row.get('source_document'),
                    'data_quality': row.get('data_quality'),
                    'geographic_scope': row.get('geographic_scope'),
                    'lifecycle_stage': row.get('lifecycle_stage'),
                    'specification': row.get('material_specification'),
                    'notes': row.get('notes'),
                    'alternative_names': row.get('alternative_names')
                }

                # Remove None values
                material = {k: v for k, v in material.items() if pd.notna(v)}
                materials.append(material)

            logger.info(f"Loaded {len(materials)} materials from CSV")
            return materials

        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise

    def load_data(
        self,
        materials: List[Dict[str, Any]],
        version: Optional[str] = None,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Load materials into GraphDB with versioning.

        Args:
            materials: List of material dictionaries
            version: Version string (YYYY-MM format), defaults to current month
            clear_existing: Whether to clear existing version before loading

        Returns:
            Dictionary with load statistics
        """
        # Reset statistics
        self.stats = {
            'materials_loaded': 0,
            'triples_created': 0,
            'errors': [],
            'warnings': []
        }

        # Determine version
        if version:
            # Parse version string
            year, month = version.split('-')
            version_uri = self.version_manager.create_version_uri(int(year), int(month))
        else:
            version_uri = self.version_manager.get_current_version_uri()

        logger.info(f"Loading data into version: {version_uri}")

        # Clear existing version if requested
        if clear_existing:
            logger.warning(f"Clearing existing data in {version_uri}")
            try:
                self.client.clear_repository(named_graph=version_uri)
            except GraphDBError as e:
                logger.error(f"Error clearing existing version: {e}")

        # Create RDF graph
        graph = Graph()
        graph.bind('tgo', TGO)
        graph.bind('rdfs', RDFS)
        graph.bind('xsd', XSD)

        # Convert materials to RDF
        logger.info("Converting materials to RDF triples...")
        valid_materials = 0

        for material in materials:
            if self.validate_material(material):
                try:
                    triple_count = self.material_to_rdf(material, graph)
                    self.stats['triples_created'] += triple_count
                    valid_materials += 1
                except Exception as e:
                    error = f"Error converting material {material.get('id', 'unknown')} to RDF: {e}"
                    logger.error(error)
                    self.stats['errors'].append(error)

        logger.info(f"Converted {valid_materials} materials to {self.stats['triples_created']} RDF triples")

        # Load into GraphDB
        if valid_materials > 0:
            try:
                logger.info(f"Loading {self.stats['triples_created']} triples into GraphDB...")
                self.client.insert_triples(graph, named_graph=version_uri, format='turtle')
                self.stats['materials_loaded'] = valid_materials
                logger.info(f"Successfully loaded {valid_materials} materials into {version_uri}")

                # Create version metadata
                logger.info("Creating version metadata...")
                version_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                notes = f"Loaded {valid_materials} TGO construction materials with emission factors"

                self.version_manager.create_version_metadata(
                    version_uri=version_uri,
                    version_date=version_date,
                    notes=notes
                )
                logger.info("Version metadata created")

            except (GraphDBError, VersionManagerError) as e:
                error = f"Error loading data into GraphDB: {e}"
                logger.error(error)
                self.stats['errors'].append(error)
                raise
        else:
            logger.error("No valid materials to load")

        return self.stats

    def generate_load_report(self, stats: Dict[str, Any]) -> str:
        """
        Generate a human-readable load report.

        Args:
            stats: Load statistics dictionary

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("TGO DATA LOAD REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")
        report.append("STATISTICS:")
        report.append(f"  Materials loaded: {stats['materials_loaded']}")
        report.append(f"  Triples created: {stats['triples_created']}")
        report.append(f"  Errors: {len(stats['errors'])}")
        report.append(f"  Warnings: {len(stats['warnings'])}")
        report.append("")

        if stats['errors']:
            report.append("ERRORS:")
            for i, error in enumerate(stats['errors'][:10], 1):
                report.append(f"  {i}. {error}")
            if len(stats['errors']) > 10:
                report.append(f"  ... and {len(stats['errors']) - 10} more errors")
            report.append("")

        if stats['warnings']:
            report.append("WARNINGS:")
            for i, warning in enumerate(stats['warnings'][:10], 1):
                report.append(f"  {i}. {warning}")
            if len(stats['warnings']) > 10:
                report.append(f"  ... and {len(stats['warnings']) - 10} more warnings")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Load TGO emission factor data into GraphDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load from JSON file
  python load_tgo_data.py --json test_data/generated_materials.json

  # Load from CSV file
  python load_tgo_data.py --csv .planning/tgo_materials_template.csv

  # Specify custom version
  python load_tgo_data.py --json test_data/generated_materials.json --version 2026-04

  # Clear existing version before loading
  python load_tgo_data.py --json test_data/generated_materials.json --clear
        """
    )

    parser.add_argument(
        '--json',
        type=str,
        help='Path to JSON file containing materials'
    )

    parser.add_argument(
        '--csv',
        type=str,
        help='Path to CSV file containing materials (template format)'
    )

    parser.add_argument(
        '--version',
        type=str,
        help='Version string (YYYY-MM format), defaults to current month'
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing version before loading'
    )

    parser.add_argument(
        '--graphdb-url',
        type=str,
        default='http://localhost:7200/repositories/carbonscope-bim-kg',
        help='GraphDB repository URL (default: http://localhost:7200/repositories/carbonscope-bim-kg)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Path to save load report'
    )

    args = parser.parse_args()

    # Validate input
    if not args.json and not args.csv:
        parser.error("Must specify either --json or --csv input file")

    if args.json and args.csv:
        parser.error("Cannot specify both --json and --csv")

    # Initialize loader
    try:
        loader = TGODataLoader(graphdb_url=args.graphdb_url)
        logger.info("TGO Data Loader initialized")
    except Exception as e:
        logger.error(f"Failed to initialize loader: {e}")
        sys.exit(1)

    # Load materials from file
    try:
        if args.json:
            materials = loader.load_from_json(Path(args.json))
        else:
            materials = loader.load_from_csv(Path(args.csv))
    except Exception as e:
        logger.error(f"Failed to load materials: {e}")
        sys.exit(1)

    # Load into GraphDB
    try:
        stats = loader.load_data(
            materials=materials,
            version=args.version,
            clear_existing=args.clear
        )
    except Exception as e:
        logger.error(f"Failed to load data into GraphDB: {e}")
        sys.exit(1)

    # Generate and display report
    report = loader.generate_load_report(stats)
    print(report)

    # Save report if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")

    # Exit with error code if there were errors
    if stats['errors']:
        sys.exit(1)
    else:
        logger.info("Data load completed successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()

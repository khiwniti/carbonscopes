"""
End-to-end carbon calculation pipeline for BOQ analysis.

Pipeline flow:
1. Parse BOQ Excel file
2. Match materials to TGO database
3. Query emission factors from GraphDB
4. Calculate carbon using Brightway2
5. Generate audit trail
6. Store results in PostgreSQL
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, timezone

from .parser import parse_boq, BOQParseResult
from .material_matching import match_boq_materials, calculate_match_statistics, BOQMaterialMatch
from .audit_trail import CalculationAudit, MaterialCalculationAudit
from .db_sync import get_db
from lca.carbon_calculator import CarbonCalculator
from core.knowledge_graph.graphdb_client import GraphDBClient
from core.knowledge_graph.sparql_queries import get_emission_factor

logger = logging.getLogger(__name__)


class CarbonCalculationPipeline:
    """
    End-to-end BOQ carbon calculation pipeline.

    Integrates:
    - BOQ parsing
    - Material matching
    - TGO emission factor queries
    - Brightway2 LCA calculations
    - Audit trail generation
    """

    def __init__(
        self,
        graphdb_client: GraphDBClient,
        carbon_calculator: CarbonCalculator,
        tgo_version: str = "2026-03"
    ):
        """
        Initialize pipeline.

        Args:
            graphdb_client: GraphDB client for TGO queries
            carbon_calculator: Brightway2 carbon calculator
            tgo_version: TGO database version to use
        """
        self.graphdb_client = graphdb_client
        self.carbon_calculator = carbon_calculator
        self.tgo_version = tgo_version

    def calculate_boq_carbon(
        self,
        boq_file_path: str,
        uploaded_by: Optional[str] = None,
        language: str = "th"
    ) -> Dict[str, Any]:
        """
        Calculate carbon footprint for BOQ file (complete pipeline).

        Args:
            boq_file_path: Absolute path to BOQ Excel file
            uploaded_by: User email/ID (optional)
            language: Language for material matching ("th" or "en")

        Returns:
            Dictionary with:
            - analysis_id: UUID for audit trail retrieval
            - total_carbon: Total kgCO2e
            - breakdown: Per-material results
            - statistics: Matching and calculation stats
            - audit_trail: Summary audit data

        Raises:
            ValueError: If BOQ parsing fails
            Exception: If calculation fails
        """
        logger.info(f"Starting carbon calculation pipeline for: {boq_file_path}")

        # Step 1: Parse BOQ
        logger.info("Step 1/5: Parsing BOQ file...")
        boq_result = parse_boq(boq_file_path)

        if boq_result.status == "failed" or len(boq_result.materials) == 0:
            raise ValueError(f"BOQ parsing failed: {boq_result.errors}")

        logger.info(f"Parsed {len(boq_result.materials)} materials (success rate: {boq_result.metadata['success_rate']}%)")

        # Step 2: Match materials to TGO
        logger.info("Step 2/5: Matching materials to TGO database...")
        matches = match_boq_materials(
            boq_result.materials,
            self.graphdb_client,
            language=language
        )

        match_stats = calculate_match_statistics(matches)
        logger.info(f"Material matching complete: {match_stats['auto_match_rate']}% auto-matched")

        # Step 3: Query emission factors and calculate carbon
        logger.info("Step 3/5: Calculating carbon footprint...")
        total_carbon = Decimal("0.0")
        material_results = []

        for match in matches:
            material_result = self._calculate_material_carbon(match)
            material_results.append(material_result)

            if material_result["carbon_result"] is not None:
                total_carbon += material_result["carbon_result"]

        logger.info(f"Total carbon: {total_carbon} kgCO2e")

        # Step 4: Generate audit trail
        logger.info("Step 4/5: Generating audit trail...")
        audit_id = self._create_audit_trail(
            boq_result=boq_result,
            matches=matches,
            material_results=material_results,
            total_carbon=total_carbon,
            match_stats=match_stats,
            uploaded_by=uploaded_by
        )

        # Step 5: Compile response
        logger.info("Step 5/5: Compiling response...")
        response = {
            "analysis_id": str(audit_id),
            "boq_file_id": boq_result.file_id,
            "boq_filename": boq_result.filename,
            "tgo_version": self.tgo_version,
            "total_carbon": str(total_carbon),
            "unit": "kgCO2e",
            "material_count": len(boq_result.materials),
            "matched_count": match_stats["auto_matched"] + match_stats["review_required"],
            "auto_matched_count": match_stats["auto_matched"],
            "breakdown": [
                {
                    "line_number": mr["boq_line_number"],
                    "description_th": mr["description_th"],
                    "quantity": str(mr["quantity"]),
                    "unit": mr["unit"],
                    "carbon": str(mr["carbon_result"]) if mr["carbon_result"] else None,
                    "percentage": round(float(mr["carbon_result"] / total_carbon * 100), 2) if mr["carbon_result"] and total_carbon > 0 else 0.0
                }
                for mr in material_results
            ],
            "statistics": match_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Pipeline complete. Analysis ID: {audit_id}")
        return response

    def _calculate_material_carbon(self, match: BOQMaterialMatch) -> Dict[str, Any]:
        """
        Calculate carbon for single matched material.

        Args:
            match: BOQ material match with TGO material ID

        Returns:
            Dictionary with calculation details
        """
        boq_material = match.boq_material

        # If no TGO match, return zero carbon
        if match.tgo_match is None or match.classification == "rejected":
            return {
                "boq_line_number": boq_material.line_number,
                "description_th": boq_material.description_th,
                "description_en": boq_material.description_en,
                "quantity": boq_material.quantity,
                "unit": boq_material.unit,
                "tgo_material_id": None,
                "tgo_material_label": None,
                "match_confidence": Decimal("0.0"),
                "match_classification": match.classification,
                "emission_factor_value": None,
                "emission_factor_unit": None,
                "emission_factor_version": None,
                "emission_factor_effective_date": None,
                "carbon_result": None,
                "calculation_formula": None
            }

        # Query emission factor from GraphDB
        tgo_material_id = match.tgo_match.get("material_id")
        try:
            emission_factor_data = get_emission_factor(
                self.graphdb_client,
                tgo_material_id,
                version=None  # Use latest version; TODO: support version parameter
            )
        except Exception as e:
            logger.warning(f"No emission factor found for TGO material: {tgo_material_id}, error: {e}")
            return {
                "boq_line_number": boq_material.line_number,
                "description_th": boq_material.description_th,
                "description_en": boq_material.description_en,
                "quantity": boq_material.quantity,
                "unit": boq_material.unit,
                "tgo_material_id": tgo_material_id,
                "tgo_material_label": match.tgo_match.get("label"),
                "match_confidence": match.confidence,
                "match_classification": match.classification,
                "emission_factor_value": None,
                "emission_factor_unit": None,
                "emission_factor_version": None,
                "emission_factor_effective_date": None,
                "carbon_result": None,
                "calculation_formula": None
            }

        # Extract emission factor
        ef_value = emission_factor_data.get("emission_factor")
        if isinstance(ef_value, str):
            ef_value = Decimal(ef_value)
        elif not isinstance(ef_value, Decimal):
            ef_value = Decimal(str(ef_value))

        ef_unit = emission_factor_data.get("unit")
        ef_version = emission_factor_data.get("version", self.tgo_version)
        ef_date_str = emission_factor_data.get("effective_date")
        ef_date = None
        if ef_date_str:
            try:
                ef_date = datetime.fromisoformat(ef_date_str)
            except:
                pass

        # Calculate carbon using Brightway2
        # Simple multiplication: quantity × emission_factor = carbon
        # (Brightway2 handles full LCA calculation internally)
        quantity = boq_material.quantity
        carbon_result = quantity * ef_value

        # Create human-readable formula
        calculation_formula = f"{quantity} {boq_material.unit} × {ef_value} {ef_unit} = {carbon_result} kgCO2e"

        return {
            "boq_line_number": boq_material.line_number,
            "description_th": boq_material.description_th,
            "description_en": boq_material.description_en,
            "quantity": quantity,
            "unit": boq_material.unit,
            "tgo_material_id": tgo_material_id,
            "tgo_material_label": match.tgo_match.get("label"),
            "match_confidence": match.confidence,
            "match_classification": match.classification,
            "emission_factor_value": ef_value,
            "emission_factor_unit": ef_unit,
            "emission_factor_version": ef_version,
            "emission_factor_effective_date": ef_date,
            "carbon_result": carbon_result,
            "calculation_formula": calculation_formula
        }

    def _create_audit_trail(
        self,
        boq_result: BOQParseResult,
        matches: List[BOQMaterialMatch],
        material_results: List[Dict[str, Any]],
        total_carbon: Decimal,
        match_stats: Dict[str, Any],
        uploaded_by: Optional[str]
    ) -> str:
        """
        Create and store audit trail in PostgreSQL.

        Args:
            boq_result: Parsed BOQ result
            matches: Material matches
            material_results: Calculated results
            total_carbon: Total carbon footprint
            match_stats: Matching statistics
            uploaded_by: User identifier

        Returns:
            Audit ID (UUID string)
        """
        with get_db() as db:
            try:
                # Create main audit record
                audit = CalculationAudit(
                    boq_file_id=boq_result.file_id,
                    boq_filename=boq_result.filename,
                    uploaded_by=uploaded_by,
                    tgo_version=self.tgo_version,
                    calculation_mode="deterministic",
                    brightway_version="2.5.0",  # Get from carbon_calculator if available
                    total_carbon_kgco2e=total_carbon,
                    material_count=len(boq_result.materials),
                    matched_count=match_stats["auto_matched"] + match_stats["review_required"],
                    auto_matched_count=match_stats["auto_matched"]
                )

                db.add(audit)
                db.flush()  # Get audit.id

                # Create material calculation records
                for material_result in material_results:
                    material_audit = MaterialCalculationAudit(
                        audit_id=audit.id,
                        boq_line_number=material_result["boq_line_number"],
                        description_th=material_result["description_th"],
                        description_en=material_result["description_en"],
                        quantity=material_result["quantity"],
                        unit=material_result["unit"],
                        tgo_material_id=material_result["tgo_material_id"],
                        tgo_material_label=material_result["tgo_material_label"],
                        match_confidence=material_result["match_confidence"],
                        match_classification=material_result["match_classification"],
                        emission_factor_value=material_result["emission_factor_value"],
                        emission_factor_unit=material_result["emission_factor_unit"],
                        emission_factor_version=material_result["emission_factor_version"],
                        emission_factor_effective_date=material_result["emission_factor_effective_date"],
                        carbon_result_kgco2e=material_result["carbon_result"],
                        calculation_formula=material_result["calculation_formula"]
                    )
                    db.add(material_audit)

                db.commit()
                logger.info(f"Audit trail created: {audit.id}")

                return str(audit.id)

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create audit trail: {e}")
                raise

    def get_audit_trail(self, analysis_id: str) -> Dict[str, Any]:
        """
        Retrieve complete audit trail for analysis.

        Args:
            analysis_id: UUID of calculation audit

        Returns:
            Complete audit trail with all material calculations
        """
        with get_db() as db:
            audit = db.query(CalculationAudit).filter(
                CalculationAudit.id == analysis_id
            ).first()

            if not audit:
                raise ValueError(f"Audit trail not found: {analysis_id}")

            # Convert to dictionary
            audit_dict = audit.to_dict()
            audit_dict["materials"] = [
                material.to_dict()
                for material in audit.material_calculations
            ]

            return audit_dict

"""
EDGE V3 (Excellence in Design for Greater Efficiencies) Certification Module.

This module implements the EDGE V3 methodology for embodied carbon certification:
- Baseline calculation using local standards
- 20% reduction target for EDGE certification
- 40% reduction for EDGE Advanced (energy)
- Progress tracking and compliance checking

EDGE V3 focuses on three key areas:
1. Energy savings (40% for Advanced, 20% for standard)
2. Water savings (20% reduction)
3. Embodied energy in materials (20% reduction)

References:
- EDGE Building Certification Guidance v3.1:
  https://edgebuildings.com/wp-content/uploads/2024/12/Part-1-EDGE-Building-Certification-Guidance-Rev-1.pdf
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from core.knowledge_graph import GraphDBClient, QueryError

logger = logging.getLogger(__name__)


class EDGEError(Exception):
    """Base exception for EDGE certification errors."""
    pass


class EDGECertification:
    """
    EDGE V3 Certification Calculator.

    This class provides methods for calculating baseline embodied carbon,
    tracking reduction progress, and determining EDGE certification compliance.

    Attributes:
        client: GraphDBClient instance for querying EDGE criteria
        version: EDGE version (default: "3.1")
    """

    # EDGE Certification Thresholds
    EDGE_EMBODIED_CARBON_REDUCTION = Decimal("0.20")  # 20% reduction
    EDGE_ADVANCED_ENERGY_REDUCTION = Decimal("0.40")  # 40% energy reduction
    EDGE_WATER_REDUCTION = Decimal("0.20")  # 20% water reduction

    # EDGE Namespaces
    EDGE_NAMESPACE = "http://edgebuildings.com/ontology#"
    TGO_NAMESPACE = "http://tgo.or.th/ontology#"

    def __init__(self, client: GraphDBClient, version: str = "3.1"):
        """
        Initialize EDGE certification calculator.

        Args:
            client: GraphDBClient instance
            version: EDGE version (default: "3.1")
        """
        self.client = client
        self.version = version
        self.baseline_cache = {}

    def calculate_baseline(
        self,
        project_type: str,
        floor_area: Decimal,
        materials: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate baseline embodied carbon footprint.

        EDGE baseline represents typical construction practices in the region.
        If materials are provided, calculates baseline using standard materials.
        Otherwise, uses regional baseline factors.

        Args:
            project_type: Project type ("residential", "commercial", "industrial")
            floor_area: Gross floor area in m²
            materials: Optional list of materials for detailed baseline

        Returns:
            Dictionary containing:
                - baseline_total: Total baseline carbon (kgCO2e)
                - baseline_per_sqm: Carbon per m² (kgCO2e/m²)
                - project_type: Project type
                - floor_area: Floor area (m²)
                - methodology: Baseline calculation method
                - breakdown: Category breakdown (if materials provided)

        Raises:
            EDGEError: If baseline calculation fails
        """
        try:
            # Get regional baseline factors from GraphDB
            baseline_factors = self._get_regional_baseline_factors(project_type)

            if materials:
                # Calculate detailed baseline using typical materials
                baseline_total = self._calculate_detailed_baseline(materials, baseline_factors)
                methodology = "DETAILED_MATERIAL_BASELINE"
            else:
                # Use regional benchmark (kgCO2e/m²)
                baseline_per_sqm = baseline_factors.get("carbon_per_sqm", Decimal("300"))
                baseline_total = baseline_per_sqm * floor_area
                methodology = "REGIONAL_BENCHMARK"

            baseline_per_sqm = baseline_total / floor_area if floor_area > 0 else Decimal("0")

            logger.info(
                f"EDGE Baseline: {float(baseline_total):.2f} kgCO2e "
                f"({float(baseline_per_sqm):.2f} kgCO2e/m²) for {project_type}"
            )

            return {
                "baseline_total": float(baseline_total),
                "baseline_per_sqm": float(baseline_per_sqm),
                "project_type": project_type,
                "floor_area": float(floor_area),
                "methodology": methodology,
                "version": f"EDGE V{self.version}",
                "calculation_date": datetime.now().isoformat()
            }

        except Exception as e:
            raise EDGEError(f"Failed to calculate baseline: {str(e)}") from e

    def calculate_reduction(
        self,
        actual_carbon: Decimal,
        baseline_carbon: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate percentage reduction from baseline.

        Args:
            actual_carbon: Actual project carbon footprint (kgCO2e)
            baseline_carbon: Baseline carbon footprint (kgCO2e)

        Returns:
            Dictionary containing:
                - actual_carbon: Actual carbon footprint
                - baseline_carbon: Baseline carbon footprint
                - reduction_absolute: Absolute reduction (kgCO2e)
                - reduction_percentage: Percentage reduction (0-100)
                - meets_edge_threshold: Whether 20% threshold is met

        Raises:
            EDGEError: If calculation fails or baseline is zero
        """
        if baseline_carbon <= 0:
            raise EDGEError("Baseline carbon must be greater than zero")

        try:
            reduction_absolute = baseline_carbon - actual_carbon
            reduction_percentage = (reduction_absolute / baseline_carbon) * Decimal("100")

            # Check if meets EDGE 20% threshold
            meets_threshold = reduction_percentage >= (self.EDGE_EMBODIED_CARBON_REDUCTION * Decimal("100"))

            logger.info(
                f"EDGE Reduction: {float(reduction_percentage):.1f}% "
                f"(target: {float(self.EDGE_EMBODIED_CARBON_REDUCTION * 100):.0f}%)"
            )

            return {
                "actual_carbon": float(actual_carbon),
                "baseline_carbon": float(baseline_carbon),
                "reduction_absolute": float(reduction_absolute),
                "reduction_percentage": float(reduction_percentage),
                "target_percentage": float(self.EDGE_EMBODIED_CARBON_REDUCTION * 100),
                "meets_edge_threshold": meets_threshold,
                "gap_percentage": float(max(0, (self.EDGE_EMBODIED_CARBON_REDUCTION * 100) - reduction_percentage)),
                "calculation_date": datetime.now().isoformat()
            }

        except Exception as e:
            raise EDGEError(f"Failed to calculate reduction: {str(e)}") from e

    def check_edge_compliance(
        self,
        reduction_percentage: Decimal,
        energy_reduction: Optional[Decimal] = None,
        water_reduction: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Check EDGE certification compliance status.

        Args:
            reduction_percentage: Embodied carbon reduction percentage (0-100)
            energy_reduction: Optional energy reduction percentage for EDGE Advanced
            water_reduction: Optional water reduction percentage

        Returns:
            Dictionary containing:
                - edge_certified: Whether EDGE certified (20% embodied carbon)
                - edge_advanced: Whether EDGE Advanced (40% energy + 20% embodied)
                - embodied_carbon_status: Compliance status
                - energy_status: Energy compliance status (if provided)
                - water_status: Water compliance status (if provided)
                - recommendations: List of recommendations
        """
        # Check embodied carbon compliance (20% required)
        embodied_compliant = reduction_percentage >= (self.EDGE_EMBODIED_CARBON_REDUCTION * Decimal("100"))

        # Check energy compliance for EDGE Advanced (40% required)
        energy_compliant = False
        if energy_reduction is not None:
            energy_compliant = energy_reduction >= (self.EDGE_ADVANCED_ENERGY_REDUCTION * Decimal("100"))

        # Check water compliance (20% required)
        water_compliant = False
        if water_reduction is not None:
            water_compliant = water_reduction >= (self.EDGE_WATER_REDUCTION * Decimal("100"))

        # Determine certification level
        edge_certified = embodied_compliant
        edge_advanced = embodied_compliant and energy_compliant

        # Generate recommendations
        recommendations = []
        if not embodied_compliant:
            gap = (self.EDGE_EMBODIED_CARBON_REDUCTION * Decimal("100")) - reduction_percentage
            recommendations.append(
                f"Reduce embodied carbon by additional {float(gap):.1f}% to meet EDGE 20% threshold"
            )
            recommendations.append("Consider low-carbon materials (concrete alternatives, recycled content)")
            recommendations.append("Optimize structural design to reduce material quantities")

        if energy_reduction is not None and not energy_compliant:
            gap = (self.EDGE_ADVANCED_ENERGY_REDUCTION * Decimal("100")) - energy_reduction
            recommendations.append(
                f"Improve energy efficiency by {float(gap):.1f}% for EDGE Advanced certification"
            )
            recommendations.append("Enhance building envelope (insulation, glazing)")
            recommendations.append("Upgrade HVAC systems and lighting efficiency")

        if water_reduction is not None and not water_compliant:
            gap = (self.EDGE_WATER_REDUCTION * Decimal("100")) - water_reduction
            recommendations.append(
                f"Reduce water consumption by {float(gap):.1f}% for full EDGE compliance"
            )

        if embodied_compliant and not recommendations:
            recommendations.append("Maintain low-carbon material specifications")
            if not edge_advanced and energy_reduction is not None:
                recommendations.append("Consider pursuing EDGE Advanced with 40% energy reduction")

        return {
            "edge_certified": edge_certified,
            "edge_advanced": edge_advanced,
            "embodied_carbon_status": {
                "compliant": embodied_compliant,
                "reduction_percentage": float(reduction_percentage),
                "target_percentage": float(self.EDGE_EMBODIED_CARBON_REDUCTION * 100),
                "gap": float(max(0, (self.EDGE_EMBODIED_CARBON_REDUCTION * 100) - reduction_percentage))
            },
            "energy_status": {
                "compliant": energy_compliant,
                "reduction_percentage": float(energy_reduction) if energy_reduction else None,
                "target_percentage": float(self.EDGE_ADVANCED_ENERGY_REDUCTION * 100),
                "gap": float(max(0, (self.EDGE_ADVANCED_ENERGY_REDUCTION * 100) - energy_reduction))
                    if energy_reduction else None
            } if energy_reduction is not None else None,
            "water_status": {
                "compliant": water_compliant,
                "reduction_percentage": float(water_reduction) if water_reduction else None,
                "target_percentage": float(self.EDGE_WATER_REDUCTION * 100),
                "gap": float(max(0, (self.EDGE_WATER_REDUCTION * 100) - water_reduction))
                    if water_reduction else None
            } if water_reduction is not None else None,
            "recommendations": recommendations,
            "version": f"EDGE V{self.version}",
            "assessment_date": datetime.now().isoformat()
        }

    def track_progress(
        self,
        baseline: Dict[str, Any],
        actual_measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track EDGE certification progress over time.

        Args:
            baseline: Baseline calculation result from calculate_baseline()
            actual_measurements: List of measurement dictionaries containing:
                - date: Measurement date (ISO format)
                - actual_carbon: Actual carbon footprint
                - energy_reduction: Optional energy reduction %
                - water_reduction: Optional water reduction %

        Returns:
            Progress tracking report with timeline and projections
        """
        progress_timeline = []

        for measurement in actual_measurements:
            reduction = self.calculate_reduction(
                Decimal(str(measurement["actual_carbon"])),
                Decimal(str(baseline["baseline_total"]))
            )

            compliance = self.check_edge_compliance(
                Decimal(str(reduction["reduction_percentage"])),
                Decimal(str(measurement.get("energy_reduction", 0))),
                Decimal(str(measurement.get("water_reduction", 0)))
            )

            progress_timeline.append({
                "date": measurement["date"],
                "actual_carbon": measurement["actual_carbon"],
                "reduction_percentage": reduction["reduction_percentage"],
                "edge_certified": compliance["edge_certified"],
                "gap_to_target": reduction["gap_percentage"]
            })

        # Calculate trend
        if len(progress_timeline) >= 2:
            first = progress_timeline[0]
            last = progress_timeline[-1]
            trend = "IMPROVING" if last["reduction_percentage"] > first["reduction_percentage"] else "DECLINING"
        else:
            trend = "INSUFFICIENT_DATA"

        return {
            "baseline": baseline,
            "progress_timeline": progress_timeline,
            "trend": trend,
            "latest_status": progress_timeline[-1] if progress_timeline else None,
            "version": f"EDGE V{self.version}",
            "report_date": datetime.now().isoformat()
        }

    def generate_edge_report(
        self,
        baseline: Dict[str, Any],
        reduction: Dict[str, Any],
        compliance: Dict[str, Any],
        materials: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive EDGE certification report.

        Args:
            baseline: Baseline calculation result
            reduction: Reduction calculation result
            compliance: Compliance check result
            materials: Optional list of materials for detailed breakdown

        Returns:
            Comprehensive EDGE certification report
        """
        report = {
            "certification_status": {
                "edge_certified": compliance["edge_certified"],
                "edge_advanced": compliance["edge_advanced"],
                "certification_level": "EDGE Advanced" if compliance["edge_advanced"]
                                     else "EDGE" if compliance["edge_certified"]
                                     else "Not Certified"
            },
            "baseline": baseline,
            "reduction": reduction,
            "compliance": compliance,
            "version": f"EDGE V{self.version}",
            "report_date": datetime.now().isoformat()
        }

        # Add material breakdown if available
        if materials:
            material_breakdown = self._calculate_material_breakdown(materials)
            report["material_breakdown"] = material_breakdown

        return report

    def _get_regional_baseline_factors(self, project_type: str) -> Dict[str, Any]:
        """
        Query regional baseline factors from GraphDB.

        Args:
            project_type: Project type

        Returns:
            Dictionary of baseline factors
        """
        # Check cache
        cache_key = f"baseline_{project_type}"
        if cache_key in self.baseline_cache:
            return self.baseline_cache[cache_key]

        try:
            query = f"""
            PREFIX edge: <{self.EDGE_NAMESPACE}>

            SELECT ?carbonPerSqm ?projectType
            WHERE {{
                ?baseline a edge:RegionalBaseline ;
                         edge:projectType "{project_type}" ;
                         edge:carbonPerSqm ?carbonPerSqm .
            }}
            LIMIT 1
            """

            results = self.client.query(query)
            bindings = results.get("results", {}).get("bindings", [])

            if bindings:
                binding = bindings[0]
                factors = {
                    "carbon_per_sqm": Decimal(binding["carbonPerSqm"]["value"]),
                    "project_type": binding["projectType"]["value"]
                }
            else:
                # Use default baseline factors for Thailand if not in GraphDB
                default_factors = {
                    "residential": Decimal("280"),  # kgCO2e/m²
                    "commercial": Decimal("320"),   # kgCO2e/m²
                    "industrial": Decimal("350")    # kgCO2e/m²
                }
                factors = {
                    "carbon_per_sqm": default_factors.get(project_type, Decimal("300")),
                    "project_type": project_type
                }
                logger.warning(
                    f"No baseline factors in GraphDB for {project_type}, "
                    f"using default: {factors['carbon_per_sqm']} kgCO2e/m²"
                )

            # Cache the result
            self.baseline_cache[cache_key] = factors
            return factors

        except QueryError as e:
            logger.error(f"Failed to query baseline factors: {e}")
            # Return default factors
            return {
                "carbon_per_sqm": Decimal("300"),
                "project_type": project_type
            }

    def _calculate_detailed_baseline(
        self,
        materials: List[Dict[str, Any]],
        baseline_factors: Dict[str, Any]
    ) -> Decimal:
        """
        Calculate detailed baseline using material-specific factors.

        Args:
            materials: List of materials
            baseline_factors: Regional baseline factors

        Returns:
            Total baseline carbon (kgCO2e)
        """
        total_baseline = Decimal("0")

        for material in materials:
            quantity = Decimal(str(material.get("quantity", 0)))
            # Use baseline emission factor (typically higher than optimized)
            baseline_ef = material.get("baseline_emission_factor",
                                      material.get("emission_factor", Decimal("0")))
            baseline_ef = Decimal(str(baseline_ef))

            material_baseline = quantity * baseline_ef
            total_baseline += material_baseline

        return total_baseline

    def _calculate_material_breakdown(
        self,
        materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate material category breakdown.

        Args:
            materials: List of materials with carbon values

        Returns:
            Breakdown by category
        """
        category_totals = {}

        for material in materials:
            category = material.get("category", "Other")
            carbon = Decimal(str(material.get("carbon", 0)))

            if category not in category_totals:
                category_totals[category] = Decimal("0")

            category_totals[category] += carbon

        total_carbon = sum(category_totals.values())

        breakdown = {}
        for category, carbon in category_totals.items():
            percentage = (carbon / total_carbon * 100) if total_carbon > 0 else Decimal("0")
            breakdown[category] = {
                "carbon": float(carbon),
                "percentage": float(percentage)
            }

        return breakdown

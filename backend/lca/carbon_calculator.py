"""
Carbon Calculator for LCA (Life Cycle Assessment).

This module provides the core carbon calculation functionality for construction
projects, integrating with TGO emission factors from GraphDB.

Example:
    >>> from carbonscope.backend.core.knowledge_graph import GraphDBClient
    >>> from carbonscope.backend.lca.carbon_calculator import CarbonCalculator
    >>>
    >>> client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    >>> calculator = CarbonCalculator(client)
    >>>
    >>> # Calculate carbon for a single material
    >>> carbon = calculator.calculate_material_carbon(
    ...     material_name="Ready-mix Concrete C30",
    ...     quantity=150.5,
    ...     unit="m³"
    ... )
    >>> print(f"Carbon: {carbon} kgCO2e")
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from core.knowledge_graph.graphdb_client import GraphDBClient
from core.knowledge_graph.sparql_queries import get_emission_factor, MaterialNotFoundError

from .unit_converter import UnitConverter, UnitConversionError
from .material_matcher import MaterialMatcher, MaterialMatchError

logger = logging.getLogger(__name__)


class CarbonCalculationError(Exception):
    """Raised when carbon calculation fails."""
    pass


class CarbonCalculator:
    """
    Calculate embodied carbon emissions for construction projects.

    Uses TGO emission factors from GraphDB and supports:
    - Single material calculations
    - Full project carbon footprints
    - EDGE certification baseline calculations
    - Carbon savings analysis
    """

    def __init__(
        self,
        graphdb_client: GraphDBClient,
        min_match_confidence: float = 0.7,
        error_tolerance: float = 0.02
    ):
        """
        Initialize the carbon calculator.

        Args:
            graphdb_client: GraphDB client instance
            min_match_confidence: Minimum confidence for material matching (0.0-1.0)
            error_tolerance: Maximum acceptable error tolerance (default: 2%)
        """
        self.client = graphdb_client
        self.error_tolerance = error_tolerance
        self.unit_converter = UnitConverter()
        self.material_matcher = MaterialMatcher(graphdb_client, min_match_confidence)

        logger.info(
            f"Initialized CarbonCalculator (confidence: {min_match_confidence}, "
            f"tolerance: {error_tolerance})"
        )

    def calculate_material_carbon(
        self,
        material_name: str,
        quantity: float,
        unit: str,
        material_id: Optional[str] = None,
        category: Optional[str] = None,
        language: str = "en"
    ) -> Decimal:
        """
        Calculate carbon emissions for a single material.

        Args:
            material_name: Material name (for matching if material_id not provided)
            quantity: Material quantity
            unit: Unit of quantity
            material_id: Optional TGO material URI (if known)
            category: Optional material category
            language: Language for name matching ("en" or "th")

        Returns:
            Carbon emissions in kgCO2e

        Raises:
            CarbonCalculationError: If calculation fails

        Example:
            >>> carbon = calculator.calculate_material_carbon(
            ...     material_name="Concrete C30",
            ...     quantity=100,
            ...     unit="m³"
            ... )
            >>> print(carbon)  # e.g., Decimal('44560.0')
        """
        try:
            # Get material data
            if material_id:
                material_data = get_emission_factor(self.client, material_id)
            else:
                # Match material by name
                match = self.material_matcher.match_material(
                    material_name,
                    language=language,
                    category=category
                )

                if not match:
                    raise CarbonCalculationError(
                        f"Material not found: '{material_name}'. "
                        f"Please check the name or try alternatives."
                    )

                material_id = match['material_id']
                material_data = get_emission_factor(self.client, material_id)

            # Get emission factor and unit
            emission_factor = material_data['emission_factor']
            ef_unit = material_data['unit']

            # Parse emission factor unit (e.g., "kgCO2e/m³" -> "m³")
            ef_base_unit = self._extract_base_unit(ef_unit)

            # Convert quantity to match emission factor unit if needed
            quantity_decimal = Decimal(str(quantity))

            if unit.lower() != ef_base_unit.lower():
                # Determine material category for density conversion
                if not category:
                    category = material_data.get('category', 'Concrete')

                try:
                    quantity_decimal = self.unit_converter.convert(
                        quantity,
                        unit,
                        ef_base_unit,
                        material_category=category
                    )
                    logger.debug(
                        f"Converted {quantity} {unit} to {quantity_decimal} {ef_base_unit}"
                    )
                except UnitConversionError as e:
                    raise CarbonCalculationError(
                        f"Unit conversion failed: {str(e)}"
                    ) from e

            # Calculate carbon emissions
            carbon_kgco2e = quantity_decimal * emission_factor

            logger.debug(
                f"Material: {material_data.get('label_en', material_name)}, "
                f"Quantity: {quantity_decimal} {ef_base_unit}, "
                f"EF: {emission_factor} {ef_unit}, "
                f"Carbon: {carbon_kgco2e} kgCO2e"
            )

            return carbon_kgco2e

        except MaterialNotFoundError as e:
            raise CarbonCalculationError(f"Material not found: {str(e)}") from e
        except Exception as e:
            logger.error(f"Error calculating carbon for '{material_name}': {str(e)}")
            raise CarbonCalculationError(
                f"Failed to calculate carbon: {str(e)}"
            ) from e

    def calculate_project_carbon(
        self,
        boq_data: List[Dict[str, Any]],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculate total carbon emissions for a project BOQ.

        Args:
            boq_data: Bill of Quantities data (list of material entries)
            language: Language for material name matching

        Returns:
            Comprehensive carbon calculation result

        Example:
            >>> boq = [
            ...     {
            ...         "material_name": "Ready-mix Concrete C30",
            ...         "quantity": 150.5,
            ...         "unit": "m³",
            ...         "category": "Concrete"
            ...     },
            ...     {
            ...         "material_name": "Steel Rebar SD40",
            ...         "quantity": 12.3,
            ...         "unit": "ton",
            ...         "category": "Steel"
            ...     }
            ... ]
            >>> result = calculator.calculate_project_carbon(boq)
            >>> print(f"Total: {result['total_carbon_kgco2e']} kgCO2e")
        """
        try:
            calculation_date = datetime.now().isoformat()
            total_carbon = Decimal("0")
            breakdown_by_material = []
            breakdown_by_category: Dict[str, Decimal] = {}

            matched_count = 0
            unmatched_count = 0
            unmatched_materials = []

            for idx, material_entry in enumerate(boq_data, 1):
                material_name = material_entry.get('material_name')
                quantity = material_entry.get('quantity')
                unit = material_entry.get('unit')
                category = material_entry.get('category')
                material_id = material_entry.get('material_id')

                if not all([material_name, quantity, unit]):
                    logger.warning(f"Entry {idx} missing required fields, skipping")
                    continue

                try:
                    # Calculate carbon for this material
                    carbon = self.calculate_material_carbon(
                        material_name=material_name,
                        quantity=quantity,
                        unit=unit,
                        material_id=material_id,
                        category=category,
                        language=language
                    )

                    # Get emission factor for reporting
                    if material_id:
                        material_data = get_emission_factor(self.client, material_id)
                    else:
                        match = self.material_matcher.match_material(
                            material_name,
                            language=language,
                            category=category
                        )
                        if match:
                            material_data = get_emission_factor(
                                self.client,
                                match['material_id']
                            )
                        else:
                            raise CarbonCalculationError(f"Material not found: {material_name}")

                    # Add to breakdown
                    breakdown_by_material.append({
                        'material_name': material_name,
                        'material_id': material_data['material_id'],
                        'quantity': float(quantity),
                        'unit': unit,
                        'emission_factor': float(material_data['emission_factor']),
                        'emission_factor_unit': material_data['unit'],
                        'carbon_kgco2e': float(carbon),
                        'category': category or material_data.get('category', 'Other')
                    })

                    # Update totals
                    total_carbon += carbon
                    matched_count += 1

                    # Update category breakdown
                    mat_category = category or material_data.get('category', 'Other')
                    if mat_category not in breakdown_by_category:
                        breakdown_by_category[mat_category] = Decimal("0")
                    breakdown_by_category[mat_category] += carbon

                except Exception as e:
                    logger.error(f"Error calculating carbon for '{material_name}': {str(e)}")
                    unmatched_count += 1
                    unmatched_materials.append({
                        'material_name': material_name,
                        'error': str(e)
                    })

            # Calculate percentages for categories
            category_breakdown = {}
            for cat, carbon in breakdown_by_category.items():
                percentage = (carbon / total_carbon * 100) if total_carbon > 0 else 0
                category_breakdown[cat] = {
                    'carbon': float(carbon),
                    'percentage': float(percentage)
                }

            # Calculate confidence score
            total_materials = matched_count + unmatched_count
            confidence_score = matched_count / total_materials if total_materials > 0 else 0

            result = {
                'project_id': boq_data[0].get('project_id', 'Unknown'),
                'calculation_date': calculation_date,
                'total_carbon_kgco2e': float(total_carbon),
                'total_carbon_tonco2e': float(total_carbon / 1000),
                'breakdown_by_category': category_breakdown,
                'breakdown_by_material': breakdown_by_material,
                'data_quality': {
                    'matched_materials': matched_count,
                    'unmatched_materials': unmatched_count,
                    'estimated_materials': 0,  # Future: track estimated values
                    'confidence_score': confidence_score,
                    'unmatched_details': unmatched_materials
                }
            }

            logger.info(
                f"Project carbon calculation complete: {total_carbon:.2f} kgCO2e "
                f"({matched_count} matched, {unmatched_count} unmatched)"
            )

            return result

        except Exception as e:
            logger.error(f"Error calculating project carbon: {str(e)}")
            raise CarbonCalculationError(
                f"Failed to calculate project carbon: {str(e)}"
            ) from e

    def calculate_baseline_carbon(
        self,
        project_data: List[Dict[str, Any]],
        baseline_factors: Optional[Dict[str, float]] = None
    ) -> Decimal:
        """
        Calculate baseline carbon using standard Thai construction practices.

        Args:
            project_data: Project material data
            baseline_factors: Optional custom baseline emission factors by category

        Returns:
            Baseline carbon in kgCO2e

        Example:
            >>> baseline = calculator.calculate_baseline_carbon(project_data)
            >>> print(f"Baseline: {baseline} kgCO2e")
        """
        # Default baseline emission factors for Thai construction
        if baseline_factors is None:
            baseline_factors = {
                'Concrete': 445.6,  # kgCO2e/m³ - Portland cement C30
                'Steel': 3000.0,    # kgCO2e/ton - Virgin rebar
                'Brick': 4.0,       # kgCO2e/block - Concrete blocks
                'Glass': 30.0,      # kgCO2e/m² - Float glass
                'Aluminum': 8500.0, # kgCO2e/ton
                'Wood': 180.0,      # kgCO2e/m³
                'Other': 100.0      # kgCO2e/unit (generic)
            }

        try:
            baseline_carbon = Decimal("0")

            for material_entry in project_data:
                quantity = Decimal(str(material_entry.get('quantity', 0)))
                category = material_entry.get('category', 'Other')

                # Get baseline factor for category
                baseline_ef = Decimal(str(baseline_factors.get(category, 100.0)))

                # Calculate baseline carbon
                material_baseline = quantity * baseline_ef
                baseline_carbon += material_baseline

                logger.debug(
                    f"Baseline for {category}: {quantity} × {baseline_ef} = {material_baseline}"
                )

            logger.info(f"Baseline carbon: {baseline_carbon} kgCO2e")
            return baseline_carbon

        except Exception as e:
            logger.error(f"Error calculating baseline carbon: {str(e)}")
            raise CarbonCalculationError(
                f"Failed to calculate baseline carbon: {str(e)}"
            ) from e

    def calculate_carbon_savings(
        self,
        project_carbon: float,
        baseline_carbon: float
    ) -> Dict[str, Any]:
        """
        Calculate carbon savings vs baseline.

        Args:
            project_carbon: Project carbon emissions (kgCO2e)
            baseline_carbon: Baseline carbon emissions (kgCO2e)

        Returns:
            Savings analysis with EDGE certification level

        Example:
            >>> savings = calculator.calculate_carbon_savings(1900000, 2500000)
            >>> print(f"Savings: {savings['percentage_reduction']}%")
            >>> print(f"EDGE Level: {savings['edge_level']}")
        """
        try:
            project_carbon_dec = Decimal(str(project_carbon))
            baseline_carbon_dec = Decimal(str(baseline_carbon))

            if baseline_carbon_dec <= 0:
                raise CarbonCalculationError("Baseline carbon must be positive")

            # Calculate absolute savings
            absolute_savings = baseline_carbon_dec - project_carbon_dec

            # Calculate percentage reduction
            percentage_reduction = (absolute_savings / baseline_carbon_dec) * 100

            # Determine EDGE certification level
            if percentage_reduction >= 100:
                edge_level = "Zero Carbon"
                edge_compliant = True
            elif percentage_reduction >= 40:
                edge_level = "EDGE Advanced"
                edge_compliant = True
            elif percentage_reduction >= 20:
                edge_level = "EDGE Certified"
                edge_compliant = True
            else:
                edge_level = "Not Certified"
                edge_compliant = False

            result = {
                'project_carbon_kgco2e': float(project_carbon_dec),
                'baseline_carbon_kgco2e': float(baseline_carbon_dec),
                'absolute_savings_kgco2e': float(absolute_savings),
                'absolute_savings_tonco2e': float(absolute_savings / 1000),
                'percentage_reduction': float(percentage_reduction),
                'edge_level': edge_level,
                'edge_compliant': edge_compliant,
                'savings_per_sqm': None  # Calculated if project area provided
            }

            logger.info(
                f"Carbon savings: {percentage_reduction:.2f}% "
                f"(EDGE: {edge_level}, Compliant: {edge_compliant})"
            )

            return result

        except Exception as e:
            logger.error(f"Error calculating carbon savings: {str(e)}")
            raise CarbonCalculationError(
                f"Failed to calculate carbon savings: {str(e)}"
            ) from e

    def calculate_carbon_intensity(
        self,
        total_carbon: float,
        project_area: float,
        area_unit: str = "m²"
    ) -> Decimal:
        """
        Calculate carbon intensity (kgCO2e per unit area).

        Args:
            total_carbon: Total carbon emissions (kgCO2e)
            project_area: Project floor area
            area_unit: Area unit (default: "m²")

        Returns:
            Carbon intensity in kgCO2e/m²
        """
        try:
            # Convert area to m² if needed
            area_m2 = self.unit_converter.convert(
                project_area,
                area_unit,
                "m²"
            )

            if area_m2 <= 0:
                raise CarbonCalculationError("Project area must be positive")

            intensity = Decimal(str(total_carbon)) / area_m2

            logger.debug(
                f"Carbon intensity: {total_carbon} kgCO2e / {area_m2} m² = {intensity} kgCO2e/m²"
            )

            return intensity

        except Exception as e:
            logger.error(f"Error calculating carbon intensity: {str(e)}")
            raise CarbonCalculationError(
                f"Failed to calculate carbon intensity: {str(e)}"
            ) from e

    def _extract_base_unit(self, ef_unit: str) -> str:
        """
        Extract base unit from emission factor unit.

        Args:
            ef_unit: Emission factor unit (e.g., "kgCO2e/m³")

        Returns:
            Base unit (e.g., "m³")
        """
        # Split on "/" to get denominator
        if '/' in ef_unit:
            parts = ef_unit.split('/')
            return parts[-1].strip()
        else:
            # No denominator, assume per unit
            return "unit"

    def generate_carbon_report(
        self,
        boq_data: List[Dict[str, Any]],
        project_area: Optional[float] = None,
        baseline_factors: Optional[Dict[str, float]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive carbon assessment report.

        Args:
            boq_data: Bill of Quantities data
            project_area: Optional project floor area (m²)
            baseline_factors: Optional custom baseline factors
            language: Language for material matching

        Returns:
            Complete carbon assessment report with EDGE compliance
        """
        try:
            # Calculate project carbon
            project_result = self.calculate_project_carbon(boq_data, language=language)

            # Calculate baseline
            baseline_carbon = self.calculate_baseline_carbon(
                boq_data,
                baseline_factors=baseline_factors
            )

            # Calculate savings
            savings = self.calculate_carbon_savings(
                project_result['total_carbon_kgco2e'],
                float(baseline_carbon)
            )

            # Calculate intensity if area provided
            intensity = None
            if project_area:
                intensity = float(self.calculate_carbon_intensity(
                    project_result['total_carbon_kgco2e'],
                    project_area
                ))
                savings['savings_per_sqm'] = float(
                    Decimal(str(savings['absolute_savings_kgco2e'])) / Decimal(str(project_area))
                )

            # Combine into comprehensive report
            report = {
                'project_id': project_result['project_id'],
                'calculation_date': project_result['calculation_date'],
                'project_area_m2': project_area,
                'carbon_intensity_kgco2e_per_m2': intensity,
                'project_carbon': {
                    'total_kgco2e': project_result['total_carbon_kgco2e'],
                    'total_tonco2e': project_result['total_carbon_tonco2e'],
                    'breakdown_by_category': project_result['breakdown_by_category'],
                    'breakdown_by_material': project_result['breakdown_by_material']
                },
                'baseline_carbon': {
                    'total_kgco2e': float(baseline_carbon),
                    'total_tonco2e': float(baseline_carbon / 1000)
                },
                'carbon_savings': savings,
                'edge_certification': {
                    'level': savings['edge_level'],
                    'compliant': savings['edge_compliant'],
                    'reduction_percentage': savings['percentage_reduction'],
                    'required_for_certified': 20.0,
                    'required_for_advanced': 40.0
                },
                'data_quality': project_result['data_quality']
            }

            logger.info(
                f"Carbon report generated: Project={project_result['total_carbon_kgco2e']:.2f} kgCO2e, "
                f"Baseline={baseline_carbon:.2f} kgCO2e, "
                f"Reduction={savings['percentage_reduction']:.2f}%, "
                f"EDGE={savings['edge_level']}"
            )

            return report

        except Exception as e:
            logger.error(f"Error generating carbon report: {str(e)}")
            raise CarbonCalculationError(
                f"Failed to generate carbon report: {str(e)}"
            ) from e

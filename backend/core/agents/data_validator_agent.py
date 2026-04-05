"""Data Validator Agent for quality assurance and validation.

This agent performs data quality checks, unit consistency validation,
and sanity range checks on input data and calculation results.
"""

import logging
from typing import Dict, Any, List
from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class DataValidatorAgent(Agent):
    """Agent for data quality validation and sanity checks.

    This agent:
    1. Validates unit consistency
    2. Performs sanity range checks on emission factors
    3. Cross-validates against industry benchmarks
    4. Flags abnormal values for review

    Capabilities:
        - validate:data
        - check:quality
    """

    # Industry benchmark ranges (kgCO2e per unit)
    EMISSION_FACTOR_RANGES = {
        "concrete": {"min": 100, "max": 500, "unit": "m³"},
        "steel": {"min": 1.5, "max": 3.5, "unit": "kg"},
        "glass": {"min": 10, "max": 50, "unit": "m²"},
        "wood": {"min": 50, "max": 300, "unit": "m³"},
        "aluminum": {"min": 8, "max": 15, "unit": "kg"},
    }

    def __init__(self, validation_service=None):
        """Initialize Data Validator Agent.

        Args:
            validation_service: Optional validation service from Phase 2.
                              If None, uses built-in validation rules.
        """
        super().__init__(
            name="data_validator",
            capabilities={"validate:data", "check:quality"}
        )
        self.validation_service = validation_service

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute data validation.

        Args:
            state: Current agent state

        Returns:
            Dictionary with:
                - validation_passed: bool indicating overall validation status
                - warnings: List of validation warnings
                - errors: List of validation errors
                - validation_details: Detailed validation results

        Example:
            >>> state = {
            ...     "user_query": "Validate data quality",
            ...     "task_results": {
            ...         "material_breakdown": [...]
            ...     }
            ... }
            >>> result = await agent.execute(state)
            >>> result["validation_passed"]
            True
        """
        logger.info(f"Data Validator Agent executing: {state['user_query']}")

        task_results = state.get("task_results", {})
        materials = task_results.get("material_breakdown", [])
        boq_materials = task_results.get("boq_materials", [])

        warnings = []
        errors = []
        validation_details = []

        # Validate material data
        if materials:
            material_validation = self._validate_materials(materials)
            warnings.extend(material_validation["warnings"])
            errors.extend(material_validation["errors"])
            validation_details.append(material_validation)

        # Validate BOQ data
        if boq_materials:
            boq_validation = self._validate_boq_data(boq_materials)
            warnings.extend(boq_validation["warnings"])
            errors.extend(boq_validation["errors"])
            validation_details.append(boq_validation)

        # Validate unit consistency
        unit_validation = self._validate_unit_consistency(materials)
        warnings.extend(unit_validation["warnings"])
        errors.extend(unit_validation["errors"])
        validation_details.append(unit_validation)

        # Overall validation status
        validation_passed = len(errors) == 0

        logger.info(
            f"Data validation complete: "
            f"{'PASSED' if validation_passed else 'FAILED'} "
            f"({len(warnings)} warnings, {len(errors)} errors)"
        )

        return {
            "validation_passed": validation_passed,
            "warnings": warnings,
            "errors": errors,
            "validation_details": validation_details,
            "warnings_count": len(warnings),
            "errors_count": len(errors)
        }

    def _validate_materials(
        self,
        materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate material data quality.

        Args:
            materials: List of material dictionaries

        Returns:
            Validation results with warnings and errors
        """
        warnings = []
        errors = []

        for material in materials:
            material_id = material.get("material_id", "unknown")
            material_name = material.get("name", "unknown")

            # Check for required fields
            if not material.get("emission_factor"):
                errors.append({
                    "material_id": material_id,
                    "field": "emission_factor",
                    "message": f"Missing emission factor for {material_name}"
                })

            if not material.get("quantity"):
                errors.append({
                    "material_id": material_id,
                    "field": "quantity",
                    "message": f"Missing quantity for {material_name}"
                })

            # Validate emission factor range
            emission_factor = material.get("emission_factor", 0)
            if emission_factor:
                range_check = self._check_emission_factor_range(
                    material_name,
                    float(emission_factor)
                )
                if not range_check["valid"]:
                    warnings.append({
                        "material_id": material_id,
                        "field": "emission_factor",
                        "message": range_check["message"],
                        "expected_range": range_check["expected_range"]
                    })

            # Validate quantity is positive
            quantity = material.get("quantity", 0)
            if quantity <= 0:
                errors.append({
                    "material_id": material_id,
                    "field": "quantity",
                    "message": f"Quantity must be positive for {material_name}, got {quantity}"
                })

        return {
            "validation_type": "material_data",
            "materials_checked": len(materials),
            "warnings": warnings,
            "errors": errors
        }

    def _check_emission_factor_range(
        self,
        material_name: str,
        emission_factor: float
    ) -> Dict[str, Any]:
        """Check if emission factor is within expected range.

        Args:
            material_name: Material name
            emission_factor: Emission factor value

        Returns:
            Validation result dictionary
        """
        material_name_lower = material_name.lower()

        # Determine material type
        material_type = None
        for mat_type in self.EMISSION_FACTOR_RANGES.keys():
            if mat_type in material_name_lower:
                material_type = mat_type
                break

        if not material_type:
            # Unknown material type - skip range check
            return {"valid": True}

        # Check range
        range_data = self.EMISSION_FACTOR_RANGES[material_type]
        min_val = range_data["min"]
        max_val = range_data["max"]
        unit = range_data["unit"]

        if emission_factor < min_val or emission_factor > max_val:
            return {
                "valid": False,
                "message": (
                    f"Emission factor {emission_factor} kgCO2e/{unit} "
                    f"for {material_name} is outside typical range "
                    f"({min_val}-{max_val} kgCO2e/{unit})"
                ),
                "expected_range": {"min": min_val, "max": max_val, "unit": unit}
            }

        return {"valid": True}

    def _validate_boq_data(
        self,
        boq_materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate BOQ data quality.

        Args:
            boq_materials: List of BOQ material dictionaries

        Returns:
            Validation results
        """
        warnings = []
        errors = []

        for material in boq_materials:
            item_id = material.get("item_id", "unknown")
            description = material.get("description", "")

            # Check for required fields
            if not description:
                errors.append({
                    "item_id": item_id,
                    "field": "description",
                    "message": f"Missing description for BOQ item {item_id}"
                })

            if not material.get("unit"):
                errors.append({
                    "item_id": item_id,
                    "field": "unit",
                    "message": f"Missing unit for BOQ item {item_id}"
                })

            # Check for suspiciously large quantities
            quantity = material.get("quantity", 0)
            unit = material.get("unit", "")

            if unit == "m³" and quantity > 10000:
                warnings.append({
                    "item_id": item_id,
                    "field": "quantity",
                    "message": (
                        f"Very large concrete/material quantity: {quantity} m³ "
                        f"for item {item_id} - please verify"
                    )
                })
            elif unit == "kg" and quantity > 100000:
                warnings.append({
                    "item_id": item_id,
                    "field": "quantity",
                    "message": (
                        f"Very large material quantity: {quantity} kg "
                        f"for item {item_id} - please verify"
                    )
                })

        return {
            "validation_type": "boq_data",
            "items_checked": len(boq_materials),
            "warnings": warnings,
            "errors": errors
        }

    def _validate_unit_consistency(
        self,
        materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate unit consistency across materials.

        Args:
            materials: List of material dictionaries

        Returns:
            Validation results
        """
        warnings = []
        errors = []

        # Valid units
        valid_units = {"m³", "m²", "kg", "ton", "piece", "m"}

        for material in materials:
            material_id = material.get("material_id", "unknown")
            unit = material.get("unit", "")

            # Check if unit is recognized
            if unit and unit not in valid_units:
                warnings.append({
                    "material_id": material_id,
                    "field": "unit",
                    "message": f"Unrecognized unit '{unit}' for material {material_id}",
                    "valid_units": list(valid_units)
                })

        return {
            "validation_type": "unit_consistency",
            "materials_checked": len(materials),
            "valid_units": list(valid_units),
            "warnings": warnings,
            "errors": errors
        }


def data_validator_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node function for Data Validator agent.

    Args:
        state: Current AgentState

    Returns:
        Dictionary with data validation results
    """
    agent = DataValidatorAgent()
    import asyncio
    return asyncio.run(agent.execute(state))

"""
Unit Conversion Utilities for LCA Calculator.

This module provides unit conversion capabilities for construction materials,
including volume, mass, area, and length conversions with material-specific
density support.

Example:
    >>> converter = UnitConverter()
    >>> kg = converter.convert_volume_to_mass(10, "m³", "Concrete")
    >>> print(kg)  # 24000.0 kg (10 m³ × 2400 kg/m³)
"""

from decimal import Decimal
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class UnitConversionError(Exception):
    """Raised when unit conversion fails."""
    pass


class UnitConverter:
    """
    Convert between different units for construction materials.

    Supports:
    - Volume: m³, liters, cm³
    - Mass: kg, ton, g, tonne
    - Area: m², cm², mm²
    - Length: m, cm, mm
    - Material-specific density conversions
    """

    # Material densities (kg/m³)
    MATERIAL_DENSITIES: Dict[str, Decimal] = {
        # Concrete types
        "Concrete": Decimal("2400"),
        "Concrete_Normal": Decimal("2400"),
        "Concrete_Lightweight": Decimal("1800"),
        "Concrete_Heavy": Decimal("2600"),

        # Metals
        "Steel": Decimal("7850"),
        "Steel_Rebar": Decimal("7850"),
        "Steel_Structural": Decimal("7850"),
        "Aluminum": Decimal("2700"),
        "Copper": Decimal("8960"),
        "Zinc": Decimal("7140"),

        # Wood types
        "Wood": Decimal("600"),  # Average
        "Wood_Softwood": Decimal("500"),
        "Wood_Hardwood": Decimal("750"),
        "Wood_Teak": Decimal("650"),
        "Wood_Oak": Decimal("750"),
        "Plywood": Decimal("600"),

        # Glass
        "Glass": Decimal("2500"),
        "Glass_Float": Decimal("2500"),
        "Glass_Tempered": Decimal("2500"),

        # Masonry
        "Brick": Decimal("1800"),
        "Block_Concrete": Decimal("2000"),
        "Block_AAC": Decimal("600"),  # Autoclaved Aerated Concrete

        # Other materials
        "Gypsum": Decimal("900"),
        "Ceramic": Decimal("2300"),
        "Plastic_PVC": Decimal("1400"),
        "Asphalt": Decimal("2360"),
        "Sand": Decimal("1600"),
        "Gravel": Decimal("1680"),
    }

    # Volume conversion factors to m³
    VOLUME_TO_M3: Dict[str, Decimal] = {
        "m³": Decimal("1"),
        "m3": Decimal("1"),
        "cubic_meter": Decimal("1"),
        "liter": Decimal("0.001"),
        "liters": Decimal("0.001"),
        "l": Decimal("0.001"),
        "cm³": Decimal("0.000001"),
        "cm3": Decimal("0.000001"),
        "cubic_cm": Decimal("0.000001"),
    }

    # Mass conversion factors to kg
    MASS_TO_KG: Dict[str, Decimal] = {
        "kg": Decimal("1"),
        "kilogram": Decimal("1"),
        "kilograms": Decimal("1"),
        "ton": Decimal("1000"),
        "tons": Decimal("1000"),
        "tonne": Decimal("1000"),
        "tonnes": Decimal("1000"),
        "metric_ton": Decimal("1000"),
        "g": Decimal("0.001"),
        "gram": Decimal("0.001"),
        "grams": Decimal("0.001"),
        "mg": Decimal("0.000001"),
        "milligram": Decimal("0.000001"),
    }

    # Area conversion factors to m²
    AREA_TO_M2: Dict[str, Decimal] = {
        "m²": Decimal("1"),
        "m2": Decimal("1"),
        "square_meter": Decimal("1"),
        "cm²": Decimal("0.0001"),
        "cm2": Decimal("0.0001"),
        "square_cm": Decimal("0.0001"),
        "mm²": Decimal("0.000001"),
        "mm2": Decimal("0.000001"),
        "square_mm": Decimal("0.000001"),
    }

    # Length conversion factors to m
    LENGTH_TO_M: Dict[str, Decimal] = {
        "m": Decimal("1"),
        "meter": Decimal("1"),
        "meters": Decimal("1"),
        "cm": Decimal("0.01"),
        "centimeter": Decimal("0.01"),
        "centimeters": Decimal("0.01"),
        "mm": Decimal("0.001"),
        "millimeter": Decimal("0.001"),
        "millimeters": Decimal("0.001"),
        "km": Decimal("1000"),
        "kilometer": Decimal("1000"),
    }

    def __init__(self):
        """Initialize the unit converter."""
        logger.debug("Initialized UnitConverter")

    def convert(
        self,
        quantity: float,
        from_unit: str,
        to_unit: str,
        material_category: Optional[str] = None
    ) -> Decimal:
        """
        Convert quantity from one unit to another.

        Args:
            quantity: Quantity to convert
            from_unit: Source unit
            to_unit: Target unit
            material_category: Optional material category for density-based conversion

        Returns:
            Converted quantity as Decimal

        Raises:
            UnitConversionError: If conversion is not possible

        Example:
            >>> converter.convert(10, "m³", "kg", "Concrete")
            Decimal('24000')
        """
        quantity_decimal = Decimal(str(quantity))
        from_unit_lower = from_unit.lower()
        to_unit_lower = to_unit.lower()

        # Same unit - no conversion needed
        if from_unit_lower == to_unit_lower:
            return quantity_decimal

        # Try direct conversion within same unit type
        try:
            # Volume to volume
            if from_unit_lower in self.VOLUME_TO_M3 and to_unit_lower in self.VOLUME_TO_M3:
                return self._convert_volume(quantity_decimal, from_unit_lower, to_unit_lower)

            # Mass to mass
            if from_unit_lower in self.MASS_TO_KG and to_unit_lower in self.MASS_TO_KG:
                return self._convert_mass(quantity_decimal, from_unit_lower, to_unit_lower)

            # Area to area
            if from_unit_lower in self.AREA_TO_M2 and to_unit_lower in self.AREA_TO_M2:
                return self._convert_area(quantity_decimal, from_unit_lower, to_unit_lower)

            # Length to length
            if from_unit_lower in self.LENGTH_TO_M and to_unit_lower in self.LENGTH_TO_M:
                return self._convert_length(quantity_decimal, from_unit_lower, to_unit_lower)

            # Volume to mass (requires material density)
            if from_unit_lower in self.VOLUME_TO_M3 and to_unit_lower in self.MASS_TO_KG:
                if not material_category:
                    raise UnitConversionError(
                        f"Material category required for volume to mass conversion"
                    )
                return self.convert_volume_to_mass(
                    quantity_decimal, from_unit_lower, material_category, to_unit_lower
                )

            # Mass to volume (requires material density)
            if from_unit_lower in self.MASS_TO_KG and to_unit_lower in self.VOLUME_TO_M3:
                if not material_category:
                    raise UnitConversionError(
                        f"Material category required for mass to volume conversion"
                    )
                return self.convert_mass_to_volume(
                    quantity_decimal, from_unit_lower, material_category, to_unit_lower
                )

            raise UnitConversionError(
                f"Cannot convert from '{from_unit}' to '{to_unit}'"
            )

        except Exception as e:
            logger.error(f"Unit conversion error: {str(e)}")
            raise UnitConversionError(f"Failed to convert units: {str(e)}") from e

    def _convert_volume(self, quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """Convert between volume units."""
        # Convert to m³ first, then to target unit
        m3 = quantity * self.VOLUME_TO_M3[from_unit]
        result = m3 / self.VOLUME_TO_M3[to_unit]
        logger.debug(f"Volume conversion: {quantity} {from_unit} = {result} {to_unit}")
        return result

    def _convert_mass(self, quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """Convert between mass units."""
        # Convert to kg first, then to target unit
        kg = quantity * self.MASS_TO_KG[from_unit]
        result = kg / self.MASS_TO_KG[to_unit]
        logger.debug(f"Mass conversion: {quantity} {from_unit} = {result} {to_unit}")
        return result

    def _convert_area(self, quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """Convert between area units."""
        # Convert to m² first, then to target unit
        m2 = quantity * self.AREA_TO_M2[from_unit]
        result = m2 / self.AREA_TO_M2[to_unit]
        logger.debug(f"Area conversion: {quantity} {from_unit} = {result} {to_unit}")
        return result

    def _convert_length(self, quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """Convert between length units."""
        # Convert to m first, then to target unit
        m = quantity * self.LENGTH_TO_M[from_unit]
        result = m / self.LENGTH_TO_M[to_unit]
        logger.debug(f"Length conversion: {quantity} {from_unit} = {result} {to_unit}")
        return result

    def convert_volume_to_mass(
        self,
        quantity: float,
        volume_unit: str,
        material_category: str,
        mass_unit: str = "kg"
    ) -> Decimal:
        """
        Convert volume to mass using material density.

        Args:
            quantity: Volume quantity
            volume_unit: Volume unit (e.g., "m³", "liters")
            material_category: Material category for density lookup
            mass_unit: Target mass unit (default: "kg")

        Returns:
            Mass in target unit

        Raises:
            UnitConversionError: If material density not found or conversion fails

        Example:
            >>> converter.convert_volume_to_mass(10, "m³", "Concrete")
            Decimal('24000')  # 10 m³ × 2400 kg/m³
        """
        try:
            quantity_decimal = Decimal(str(quantity))
            volume_unit_lower = volume_unit.lower()
            mass_unit_lower = mass_unit.lower()

            # Get material density
            density = self.get_material_density(material_category)

            # Convert volume to m³
            volume_m3 = quantity_decimal * self.VOLUME_TO_M3[volume_unit_lower]

            # Calculate mass in kg
            mass_kg = volume_m3 * density

            # Convert to target mass unit
            result = mass_kg / self.MASS_TO_KG[mass_unit_lower]

            logger.debug(
                f"Volume to mass: {quantity} {volume_unit} ({material_category}) = {result} {mass_unit}"
            )
            return result

        except KeyError as e:
            raise UnitConversionError(f"Unknown unit or material: {str(e)}") from e
        except Exception as e:
            raise UnitConversionError(f"Volume to mass conversion failed: {str(e)}") from e

    def convert_mass_to_volume(
        self,
        quantity: float,
        mass_unit: str,
        material_category: str,
        volume_unit: str = "m³"
    ) -> Decimal:
        """
        Convert mass to volume using material density.

        Args:
            quantity: Mass quantity
            mass_unit: Mass unit (e.g., "kg", "ton")
            material_category: Material category for density lookup
            volume_unit: Target volume unit (default: "m³")

        Returns:
            Volume in target unit

        Raises:
            UnitConversionError: If material density not found or conversion fails
        """
        try:
            quantity_decimal = Decimal(str(quantity))
            mass_unit_lower = mass_unit.lower()
            volume_unit_lower = volume_unit.lower()

            # Get material density
            density = self.get_material_density(material_category)

            # Convert mass to kg
            mass_kg = quantity_decimal * self.MASS_TO_KG[mass_unit_lower]

            # Calculate volume in m³
            volume_m3 = mass_kg / density

            # Convert to target volume unit
            result = volume_m3 / self.VOLUME_TO_M3[volume_unit_lower]

            logger.debug(
                f"Mass to volume: {quantity} {mass_unit} ({material_category}) = {result} {volume_unit}"
            )
            return result

        except KeyError as e:
            raise UnitConversionError(f"Unknown unit or material: {str(e)}") from e
        except ZeroDivisionError:
            raise UnitConversionError(f"Material density is zero for {material_category}")
        except Exception as e:
            raise UnitConversionError(f"Mass to volume conversion failed: {str(e)}") from e

    def get_material_density(self, material_category: str) -> Decimal:
        """
        Get density for a material category.

        Args:
            material_category: Material category name

        Returns:
            Density in kg/m³

        Raises:
            UnitConversionError: If material not found
        """
        # Try exact match first
        if material_category in self.MATERIAL_DENSITIES:
            return self.MATERIAL_DENSITIES[material_category]

        # Try partial match (e.g., "Concrete C30" matches "Concrete")
        for key in self.MATERIAL_DENSITIES:
            if material_category.startswith(key) or key in material_category:
                logger.debug(f"Using density for '{key}' for material '{material_category}'")
                return self.MATERIAL_DENSITIES[key]

        raise UnitConversionError(
            f"Unknown material category: '{material_category}'. "
            f"Available categories: {', '.join(self.MATERIAL_DENSITIES.keys())}"
        )

    def add_material_density(self, material_category: str, density_kg_m3: float) -> None:
        """
        Add or update a material density.

        Args:
            material_category: Material category name
            density_kg_m3: Density in kg/m³
        """
        self.MATERIAL_DENSITIES[material_category] = Decimal(str(density_kg_m3))
        logger.info(f"Added/updated density for '{material_category}': {density_kg_m3} kg/m³")

    def get_unit_type(self, unit: str) -> Optional[str]:
        """
        Determine the type of a unit (volume, mass, area, length).

        Args:
            unit: Unit string

        Returns:
            Unit type or None if unknown
        """
        unit_lower = unit.lower()

        if unit_lower in self.VOLUME_TO_M3:
            return "volume"
        elif unit_lower in self.MASS_TO_KG:
            return "mass"
        elif unit_lower in self.AREA_TO_M2:
            return "area"
        elif unit_lower in self.LENGTH_TO_M:
            return "length"
        else:
            return None

    def normalize_unit(self, quantity: float, unit: str) -> Tuple[Decimal, str]:
        """
        Normalize a quantity to the base unit of its type.

        Args:
            quantity: Quantity value
            unit: Unit string

        Returns:
            Tuple of (normalized_quantity, base_unit)

        Example:
            >>> converter.normalize_unit(1000, "kg")
            (Decimal('1000'), 'kg')
            >>> converter.normalize_unit(2, "ton")
            (Decimal('2000'), 'kg')
        """
        unit_type = self.get_unit_type(unit)

        if unit_type == "volume":
            base_unit = "m³"
            normalized = self._convert_volume(Decimal(str(quantity)), unit.lower(), "m³")
        elif unit_type == "mass":
            base_unit = "kg"
            normalized = self._convert_mass(Decimal(str(quantity)), unit.lower(), "kg")
        elif unit_type == "area":
            base_unit = "m²"
            normalized = self._convert_area(Decimal(str(quantity)), unit.lower(), "m²")
        elif unit_type == "length":
            base_unit = "m"
            normalized = self._convert_length(Decimal(str(quantity)), unit.lower(), "m")
        else:
            # Unknown unit - return as-is
            base_unit = unit
            normalized = Decimal(str(quantity))

        return normalized, base_unit

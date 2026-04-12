"""LCA (Life Cycle Assessment) Module for carbonscope BIM Agent.

This module provides embodied carbon calculations for construction projects
with Thailand-specific building materials data from TGO.

Key Components:
- carbon_calculator: Core LCA calculator for embodied carbon
- unit_converter: Unit conversion utilities
- material_matcher: Material name matching against TGO database
- brightway_config: Brightway2 integration (optional)
- tests: Comprehensive test suite

Usage:
    from carbonscope.backend.lca import CarbonCalculator
    from carbonscope.backend.core.knowledge_graph import GraphDBClient

    # Initialize GraphDB client
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

    # Create calculator
    calculator = CarbonCalculator(client)

    # Calculate carbon for project
    boq = [
        {
            "material_name": "Ready-mix Concrete C30",
            "quantity": 150.5,
            "unit": "m³",
            "category": "Concrete"
        }
    ]
    result = calculator.calculate_project_carbon(boq)
    print(f"Total carbon: {result['total_carbon_tonco2e']} tCO2e")
"""

from .carbon_calculator import CarbonCalculator, CarbonCalculationError
from .unit_converter import UnitConverter, UnitConversionError
from .material_matcher import MaterialMatcher, MaterialMatchError

from .brightway_config import (
    DeterministicConfig,
    ProjectConfig,
    PathConfig,
    GraphDBConfig,
    PerformanceConfig,
    ValidationConfig,
    UnitConfig,
    LoggingConfig,
    initialize_brightway,
)

__version__ = "1.1.0"

__all__ = [
    # Core LCA Components
    "CarbonCalculator",
    "CarbonCalculationError",
    "UnitConverter",
    "UnitConversionError",
    "MaterialMatcher",
    "MaterialMatchError",

    # Brightway2 Components (optional)
    "DeterministicConfig",
    "ProjectConfig",
    "PathConfig",
    "GraphDBConfig",
    "PerformanceConfig",
    "ValidationConfig",
    "UnitConfig",
    "LoggingConfig",
    "initialize_brightway",
]

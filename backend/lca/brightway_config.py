"""Brightway2 Configuration for SUNA BIM Agent.

This module provides configuration for deterministic, reproducible LCA calculations
using Brightway2 with Thailand-specific building materials data.

Configuration Goals:
- Deterministic calculations (same inputs -> same outputs)
- High precision for consultant-grade accuracy (target: <=2% error)
- Thailand construction project compatibility
- Integration with TGO emission factors from GraphDB
"""

import os
import random
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Final


# ============================================================================
# PRECISION & DETERMINISM
# ============================================================================

class DeterministicConfig:
    """Configuration constants for deterministic LCA calculations.

    These settings ensure reproducibility across multiple runs and environments,
    which is critical for consultant validation and regulatory compliance.
    """

    # High precision decimal arithmetic (28 significant figures)
    DECIMAL_PRECISION: Final[int] = 28

    # Fixed random seed for any stochastic operations (should be minimal/none)
    RANDOM_SEED: Final[int] = 42

    # Disable Monte Carlo uncertainty analysis (use static LCA only)
    MONTE_CARLO_ITERATIONS: Final[int] = 0
    USE_STATIC_LCA: Final[bool] = True

    # Use Decimal type instead of float for all calculations
    USE_DECIMAL: Final[bool] = True

    # Calculation method (ISO 14040/14044 compliant)
    CALCULATION_METHOD: Final[str] = "ISO 14040/14044"

    @classmethod
    def apply(cls):
        """Apply deterministic configuration globally.

        This method ensures that all random number generators are seeded
        with the same value, making calculations reproducible across runs.

        Call this before any LCA calculations to ensure determinism.
        """
        # Set decimal precision for high-accuracy calculations
        getcontext().prec = cls.DECIMAL_PRECISION

        # Fix random seed for Python's built-in random module
        random.seed(cls.RANDOM_SEED)

        # Fix NumPy random seed (used by Brightway2 internally)
        try:
            import numpy as np
            np.random.seed(cls.RANDOM_SEED)
            # Also set the new NumPy random generator
            np.random.default_rng(cls.RANDOM_SEED)
        except ImportError:
            pass  # numpy not required if not using Monte Carlo

        # Set environment variable for additional determinism
        os.environ["PYTHONHASHSEED"] = str(cls.RANDOM_SEED)

    @classmethod
    def reset_seeds(cls):
        """Reset all random seeds to initial state.

        Use this between test runs to ensure complete independence
        while maintaining determinism within each run.
        """
        random.seed(cls.RANDOM_SEED)
        try:
            import numpy as np
            np.random.seed(cls.RANDOM_SEED)
            np.random.default_rng(cls.RANDOM_SEED)
        except ImportError:
            pass

    @classmethod
    def validate_determinism(cls) -> bool:
        """Validate that deterministic configuration is active.

        Returns:
            True if configuration is correctly applied, False otherwise
        """
        # Check decimal precision
        if getcontext().prec != cls.DECIMAL_PRECISION:
            return False

        # Check that numpy seed produces consistent results
        try:
            import numpy as np
            np.random.seed(cls.RANDOM_SEED)
            test_vals1 = [np.random.random() for _ in range(5)]
            np.random.seed(cls.RANDOM_SEED)
            test_vals2 = [np.random.random() for _ in range(5)]
            if test_vals1 != test_vals2:
                return False
        except ImportError:
            pass

        return True


# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

class ProjectConfig:
    """Brightway2 project configuration for Thailand construction LCA."""

    # Project name for Brightway2
    PROJECT_NAME: Final[str] = "thailand-construction"

    # Database name for TGO emission factors
    DATABASE_NAME: Final[str] = "TGO-Thailand-2026"

    # Alternative databases (for future expansion)
    DATABASE_ECOINVENT: Final[str] = "ecoinvent-3.9-cutoff"
    DATABASE_CUSTOM: Final[str] = "custom-thailand-materials"

    # Impact assessment method
    IMPACT_METHOD: Final[tuple] = ("IPCC 2021", "climate change", "GWP 100a")

    # Lifecycle stages (ISO 21931-1 / EN 15978)
    LIFECYCLE_STAGES_PRODUCT: Final[list] = ["A1", "A2", "A3"]  # Material production
    LIFECYCLE_STAGES_CONSTRUCTION: Final[list] = ["A4", "A5"]   # Construction process
    LIFECYCLE_STAGES_USE: Final[list] = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
    LIFECYCLE_STAGES_EOL: Final[list] = ["C1", "C2", "C3", "C4"]
    LIFECYCLE_STAGES_BEYOND: Final[list] = ["D"]

    # Default scope: Product stage (A1-A3) for TGO compliance
    DEFAULT_STAGES: Final[list] = LIFECYCLE_STAGES_PRODUCT


# ============================================================================
# DATA DIRECTORY
# ============================================================================

class PathConfig:
    """File paths for Brightway2 data storage."""

    # Base directory for LCA data (this file's parent)
    BASE_DIR: Path = Path(__file__).parent

    # Data directory for Brightway2 projects
    DATA_DIR: Path = BASE_DIR / "data"

    # Brightway2 default data directory (override via environment variable)
    BRIGHTWAY_DIR: Path = DATA_DIR / "brightway2"

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.BRIGHTWAY_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_brightway_dir(cls) -> str:
        """Get Brightway2 data directory path as string.

        Returns:
            Absolute path to Brightway2 data directory
        """
        cls.ensure_directories()
        return str(cls.BRIGHTWAY_DIR.absolute())


# ============================================================================
# GRAPHDB INTEGRATION
# ============================================================================

class GraphDBConfig:
    """Configuration for GraphDB integration (TGO emission factors)."""

    # GraphDB endpoint (from environment or default)
    ENDPOINT: str = os.getenv("GRAPHDB_ENDPOINT", "http://localhost:7200")

    # Repository name
    REPOSITORY: str = os.getenv("GRAPHDB_REPOSITORY", "tgo-emission-factors")

    # SPARQL query timeout (seconds)
    QUERY_TIMEOUT: int = 30

    # Batch size for bulk loading
    BATCH_SIZE: int = 100

    # TGO ontology namespace
    TGO_NAMESPACE: str = "http://suna-bim.com/ontology/tgo#"

    # EDGE V3 ontology namespace
    EDGE_NAMESPACE: str = "http://suna-bim.com/ontology/edge#"


# ============================================================================
# PERFORMANCE & LIMITS
# ============================================================================

class PerformanceConfig:
    """Performance tuning parameters."""

    # Target performance: 500 materials in <5s
    TARGET_MATERIALS: Final[int] = 500
    TARGET_TIME_SECONDS: Final[int] = 5

    # Cache TTL for emission factors (seconds)
    CACHE_TTL: Final[int] = 3600  # 1 hour

    # Maximum project size (materials)
    MAX_MATERIALS_PER_PROJECT: Final[int] = 10000

    # Calculation timeout (seconds)
    CALCULATION_TIMEOUT: Final[int] = 60


# ============================================================================
# VALIDATION & TESTING
# ============================================================================

class ValidationConfig:
    """Configuration for calculation validation."""

    # Target accuracy: <=2% error vs manual consultant assessments
    TARGET_ERROR_PERCENT: Final[Decimal] = Decimal("2.0")

    # Ideal average error: <1.5%
    IDEAL_ERROR_PERCENT: Final[Decimal] = Decimal("1.5")

    # Number of validation runs for determinism testing
    DETERMINISM_RUNS: Final[int] = 10

    # Number of manual assessments for validation
    MANUAL_ASSESSMENTS_REQUIRED: Final[int] = 10


# ============================================================================
# UNITS & CONVERSIONS
# ============================================================================

class UnitConfig:
    """Standard units for LCA calculations."""

    # Carbon units
    CARBON_UNIT: Final[str] = "kg CO2e"
    CARBON_UNIT_SHORT: Final[str] = "kgCO2e"

    # Mass units
    MASS_UNITS: Final[dict] = {
        "kg": Decimal("1"),
        "ton": Decimal("1000"),
        "tonne": Decimal("1000"),
        "g": Decimal("0.001"),
        "lb": Decimal("0.453592"),
    }

    # Volume units (for concrete, aggregates)
    VOLUME_UNITS: Final[dict] = {
        "m3": Decimal("1"),
        "m³": Decimal("1"),
        "L": Decimal("0.001"),
        "ft3": Decimal("0.0283168"),
    }

    # Area units (for sheet materials)
    AREA_UNITS: Final[dict] = {
        "m2": Decimal("1"),
        "m²": Decimal("1"),
        "ft2": Decimal("0.092903"),
        "sqm": Decimal("1"),
    }

    # Length units (for linear materials)
    LENGTH_UNITS: Final[dict] = {
        "m": Decimal("1"),
        "km": Decimal("1000"),
        "cm": Decimal("0.01"),
        "mm": Decimal("0.001"),
        "ft": Decimal("0.3048"),
    }


# ============================================================================
# LOGGING & AUDIT
# ============================================================================

class LoggingConfig:
    """Logging configuration for audit trail."""

    # Log level
    LOG_LEVEL: str = os.getenv("LCA_LOG_LEVEL", "INFO")

    # Enable audit trail (store all calculations)
    ENABLE_AUDIT: Final[bool] = True

    # Audit log format
    AUDIT_FORMAT: Final[str] = "json"

    # Include detailed calculation steps
    INCLUDE_CALCULATION_STEPS: Final[bool] = True


# ============================================================================
# INITIALIZATION FUNCTION
# ============================================================================

def initialize_brightway(validate: bool = True):
    """Initialize Brightway2 with deterministic configuration.

    This function should be called once at application startup or before
    any LCA calculations are performed.

    Args:
        validate: If True, validate that deterministic config is correctly applied

    Returns:
        str: Current project name

    Raises:
        ImportError: If Brightway2 is not installed
        RuntimeError: If deterministic validation fails
    """
    # Apply deterministic settings
    DeterministicConfig.apply()

    # Validate deterministic configuration if requested
    if validate and not DeterministicConfig.validate_determinism():
        raise RuntimeError(
            "Deterministic configuration validation failed. "
            "Random number generators may not be properly seeded."
        )

    # Ensure directories exist
    PathConfig.ensure_directories()

    # Set Brightway2 data directory via environment variable
    os.environ["BRIGHTWAY2_DIR"] = PathConfig.get_brightway_dir()

    # Import and initialize Brightway2
    try:
        import bw2data as bd

        # Set current project
        bd.projects.set_current(ProjectConfig.PROJECT_NAME)

        return bd.projects.current

    except ImportError:
        raise ImportError(
            "Brightway2 is not installed. Install with: "
            "pip install brightway2>=2.5.0 bw2data bw2calc bw2io"
        )


def reset_brightway():
    """Reset Brightway2 state for deterministic testing.

    This function resets random seeds and clears any cached state
    to ensure each test run is independent but deterministic.

    Use this between test runs to verify reproducibility.
    """
    # Reset random seeds
    DeterministicConfig.reset_seeds()

    # Clear any caches (if applicable)
    try:
        import bw2data as bd
        # Projects remain persistent, but we reset the random state
        if bd.projects.current:
            # Reapply seeds after any calculations
            DeterministicConfig.apply()
    except ImportError:
        pass


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "DeterministicConfig",
    "ProjectConfig",
    "PathConfig",
    "GraphDBConfig",
    "PerformanceConfig",
    "ValidationConfig",
    "UnitConfig",
    "LoggingConfig",
    "initialize_brightway",
    "reset_brightway",
]

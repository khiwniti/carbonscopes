"""Deterministic configuration for Brightway2 calculations.

Ensures calculations are reproducible by:
- Setting decimal precision
- Disabling Monte Carlo uncertainty
- Using a fixed random seed
"""

from decimal import getcontext

# Set high precision for Decimal operations
getcontext().prec = 28


class DeterministicConfig:
    """Configuration constants for deterministic mode."""

    MONTE_CARLO_ITERATIONS = 0  # Disable Monte Carlo
    USE_STATIC_LCA = True
    RANDOM_SEED = 42
    USE_DECIMAL = True

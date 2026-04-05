"""Brightway2 engine initialization utilities.

Provides a function to set up the Brightway2 project environment.
"""

import brightway2 as bw


def init_project(project_name: str = "CarbonBIM-Thailand"):
    """Initialize a Brightway2 project.

    Args:
        project_name: Name of the Brightway project.
    """
    # Ensure deterministic config is applied before any calculations
    from .determinism import DeterministicConfig

    # Set random seed for any stochastic aspects (should be disabled)
    import random

    random.seed(DeterministicConfig.RANDOM_SEED)
    # Create or switch to the project
    bw.projects.set_current(project_name)
    return bw.projects.current

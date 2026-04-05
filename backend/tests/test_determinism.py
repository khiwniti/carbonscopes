import pytest
from core.carbon.brightway.determinism import DeterministicConfig


def test_deterministic_config_values():
    assert DeterministicConfig.MONTE_CARLO_ITERATIONS == 0
    assert DeterministicConfig.USE_STATIC_LCA is True
    assert DeterministicConfig.RANDOM_SEED == 42
    assert DeterministicConfig.USE_DECIMAL is True

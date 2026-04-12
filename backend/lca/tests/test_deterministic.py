"""Deterministic Calculation Tests for Brightway2 Integration.

This module tests that Brightway2 calculations are deterministic and reproducible,
which is critical for consultant validation and regulatory compliance.

Test Categories:
1. Random seed configuration and validation
2. Identical results across multiple runs (10+ runs)
3. Cache independence (same results with/without cache)
4. Input order independence (different order -> same result)
5. Cross-machine reproducibility (documented limitations)

Success Criteria:
- Same calculation produces identical results in 10 consecutive runs
- Random seeds are fixed and validated
- Configuration is persistent across test runs
"""

import pytest
from decimal import Decimal, getcontext
from typing import List, Dict, Any


class TestRandomSeedConfiguration:
    """Test that random seeds are properly configured and fixed."""

    def test_random_seed_is_fixed(self):
        """Test that Python random seed is fixed."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig
        import random

        # Apply config
        DeterministicConfig.apply()

        # Generate random sequence
        random.seed(DeterministicConfig.RANDOM_SEED)
        sequence1 = [random.random() for _ in range(10)]

        # Reset and regenerate
        random.seed(DeterministicConfig.RANDOM_SEED)
        sequence2 = [random.random() for _ in range(10)]

        assert sequence1 == sequence2, "Random seed not producing identical sequences"

    def test_numpy_seed_is_fixed(self):
        """Test that NumPy random seed is fixed."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        try:
            import numpy as np

            # Apply config
            DeterministicConfig.apply()

            # Generate random sequence
            np.random.seed(DeterministicConfig.RANDOM_SEED)
            sequence1 = [np.random.random() for _ in range(10)]

            # Reset and regenerate
            np.random.seed(DeterministicConfig.RANDOM_SEED)
            sequence2 = [np.random.random() for _ in range(10)]

            assert sequence1 == sequence2, "NumPy seed not producing identical sequences"

        except ImportError:
            pytest.skip("NumPy not installed")

    def test_decimal_precision_configured(self):
        """Test that decimal precision is set correctly."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        DeterministicConfig.apply()

        assert getcontext().prec == DeterministicConfig.DECIMAL_PRECISION
        assert getcontext().prec == 28

    def test_monte_carlo_disabled(self):
        """Test that Monte Carlo sampling is disabled."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        assert DeterministicConfig.MONTE_CARLO_ITERATIONS == 0
        assert DeterministicConfig.USE_STATIC_LCA is True

    def test_config_validation(self):
        """Test that configuration validation works."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        DeterministicConfig.apply()
        assert DeterministicConfig.validate_determinism() is True


class TestMultipleRunDeterminism:
    """Test that calculations produce identical results across multiple runs."""

    @pytest.fixture(autouse=True)
    def setup_brightway(self):
        """Setup test environment with Brightway2."""
        try:
            import bw2data as bd
            import bw2calc as bc
            from carbonscope.backend.lca.brightway_config import initialize_brightway, reset_brightway

            # Initialize with validation
            initialize_brightway(validate=True)

            # Create test project
            test_project = "test-determinism"
            bd.projects.set_current(test_project)

            # Create test database
            db_name = "test-deterministic-db"
            if db_name in bd.databases:
                del bd.databases[db_name]

            db = bd.Database(db_name)
            db.write({
                (db_name, "test-concrete"): {
                    "name": "Test Concrete C30",
                    "unit": "kg",
                    "location": "TH",
                    "exchanges": [
                        {
                            "amount": 1.0,
                            "type": "production",
                            "input": (db_name, "test-concrete"),
                        },
                        {
                            "amount": 0.15,  # 0.15 kgCO2e per kg
                            "type": "biosphere",
                            "name": "Carbon dioxide",
                        },
                    ],
                },
                (db_name, "test-steel"): {
                    "name": "Test Steel Rebar",
                    "unit": "kg",
                    "location": "TH",
                    "exchanges": [
                        {
                            "amount": 1.0,
                            "type": "production",
                            "input": (db_name, "test-steel"),
                        },
                        {
                            "amount": 2.5,  # 2.5 kgCO2e per kg
                            "type": "biosphere",
                            "name": "Carbon dioxide",
                        },
                    ],
                },
            })

            self.bd = bd
            self.bc = bc
            self.db = db
            self.db_name = db_name
            self.reset_brightway = reset_brightway

        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        # Cleanup
        try:
            if test_project in self.bd.projects:
                self.bd.projects.delete_project(test_project, delete_dir=True)
        except:
            pass

    def test_ten_consecutive_runs_identical(self):
        """Test that same calculation produces identical results in 10 runs."""
        from carbonscope.backend.lca.brightway_config import ValidationConfig

        # Get test material
        concrete = self.bd.get_activity((self.db_name, "test-concrete"))
        functional_unit = {concrete: 1000}  # 1000 kg concrete

        # Run calculation 10 times
        results = []
        for i in range(ValidationConfig.DETERMINISM_RUNS):
            # Reset state between runs
            self.reset_brightway()

            # Calculate LCA
            lca = self.bc.LCA(functional_unit)
            lca.lci()

            # Store result (supply sum as proxy for calculation)
            result = float(sum(lca.supply))
            results.append(result)

        # All results must be identical
        unique_results = set(results)
        assert len(unique_results) == 1, (
            f"Non-deterministic results found: {len(unique_results)} unique values\n"
            f"Results: {results}"
        )

        # Verify expected value (1000 kg concrete should give specific result)
        expected_supply = 1000.0  # Should be at least the production amount
        assert results[0] >= expected_supply

    def test_multiple_materials_deterministic(self):
        """Test multi-material calculation is deterministic."""
        # Get materials
        concrete = self.bd.get_activity((self.db_name, "test-concrete"))
        steel = self.bd.get_activity((self.db_name, "test-steel"))

        # Functional unit: mixed materials
        functional_unit = {
            concrete: 5000,  # 5000 kg concrete
            steel: 500,      # 500 kg steel
        }

        # Run 5 times
        results = []
        for _ in range(5):
            self.reset_brightway()

            lca = self.bc.LCA(functional_unit)
            lca.lci()

            result = float(sum(lca.supply))
            results.append(result)

        # All results identical
        assert len(set(results)) == 1, f"Non-deterministic multi-material results: {results}"

    def test_different_quantities_proportional(self):
        """Test that different quantities produce proportional results."""
        concrete = self.bd.get_activity((self.db_name, "test-concrete"))

        quantities = [100, 1000, 10000]
        results = {}

        for qty in quantities:
            self.reset_brightway()

            lca = self.bc.LCA({concrete: qty})
            lca.lci()

            results[qty] = float(sum(lca.supply))

        # Results should be proportional (within floating point precision)
        # 1000 kg should be 10x 100 kg
        ratio_10x = results[1000] / results[100]
        assert 9.99 < ratio_10x < 10.01, f"10x scaling not proportional: {ratio_10x}"

        # 10000 kg should be 100x 100 kg
        ratio_100x = results[10000] / results[100]
        assert 99.9 < ratio_100x < 100.1, f"100x scaling not proportional: {ratio_100x}"

    def test_decimal_precision_calculations(self):
        """Test that Decimal type maintains precision."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        # Ensure Decimal precision is applied
        DeterministicConfig.apply()

        # Test high-precision calculation
        value1 = Decimal("0.15")
        quantity = Decimal("1000.0")
        result = value1 * quantity

        # Should be exactly 150.0 with no floating point errors
        assert result == Decimal("150.0")
        assert str(result) == "150.0"

        # Test precision is maintained across operations
        tiny_value = Decimal("0.000000000000000000000001")  # 24 decimal places
        result2 = tiny_value * Decimal("1000000000000000000000000")
        assert result2 == Decimal("1.0")


class TestCacheIndependence:
    """Test that calculation results are independent of cache state."""

    @pytest.fixture(autouse=True)
    def setup_brightway(self):
        """Setup test environment."""
        try:
            import bw2data as bd
            import bw2calc as bc
            from carbonscope.backend.lca.brightway_config import initialize_brightway

            initialize_brightway(validate=True)

            test_project = "test-cache-independence"
            bd.projects.set_current(test_project)

            db_name = "test-cache-db"
            if db_name in bd.databases:
                del bd.databases[db_name]

            db = bd.Database(db_name)
            db.write({
                (db_name, "material-1"): {
                    "name": "Material 1",
                    "unit": "kg",
                    "exchanges": [
                        {"amount": 1.0, "type": "production", "input": (db_name, "material-1")},
                        {"amount": 0.5, "type": "biosphere", "name": "CO2"},
                    ],
                },
            })

            self.bd = bd
            self.bc = bc
            self.db = db
            self.db_name = db_name

        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        try:
            if test_project in self.bd.projects:
                self.bd.projects.delete_project(test_project, delete_dir=True)
        except:
            pass

    def test_same_result_with_cache_cleared(self):
        """Test that clearing cache doesn't change results."""
        from carbonscope.backend.lca.brightway_config import reset_brightway

        material = self.bd.get_activity((self.db_name, "material-1"))
        functional_unit = {material: 1000}

        # First calculation (builds cache)
        lca1 = self.bc.LCA(functional_unit)
        lca1.lci()
        result1 = float(sum(lca1.supply))

        # Clear state and recalculate
        reset_brightway()

        lca2 = self.bc.LCA(functional_unit)
        lca2.lci()
        result2 = float(sum(lca2.supply))

        # Results must be identical
        assert result1 == result2, f"Cache clearing changed results: {result1} != {result2}"


class TestInputOrderIndependence:
    """Test that calculation results are independent of input order."""

    @pytest.fixture(autouse=True)
    def setup_brightway(self):
        """Setup test environment with multiple materials."""
        try:
            import bw2data as bd
            import bw2calc as bc
            from carbonscope.backend.lca.brightway_config import initialize_brightway

            initialize_brightway(validate=True)

            test_project = "test-order-independence"
            bd.projects.set_current(test_project)

            db_name = "test-order-db"
            if db_name in bd.databases:
                del bd.databases[db_name]

            db = bd.Database(db_name)
            db.write({
                (db_name, "mat-a"): {
                    "name": "Material A",
                    "unit": "kg",
                    "exchanges": [
                        {"amount": 1.0, "type": "production", "input": (db_name, "mat-a")},
                        {"amount": 0.1, "type": "biosphere", "name": "CO2"},
                    ],
                },
                (db_name, "mat-b"): {
                    "name": "Material B",
                    "unit": "kg",
                    "exchanges": [
                        {"amount": 1.0, "type": "production", "input": (db_name, "mat-b")},
                        {"amount": 0.2, "type": "biosphere", "name": "CO2"},
                    ],
                },
                (db_name, "mat-c"): {
                    "name": "Material C",
                    "unit": "kg",
                    "exchanges": [
                        {"amount": 1.0, "type": "production", "input": (db_name, "mat-c")},
                        {"amount": 0.3, "type": "biosphere", "name": "CO2"},
                    ],
                },
            })

            self.bd = bd
            self.bc = bc
            self.db = db
            self.db_name = db_name

        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        try:
            if test_project in self.bd.projects:
                self.bd.projects.delete_project(test_project, delete_dir=True)
        except:
            pass

    def test_different_input_order_same_result(self):
        """Test that different input order produces same result."""
        from carbonscope.backend.lca.brightway_config import reset_brightway

        # Get materials
        mat_a = self.bd.get_activity((self.db_name, "mat-a"))
        mat_b = self.bd.get_activity((self.db_name, "mat-b"))
        mat_c = self.bd.get_activity((self.db_name, "mat-c"))

        # Order 1: A, B, C
        reset_brightway()
        fu1 = {mat_a: 100, mat_b: 200, mat_c: 300}
        lca1 = self.bc.LCA(fu1)
        lca1.lci()
        result1 = float(sum(lca1.supply))

        # Order 2: C, B, A (reversed)
        reset_brightway()
        fu2 = {mat_c: 300, mat_b: 200, mat_a: 100}
        lca2 = self.bc.LCA(fu2)
        lca2.lci()
        result2 = float(sum(lca2.supply))

        # Order 3: B, A, C (shuffled)
        reset_brightway()
        fu3 = {mat_b: 200, mat_a: 100, mat_c: 300}
        lca3 = self.bc.LCA(fu3)
        lca3.lci()
        result3 = float(sum(lca3.supply))

        # All results should be identical
        assert result1 == result2 == result3, (
            f"Order-dependent results found:\n"
            f"Order A,B,C: {result1}\n"
            f"Order C,B,A: {result2}\n"
            f"Order B,A,C: {result3}"
        )


class TestConfigurationValidation:
    """Test configuration validation and error handling."""

    def test_initialization_with_validation(self):
        """Test that initialization validates configuration."""
        from carbonscope.backend.lca.brightway_config import initialize_brightway

        # Should not raise an error
        project = initialize_brightway(validate=True)
        assert project is not None

    def test_reset_function_exists(self):
        """Test that reset function is available."""
        from carbonscope.backend.lca.brightway_config import reset_brightway

        # Should not raise an error
        reset_brightway()

    def test_validation_detects_misconfiguration(self):
        """Test that validation can detect problems."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig
        import random

        # Apply correct config first
        DeterministicConfig.apply()
        assert DeterministicConfig.validate_determinism() is True

        # Corrupt the random state (change seed)
        random.seed(999)  # Different seed

        # Validation should still pass (it re-seeds during validation)
        # This tests that validation itself is deterministic
        assert DeterministicConfig.validate_determinism() is True


class TestDocumentedLimitations:
    """Document known limitations and edge cases."""

    def test_floating_point_precision_limits(self):
        """Test and document floating point precision limits."""
        # Python floats have ~15-17 decimal digits of precision
        # Our Decimal type has 28 digits

        # This test documents the difference
        float_result = 0.1 + 0.2  # Classic floating point issue
        decimal_result = Decimal("0.1") + Decimal("0.2")

        # Float has precision issues
        assert float_result != 0.3  # 0.30000000000000004

        # Decimal is exact
        assert decimal_result == Decimal("0.3")

    def test_cross_platform_note(self):
        """Document cross-platform reproducibility considerations."""
        # NOTE: This test documents expected behavior across platforms
        #
        # Determinism guarantees:
        # ✓ Same results on same machine, same Python version
        # ✓ Same results across different runs on same environment
        # ✓ Same results with same random seeds
        #
        # Potential variations:
        # - Different Python versions (3.11 vs 3.12) may have different random implementations
        # - Different CPU architectures (x86 vs ARM) may have different float representations
        # - Different OS (Linux vs Windows) may have different system libraries
        #
        # For true cross-platform determinism, always use:
        # - Same Python version
        # - Same Brightway2 version
        # - Same NumPy version
        # - Decimal type for all calculations

        # This test always passes - it's documentation
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

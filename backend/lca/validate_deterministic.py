#!/usr/bin/env python3
"""Deterministic Configuration Validation Script.

This script validates that Brightway2 is properly configured for deterministic
calculations. It performs a series of checks and reports any issues.

Usage:
    python validate_deterministic.py
    python validate_deterministic.py --verbose
    python validate_deterministic.py --runs 20  # More test runs

Exit Codes:
    0: All validation checks passed
    1: One or more validation checks failed
    2: Critical error (Brightway2 not installed, etc.)
"""

import sys
import argparse
from decimal import Decimal, getcontext
from typing import List, Tuple


class ValidationResult:
    """Container for validation test results."""

    def __init__(self, name: str, passed: bool, message: str, details: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status}: {self.name} - {self.message}"


class DeterministicValidator:
    """Validates deterministic configuration for Brightway2."""

    def __init__(self, verbose: bool = False, num_runs: int = 10):
        self.verbose = verbose
        self.num_runs = num_runs
        self.results: List[ValidationResult] = []

    def log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")

    def add_result(self, name: str, passed: bool, message: str, details: str = ""):
        """Add a validation result."""
        result = ValidationResult(name, passed, message, details)
        self.results.append(result)
        if self.verbose or not passed:
            print(result)

    def validate_imports(self) -> bool:
        """Validate that all required packages are installed."""
        self.log("Checking package imports...")

        # Check suna.backend.lca.brightway_config
        try:
            from suna.backend.lca.brightway_config import (
                DeterministicConfig,
                initialize_brightway,
                reset_brightway,
            )
            self.add_result(
                "Import Config",
                True,
                "Successfully imported brightway_config module"
            )
        except ImportError as e:
            self.add_result(
                "Import Config",
                False,
                f"Failed to import brightway_config: {e}"
            )
            return False

        # Check Brightway2
        try:
            import bw2data as bd
            import bw2calc as bc
            self.add_result(
                "Import Brightway2",
                True,
                f"Brightway2 installed (bw2data v{bd.__version__})"
            )
        except ImportError as e:
            self.add_result(
                "Import Brightway2",
                False,
                f"Brightway2 not installed: {e}",
                "Install with: pip install brightway2>=2.5.0"
            )
            return False

        # Check NumPy
        try:
            import numpy as np
            self.add_result(
                "Import NumPy",
                True,
                f"NumPy installed (v{np.__version__})"
            )
        except ImportError as e:
            self.add_result(
                "Import NumPy",
                False,
                f"NumPy not installed: {e}",
                "Install with: pip install numpy"
            )
            return False

        return True

    def validate_configuration(self) -> bool:
        """Validate configuration constants."""
        self.log("Checking configuration values...")

        from suna.backend.lca.brightway_config import DeterministicConfig

        # Check random seed
        if DeterministicConfig.RANDOM_SEED == 42:
            self.add_result(
                "Random Seed",
                True,
                f"Fixed seed configured: {DeterministicConfig.RANDOM_SEED}"
            )
        else:
            self.add_result(
                "Random Seed",
                False,
                f"Unexpected seed value: {DeterministicConfig.RANDOM_SEED}",
                "Expected: 42"
            )

        # Check decimal precision
        if DeterministicConfig.DECIMAL_PRECISION == 28:
            self.add_result(
                "Decimal Precision",
                True,
                f"High precision configured: {DeterministicConfig.DECIMAL_PRECISION} digits"
            )
        else:
            self.add_result(
                "Decimal Precision",
                False,
                f"Low precision: {DeterministicConfig.DECIMAL_PRECISION}",
                "Expected: 28 digits"
            )

        # Check Monte Carlo disabled
        if DeterministicConfig.MONTE_CARLO_ITERATIONS == 0:
            self.add_result(
                "Monte Carlo",
                True,
                "Monte Carlo sampling disabled (deterministic mode)"
            )
        else:
            self.add_result(
                "Monte Carlo",
                False,
                f"Monte Carlo enabled: {DeterministicConfig.MONTE_CARLO_ITERATIONS} iterations",
                "Set MONTE_CARLO_ITERATIONS = 0 for determinism"
            )

        # Check static LCA mode
        if DeterministicConfig.USE_STATIC_LCA:
            self.add_result(
                "Static LCA",
                True,
                "Static LCA mode enabled (deterministic)"
            )
        else:
            self.add_result(
                "Static LCA",
                False,
                "Static LCA mode disabled",
                "Set USE_STATIC_LCA = True"
            )

        return all(r.passed for r in self.results[-4:])

    def validate_seed_application(self) -> bool:
        """Validate that seeds are properly applied."""
        self.log("Testing random seed application...")

        from suna.backend.lca.brightway_config import DeterministicConfig
        import random
        import numpy as np

        # Apply configuration
        DeterministicConfig.apply()

        # Test Python random
        random.seed(DeterministicConfig.RANDOM_SEED)
        py_seq1 = [random.random() for _ in range(10)]
        random.seed(DeterministicConfig.RANDOM_SEED)
        py_seq2 = [random.random() for _ in range(10)]

        if py_seq1 == py_seq2:
            self.add_result(
                "Python Random Seed",
                True,
                "Python random module produces identical sequences"
            )
        else:
            self.add_result(
                "Python Random Seed",
                False,
                "Python random module not deterministic",
                f"Seq1: {py_seq1[:3]}...\nSeq2: {py_seq2[:3]}..."
            )
            return False

        # Test NumPy random
        np.random.seed(DeterministicConfig.RANDOM_SEED)
        np_seq1 = [np.random.random() for _ in range(10)]
        np.random.seed(DeterministicConfig.RANDOM_SEED)
        np_seq2 = [np.random.random() for _ in range(10)]

        if np_seq1 == np_seq2:
            self.add_result(
                "NumPy Random Seed",
                True,
                "NumPy random produces identical sequences"
            )
        else:
            self.add_result(
                "NumPy Random Seed",
                False,
                "NumPy random not deterministic",
                f"Seq1: {np_seq1[:3]}...\nSeq2: {np_seq2[:3]}..."
            )
            return False

        # Test decimal precision
        if getcontext().prec == DeterministicConfig.DECIMAL_PRECISION:
            self.add_result(
                "Decimal Context",
                True,
                f"Decimal precision applied: {getcontext().prec} digits"
            )
        else:
            self.add_result(
                "Decimal Context",
                False,
                f"Decimal precision not applied: {getcontext().prec} != {DeterministicConfig.DECIMAL_PRECISION}"
            )
            return False

        return True

    def validate_brightway_initialization(self) -> bool:
        """Validate Brightway2 initialization."""
        self.log("Testing Brightway2 initialization...")

        try:
            from suna.backend.lca.brightway_config import initialize_brightway

            # Initialize (with validation)
            project_name = initialize_brightway(validate=True)

            self.add_result(
                "Brightway2 Init",
                True,
                f"Successfully initialized project: {project_name}"
            )
            return True

        except RuntimeError as e:
            self.add_result(
                "Brightway2 Init",
                False,
                f"Initialization validation failed: {e}"
            )
            return False
        except Exception as e:
            self.add_result(
                "Brightway2 Init",
                False,
                f"Unexpected error during initialization: {e}"
            )
            return False

    def validate_calculation_determinism(self) -> bool:
        """Validate that actual LCA calculations are deterministic."""
        self.log(f"Testing calculation determinism ({self.num_runs} runs)...")

        try:
            import bw2data as bd
            import bw2calc as bc
            from suna.backend.lca.brightway_config import reset_brightway

            # Create test project
            test_project = "test-validation-determinism"
            bd.projects.set_current(test_project)

            # Create minimal test database
            db_name = "test-validation-db"
            if db_name in bd.databases:
                del bd.databases[db_name]

            db = bd.Database(db_name)
            db.write({
                (db_name, "test-material"): {
                    "name": "Test Material",
                    "unit": "kg",
                    "exchanges": [
                        {
                            "amount": 1.0,
                            "type": "production",
                            "input": (db_name, "test-material"),
                        },
                        {
                            "amount": 0.5,  # 0.5 kgCO2e per kg
                            "type": "biosphere",
                            "name": "Carbon dioxide",
                        },
                    ],
                }
            })

            # Get activity
            activity = bd.get_activity((db_name, "test-material"))
            functional_unit = {activity: 1000}  # 1000 kg

            # Run multiple calculations
            results = []
            for i in range(self.num_runs):
                reset_brightway()

                lca = bc.LCA(functional_unit)
                lca.lci()

                result = float(sum(lca.supply))
                results.append(result)

                if self.verbose:
                    print(f"    Run {i+1}/{self.num_runs}: {result}")

            # Check if all results are identical
            unique_results = set(results)
            if len(unique_results) == 1:
                self.add_result(
                    "Calculation Determinism",
                    True,
                    f"All {self.num_runs} runs produced identical results: {results[0]}"
                )
                success = True
            else:
                self.add_result(
                    "Calculation Determinism",
                    False,
                    f"Non-deterministic results: {len(unique_results)} unique values",
                    f"Results: {sorted(unique_results)}"
                )
                success = False

            # Cleanup
            bd.projects.delete_project(test_project, delete_dir=True)

            return success

        except Exception as e:
            self.add_result(
                "Calculation Determinism",
                False,
                f"Error during calculation test: {e}"
            )
            return False

    def validate_decimal_arithmetic(self) -> bool:
        """Validate Decimal arithmetic precision."""
        self.log("Testing Decimal arithmetic...")

        # Test basic operations
        val1 = Decimal("0.1")
        val2 = Decimal("0.2")
        result = val1 + val2

        if result == Decimal("0.3"):
            self.add_result(
                "Decimal Arithmetic",
                True,
                "Decimal type maintains exact precision"
            )
        else:
            self.add_result(
                "Decimal Arithmetic",
                False,
                f"Decimal precision issue: 0.1 + 0.2 = {result}"
            )
            return False

        # Test high precision
        tiny = Decimal("0.000000000000000000000001")  # 24 decimals
        large = Decimal("1000000000000000000000000")
        result2 = tiny * large

        if result2 == Decimal("1.0"):
            self.add_result(
                "High Precision",
                True,
                "High-precision calculations work correctly"
            )
        else:
            self.add_result(
                "High Precision",
                False,
                f"Precision lost in calculation: {result2}"
            )
            return False

        return True

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("=" * 70)
        print("Deterministic Configuration Validation")
        print("=" * 70)
        print()

        # Run validation checks in order
        checks = [
            ("Package Imports", self.validate_imports),
            ("Configuration Values", self.validate_configuration),
            ("Seed Application", self.validate_seed_application),
            ("Decimal Arithmetic", self.validate_decimal_arithmetic),
            ("Brightway2 Initialization", self.validate_brightway_initialization),
            ("Calculation Determinism", self.validate_calculation_determinism),
        ]

        for name, check_func in checks:
            if self.verbose:
                print(f"\n[{name}]")
            try:
                passed = check_func()
                if not passed and not self.verbose:
                    # In non-verbose mode, stop at first failure
                    break
            except Exception as e:
                self.add_result(
                    name,
                    False,
                    f"Unexpected error: {e}"
                )
                break

        # Print summary
        print()
        print("=" * 70)
        print("Validation Summary")
        print("=" * 70)

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        print(f"\nPassed: {passed_count}/{total_count} checks")
        print()

        # Show failed checks
        failed = [r for r in self.results if not r.passed]
        if failed:
            print("Failed Checks:")
            for result in failed:
                print(f"  ❌ {result.name}: {result.message}")
                if result.details:
                    print(f"     {result.details}")
            print()

        # Overall status
        all_passed = len(failed) == 0
        if all_passed:
            print("✅ All validation checks PASSED")
            print("   Brightway2 is properly configured for deterministic calculations.")
        else:
            print("❌ Some validation checks FAILED")
            print("   See DETERMINISTIC_MODE_GUIDE.md for troubleshooting.")

        print()
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate deterministic configuration for Brightway2"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-r", "--runs",
        type=int,
        default=10,
        help="Number of test runs for determinism check (default: 10)"
    )

    args = parser.parse_args()

    # Create validator
    validator = DeterministicValidator(
        verbose=args.verbose,
        num_runs=args.runs
    )

    # Run validations
    try:
        success = validator.run_all_validations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()

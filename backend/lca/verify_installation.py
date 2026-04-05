#!/usr/bin/env python3
"""Brightway2 Installation Verification Script.

This script verifies that Brightway2 is properly installed and configured
for the SUNA BIM Agent LCA integration.

Usage:
    python3 verify_installation.py
    # or
    python3 suna/backend/lca/verify_installation.py
"""

import sys
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(label: str, status: bool, details: str = ""):
    """Print a check result."""
    icon = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    color = "\033[92m" if status else "\033[91m"  # Green or Red
    reset = "\033[0m"

    print(f"{color}{icon} {label}: {status_text}{reset}")
    if details:
        print(f"   {details}")


def check_python_version() -> bool:
    """Check Python version is 3.11+."""
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 11
    details = f"Python {version.major}.{version.minor}.{version.micro}"
    print_check("Python Version (≥3.11)", is_ok, details)
    return is_ok


def check_brightway_imports() -> tuple[bool, list]:
    """Check if Brightway2 packages can be imported."""
    packages = {
        "bw2data": None,
        "bw2calc": None,
        "bw2io": None,
        "brightway2": None,
    }

    for package in packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            packages[package] = version
        except ImportError:
            packages[package] = None

    all_ok = all(v is not None for v in packages.values())

    for pkg, version in packages.items():
        if version:
            print_check(f"Import {pkg}", True, f"Version: {version}")
        else:
            print_check(f"Import {pkg}", False, "Not installed")

    return all_ok, packages


def check_config_module() -> bool:
    """Check if brightway_config can be imported."""
    try:
        from suna.backend.lca.brightway_config import (
            DeterministicConfig,
            ProjectConfig,
            initialize_brightway,
        )

        print_check("Configuration Module", True, "Successfully imported")

        # Check key config values
        print(f"   - Project Name: {ProjectConfig.PROJECT_NAME}")
        print(f"   - Database Name: {ProjectConfig.DATABASE_NAME}")
        print(f"   - Random Seed: {DeterministicConfig.RANDOM_SEED}")
        print(f"   - Decimal Precision: {DeterministicConfig.DECIMAL_PRECISION}")

        return True
    except ImportError as e:
        print_check("Configuration Module", False, f"Import error: {e}")
        return False


def check_data_directory() -> bool:
    """Check if data directory exists."""
    try:
        from suna.backend.lca.brightway_config import PathConfig

        PathConfig.ensure_directories()

        data_dir_exists = PathConfig.DATA_DIR.exists()
        bw2_dir_exists = PathConfig.BRIGHTWAY_DIR.exists()

        if data_dir_exists and bw2_dir_exists:
            print_check("Data Directories", True)
            print(f"   - Data dir: {PathConfig.DATA_DIR}")
            print(f"   - BW2 dir: {PathConfig.BRIGHTWAY_DIR}")
            return True
        else:
            print_check("Data Directories", False, "Directories not created")
            return False
    except Exception as e:
        print_check("Data Directories", False, f"Error: {e}")
        return False


def check_brightway_project() -> bool:
    """Check if Brightway2 project can be initialized."""
    try:
        from suna.backend.lca.brightway_config import initialize_brightway

        project = initialize_brightway()

        print_check("Project Initialization", True, f"Project: {project}")

        # Check if project exists
        import bw2data as bd

        current = bd.projects.current
        print(f"   - Current project: {current}")

        return True
    except Exception as e:
        print_check("Project Initialization", False, f"Error: {e}")
        return False


def check_determinism() -> bool:
    """Check if deterministic config can be applied."""
    try:
        from suna.backend.lca.brightway_config import DeterministicConfig
        from decimal import getcontext

        # Apply config
        DeterministicConfig.apply()

        # Check precision
        precision = getcontext().prec
        precision_ok = precision == DeterministicConfig.DECIMAL_PRECISION

        if precision_ok:
            print_check("Deterministic Config", True, f"Precision: {precision}")
            return True
        else:
            print_check(
                "Deterministic Config",
                False,
                f"Precision {precision} != {DeterministicConfig.DECIMAL_PRECISION}",
            )
            return False
    except Exception as e:
        print_check("Deterministic Config", False, f"Error: {e}")
        return False


def check_basic_calculation() -> bool:
    """Check if a basic LCA calculation works."""
    try:
        import bw2data as bd
        import bw2calc as bc

        # Create test database
        db_name = "test-verify"
        if db_name in bd.databases:
            del bd.databases[db_name]

        db = bd.Database(db_name)
        db.write(
            {
                (db_name, "test-material"): {
                    "name": "Test Material",
                    "unit": "kg",
                    "exchanges": [
                        {
                            "amount": 1.0,
                            "type": "production",
                            "input": (db_name, "test-material"),
                        },
                    ],
                }
            }
        )

        # Perform calculation
        activity = bd.get_activity((db_name, "test-material"))
        lca = bc.LCA({activity: 100})
        lca.lci()

        # Clean up
        del bd.databases[db_name]

        print_check("Basic LCA Calculation", True, "Simple calculation successful")
        return True
    except Exception as e:
        print_check("Basic LCA Calculation", False, f"Error: {e}")
        return False


def run_verification():
    """Run all verification checks."""
    print_header("BRIGHTWAY2 INSTALLATION VERIFICATION")
    print("SUNA BIM Agent - LCA Module")
    print()

    checks = []

    # Python version
    print_header("Python Environment")
    checks.append(check_python_version())

    # Brightway2 imports
    print_header("Brightway2 Packages")
    bw2_ok, packages = check_brightway_imports()
    checks.append(bw2_ok)

    # Configuration module
    print_header("SUNA LCA Configuration")
    checks.append(check_config_module())

    # Data directories
    print_header("Data Storage")
    checks.append(check_data_directory())

    # Only run these if Brightway2 is installed
    if bw2_ok:
        # Project initialization
        print_header("Brightway2 Project")
        checks.append(check_brightway_project())

        # Deterministic config
        print_header("Deterministic Configuration")
        checks.append(check_determinism())

        # Basic calculation
        print_header("LCA Calculation Test")
        checks.append(check_basic_calculation())
    else:
        print_header("Brightway2 Project")
        print_check(
            "Skipped",
            False,
            "Brightway2 not installed - run: uv pip install -r lca/requirements.txt",
        )
        checks.append(False)

    # Summary
    print_header("VERIFICATION SUMMARY")
    passed = sum(checks)
    total = len(checks)

    print(f"\nPassed: {passed}/{total} checks")

    if passed == total:
        print("\n✓ All checks passed! Brightway2 is ready to use.")
        print("\nNext steps:")
        print("  1. Load TGO data (Task #21)")
        print("  2. Integrate with API (Task #22)")
        print("  3. Validate accuracy (Task #23)")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  1. Install Brightway2: uv pip install -r lca/requirements.txt")
        print("  2. Check Python version: python3 --version (need 3.11+)")
        print("  3. Review installation guide: cat lca/INSTALL.md")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())

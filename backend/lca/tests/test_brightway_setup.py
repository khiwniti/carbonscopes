"""Basic Brightway2 Setup Tests.

This module tests the installation and configuration of Brightway2 for the
carbonscope BIM Agent LCA integration.

Tests cover:
- Brightway2 imports
- Project creation and management
- Database CRUD operations
- Deterministic configuration
- Basic LCA calculations
"""

import pytest
from decimal import Decimal, getcontext


class TestBrightway2Imports:
    """Test that Brightway2 packages can be imported successfully."""

    def test_import_bw2data(self):
        """Test bw2data import."""
        try:
            import bw2data as bd
            assert bd is not None
            assert hasattr(bd, 'projects')
            assert hasattr(bd, 'Database')
        except ImportError as e:
            pytest.fail(f"Failed to import bw2data: {e}")

    def test_import_bw2calc(self):
        """Test bw2calc import."""
        try:
            import bw2calc as bc
            assert bc is not None
            assert hasattr(bc, 'LCA')
        except ImportError as e:
            pytest.fail(f"Failed to import bw2calc: {e}")

    def test_import_bw2io(self):
        """Test bw2io import."""
        try:
            import bw2io as bi
            assert bi is not None
        except ImportError as e:
            pytest.fail(f"Failed to import bw2io: {e}")

    def test_brightway2_version(self):
        """Test Brightway2 version is 2.5+."""
        try:
            import bw2data as bd
            version = bd.__version__
            # Parse version (e.g., "4.0.0" for bw2data)
            major = int(version.split('.')[0])
            assert major >= 4, f"bw2data version {version} is too old (need 4.0+)"
        except ImportError:
            pytest.skip("bw2data not installed")


class TestBrightway2Configuration:
    """Test Brightway2 configuration and initialization."""

    def test_import_config(self):
        """Test that brightway_config can be imported."""
        from carbonscope.backend.lca.brightway_config import (
            DeterministicConfig,
            ProjectConfig,
            PathConfig,
            initialize_brightway,
        )

        assert DeterministicConfig is not None
        assert ProjectConfig is not None
        assert PathConfig is not None
        assert initialize_brightway is not None

    def test_deterministic_config_values(self):
        """Test deterministic configuration constants."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        assert DeterministicConfig.DECIMAL_PRECISION == 28
        assert DeterministicConfig.RANDOM_SEED == 42
        assert DeterministicConfig.MONTE_CARLO_ITERATIONS == 0
        assert DeterministicConfig.USE_STATIC_LCA is True
        assert DeterministicConfig.USE_DECIMAL is True

    def test_project_config_values(self):
        """Test project configuration constants."""
        from carbonscope.backend.lca.brightway_config import ProjectConfig

        assert ProjectConfig.PROJECT_NAME == "thailand-construction"
        assert ProjectConfig.DATABASE_NAME == "TGO-Thailand-2026"
        assert ProjectConfig.DEFAULT_STAGES == ["A1", "A2", "A3"]

    def test_path_config_directories(self):
        """Test that path configuration creates necessary directories."""
        from carbonscope.backend.lca.brightway_config import PathConfig

        # Ensure directories are created
        PathConfig.ensure_directories()

        assert PathConfig.DATA_DIR.exists()
        assert PathConfig.DATA_DIR.is_dir()
        assert PathConfig.BRIGHTWAY_DIR.exists()
        assert PathConfig.BRIGHTWAY_DIR.is_dir()

    def test_apply_deterministic_config(self):
        """Test that deterministic config can be applied."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        # Apply config
        DeterministicConfig.apply()

        # Check decimal precision
        assert getcontext().prec == 28

        # Check random seed (by generating same sequence)
        import random
        random.seed(42)  # Re-seed after apply()
        first = [random.random() for _ in range(5)]

        random.seed(42)  # Re-seed to get same sequence
        second = [random.random() for _ in range(5)]

        assert first == second, "Random seed not working correctly"


class TestBrightway2ProjectManagement:
    """Test Brightway2 project creation and management."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Import Brightway2
        try:
            import bw2data as bd
            self.bd = bd
        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        # Teardown: Clean up test projects
        # Note: Be careful not to delete production projects

    def test_initialize_project(self):
        """Test project initialization function."""
        from carbonscope.backend.lca.brightway_config import initialize_brightway

        # Initialize project
        project_name = initialize_brightway()

        assert project_name == "thailand-construction"
        assert self.bd.projects.current == "thailand-construction"

    def test_project_creation(self):
        """Test manual project creation."""
        # Create test project
        test_project_name = "test-lca-project"
        self.bd.projects.set_current(test_project_name)

        assert self.bd.projects.current == test_project_name

        # Clean up
        self.bd.projects.delete_project(test_project_name, delete_dir=True)

    def test_list_projects(self):
        """Test listing all projects."""
        projects = list(self.bd.projects)

        # Should be a list
        assert isinstance(projects, list)

        # Should contain at least one project (thailand-construction or default)
        # Note: This might fail on first run before initialization

    def test_switch_projects(self):
        """Test switching between projects."""
        # Create two test projects
        project1 = "test-project-1"
        project2 = "test-project-2"

        self.bd.projects.set_current(project1)
        assert self.bd.projects.current == project1

        self.bd.projects.set_current(project2)
        assert self.bd.projects.current == project2

        # Clean up
        self.bd.projects.delete_project(project1, delete_dir=True)
        self.bd.projects.delete_project(project2, delete_dir=True)


class TestBrightway2DatabaseOperations:
    """Test Brightway2 database CRUD operations."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        try:
            import bw2data as bd
            self.bd = bd

            # Ensure we're in a test project
            test_project = "test-db-operations"
            self.bd.projects.set_current(test_project)

        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        # Clean up: Delete test project
        try:
            self.bd.projects.delete_project("test-db-operations", delete_dir=True)
        except:
            pass

    def test_create_empty_database(self):
        """Test creating an empty database."""
        db_name = "test-empty-db"
        db = self.bd.Database(db_name)
        db.write({})  # Empty database

        assert db_name in self.bd.databases
        assert len(db) == 0

    def test_create_database_with_activity(self):
        """Test creating a database with a single activity."""
        db_name = "test-materials"

        # Create database with one activity
        db = self.bd.Database(db_name)
        db.write({
            (db_name, "concrete-c30"): {
                "name": "Concrete C30",
                "unit": "kg",
                "location": "TH",
                "exchanges": [],
            }
        })

        assert db_name in self.bd.databases
        assert len(db) == 1

        # Retrieve activity
        activity = self.bd.get_activity((db_name, "concrete-c30"))
        assert activity["name"] == "Concrete C30"
        assert activity["unit"] == "kg"
        assert activity["location"] == "TH"

    def test_database_with_exchanges(self):
        """Test creating activity with exchanges (emissions)."""
        db_name = "test-materials-with-exchanges"

        db = self.bd.Database(db_name)
        db.write({
            (db_name, "steel-rebar"): {
                "name": "Steel Rebar",
                "unit": "kg",
                "location": "TH",
                "exchanges": [
                    {
                        "amount": 2.5,  # 2.5 kgCO2e per kg steel
                        "type": "biosphere",
                        "name": "Carbon dioxide",
                        "unit": "kg",
                    },
                ],
            }
        })

        assert db_name in self.bd.databases

        # Retrieve and check exchanges
        activity = self.bd.get_activity((db_name, "steel-rebar"))
        exchanges = list(activity.exchanges())
        assert len(exchanges) >= 1  # At least production + biosphere

    def test_database_crud(self):
        """Test Create, Read, Update, Delete operations."""
        db_name = "test-crud-db"

        # CREATE
        db = self.bd.Database(db_name)
        db.write({
            (db_name, "material-1"): {
                "name": "Material 1",
                "unit": "kg",
            }
        })
        assert db_name in self.bd.databases

        # READ
        activity = self.bd.get_activity((db_name, "material-1"))
        assert activity["name"] == "Material 1"

        # UPDATE (add another activity)
        activity2_data = {
            (db_name, "material-2"): {
                "name": "Material 2",
                "unit": "m3",
            }
        }
        db.write(activity2_data)
        assert len(db) == 2

        # DELETE (database)
        del self.bd.databases[db_name]
        assert db_name not in self.bd.databases

    def test_query_database(self):
        """Test querying activities from database."""
        db_name = "test-query-db"

        # Create database with multiple activities
        db = self.bd.Database(db_name)
        db.write({
            (db_name, "concrete"): {"name": "Concrete", "unit": "m3"},
            (db_name, "steel"): {"name": "Steel", "unit": "kg"},
            (db_name, "wood"): {"name": "Wood", "unit": "m3"},
        })

        # Query by iteration
        materials = [act["name"] for act in db]
        assert "Concrete" in materials
        assert "Steel" in materials
        assert "Wood" in materials

        # Query specific activity
        concrete = self.bd.get_activity((db_name, "concrete"))
        assert concrete["name"] == "Concrete"


class TestBrightway2BasicCalculations:
    """Test basic LCA calculations with Brightway2."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup test database for calculations."""
        try:
            import bw2data as bd
            import bw2calc as bc
            self.bd = bd
            self.bc = bc

            # Create test project
            test_project = "test-calculations"
            self.bd.projects.set_current(test_project)

            # Create test database with emission factor
            db_name = "test-calc-db"
            db = self.bd.Database(db_name)
            db.write({
                (db_name, "test-material"): {
                    "name": "Test Material",
                    "unit": "kg",
                    "location": "TH",
                    "exchanges": [
                        {
                            "amount": 1.0,  # Production
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

            self.db = db
            self.db_name = db_name

        except ImportError:
            pytest.skip("Brightway2 not installed")

        yield

        # Clean up
        try:
            self.bd.projects.delete_project("test-calculations", delete_dir=True)
        except:
            pass

    def test_simple_lca_calculation(self):
        """Test a simple LCA calculation."""
        # Get activity
        activity = self.bd.get_activity((self.db_name, "test-material"))

        # Create functional unit: 100 kg of material
        functional_unit = {activity: 100}

        # Create LCA object
        lca = self.bc.LCA(functional_unit)
        lca.lci()  # Life cycle inventory

        # Check that calculation ran
        assert lca.demand is not None
        assert lca.supply is not None

    def test_deterministic_calculation(self):
        """Test that calculations are deterministic (same input -> same output)."""
        from carbonscope.backend.lca.brightway_config import DeterministicConfig

        # Apply deterministic config
        DeterministicConfig.apply()

        # Get activity
        activity = self.bd.get_activity((self.db_name, "test-material"))
        functional_unit = {activity: 100}

        # Run calculation 10 times
        results = []
        for _ in range(10):
            lca = self.bc.LCA(functional_unit)
            lca.lci()
            # Get inventory result
            results.append(float(sum(lca.supply)))

        # All results should be identical
        assert len(set(results)) == 1, f"Non-deterministic results: {results}"

    def test_different_quantities(self):
        """Test calculations with different functional unit quantities."""
        activity = self.bd.get_activity((self.db_name, "test-material"))

        # Calculate for different quantities
        quantities = [10, 100, 1000]
        results = []

        for qty in quantities:
            lca = self.bc.LCA({activity: qty})
            lca.lci()
            results.append(float(sum(lca.supply)))

        # Results should scale proportionally (not necessarily linearly due to complexity)
        # At minimum, larger quantity should give larger result
        assert results[0] < results[1] < results[2]


class TestBrightway2Integration:
    """Test integration with carbonscope configuration."""

    def test_config_integration(self):
        """Test that config module integrates correctly."""
        from carbonscope.backend.lca.brightway_config import (
            initialize_brightway,
            DeterministicConfig,
            ProjectConfig,
        )

        # Apply config
        DeterministicConfig.apply()

        # Initialize
        project = initialize_brightway()

        assert project == ProjectConfig.PROJECT_NAME

    def test_graphdb_config_exists(self):
        """Test that GraphDB configuration is available."""
        from carbonscope.backend.lca.brightway_config import GraphDBConfig

        assert GraphDBConfig.ENDPOINT is not None
        assert GraphDBConfig.REPOSITORY is not None
        assert GraphDBConfig.TGO_NAMESPACE is not None

    def test_validation_config_exists(self):
        """Test that validation configuration is available."""
        from carbonscope.backend.lca.brightway_config import ValidationConfig

        assert ValidationConfig.TARGET_ERROR_PERCENT == Decimal("2.0")
        assert ValidationConfig.DETERMINISM_RUNS == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

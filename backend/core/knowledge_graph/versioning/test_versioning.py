"""
Unit tests for TGO Named Graph Versioning System.

These tests validate the versioning logic without requiring a live GraphDB instance.
Integration tests that require GraphDB should be placed in tests/integration/.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Import from local module
from carbonscope.backend.core.knowledge_graph.versioning.version_manager import VersionManager


class TestVersionManager(unittest.TestCase):
    """Test cases for VersionManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock GraphDB client
        self.mock_client = Mock()
        self.vm = VersionManager(self.mock_client)

    def test_create_version_uri(self):
        """Test version URI creation."""
        # Test valid inputs
        uri = self.vm.create_version_uri(2024, 12)
        self.assertEqual(uri, "http://tgo.or.th/versions/2024-12")

        uri = self.vm.create_version_uri(2025, 1)
        self.assertEqual(uri, "http://tgo.or.th/versions/2025-01")

        uri = self.vm.create_version_uri(2026, 3)
        self.assertEqual(uri, "http://tgo.or.th/versions/2026-03")

    def test_create_version_uri_invalid_month(self):
        """Test version URI creation with invalid month."""
        with self.assertRaises(ValueError):
            self.vm.create_version_uri(2024, 0)

        with self.assertRaises(ValueError):
            self.vm.create_version_uri(2024, 13)

        with self.assertRaises(ValueError):
            self.vm.create_version_uri(2024, -1)

    def test_parse_version_uri(self):
        """Test version URI parsing."""
        year, month = self.vm.parse_version_uri("http://tgo.or.th/versions/2024-12")
        self.assertEqual(year, 2024)
        self.assertEqual(month, 12)

        year, month = self.vm.parse_version_uri("http://tgo.or.th/versions/2025-01")
        self.assertEqual(year, 2025)
        self.assertEqual(month, 1)

    def test_parse_version_uri_invalid(self):
        """Test version URI parsing with invalid URI."""
        with self.assertRaises(ValueError):
            self.vm.parse_version_uri("http://invalid.uri/versions/2024-12")

        with self.assertRaises(ValueError):
            self.vm.parse_version_uri("http://tgo.or.th/versions/invalid")

        with self.assertRaises(ValueError):
            self.vm.parse_version_uri("http://tgo.or.th/versions/2024-13")

    def test_get_current_version_uri(self):
        """Test getting current version URI."""
        uri = self.vm.get_current_version_uri()

        # Should be in format http://tgo.or.th/versions/YYYY-MM
        self.assertTrue(uri.startswith("http://tgo.or.th/versions/"))

        # Parse and verify it's the current month
        year, month = self.vm.parse_version_uri(uri)
        now = datetime.now()
        self.assertEqual(year, now.year)
        self.assertEqual(month, now.month)

    def test_normalize_version_uri_full_uri(self):
        """Test normalizing full URI."""
        uri = "http://tgo.or.th/versions/2024-12"
        normalized = self.vm._normalize_version_uri(uri)
        self.assertEqual(normalized, uri)

    def test_normalize_version_uri_short_format(self):
        """Test normalizing short format (YYYY-MM)."""
        normalized = self.vm._normalize_version_uri("2024-12")
        self.assertEqual(normalized, "http://tgo.or.th/versions/2024-12")

        normalized = self.vm._normalize_version_uri("2025-01")
        self.assertEqual(normalized, "http://tgo.or.th/versions/2025-01")

    def test_normalize_version_uri_invalid(self):
        """Test normalizing invalid format."""
        with self.assertRaises(ValueError):
            self.vm._normalize_version_uri("invalid")

        with self.assertRaises(ValueError):
            self.vm._normalize_version_uri("2024")

    def test_custom_base_uri(self):
        """Test using custom base URI."""
        custom_vm = VersionManager(
            self.mock_client,
            base_uri="http://custom.org/versions"
        )

        uri = custom_vm.create_version_uri(2024, 12)
        self.assertEqual(uri, "http://custom.org/versions/2024-12")

    def test_custom_staleness_threshold(self):
        """Test using custom staleness threshold."""
        custom_vm = VersionManager(
            self.mock_client,
            staleness_threshold_months=12
        )

        self.assertEqual(custom_vm.staleness_threshold_months, 12)

    @patch('carbonscope.backend.core.knowledge_graph.versioning.version_manager.datetime')
    def test_find_stale_factors_mock(self, mock_datetime):
        """Test finding stale factors with mocked GraphDB."""
        # Mock datetime
        mock_datetime.now.return_value = datetime(2026, 3, 22)
        mock_datetime.strptime = datetime.strptime

        # Mock GraphDB response
        self.mock_client.query.return_value = {
            'results': {
                'bindings': [
                    {
                        'material': {'value': 'http://tgo.or.th/materials/concrete-c30'},
                        'label': {'value': 'Concrete C30'},
                        'effectiveDate': {'value': '2024-01-15'},
                        'category': {'value': 'Concrete'}
                    }
                ]
            }
        }

        # Call method
        stale = self.vm.find_stale_factors(months=6)

        # Verify results
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]['label'], 'Concrete C30')
        self.assertEqual(stale[0]['category'], 'Concrete')
        self.assertGreater(stale[0]['ageInDays'], 400)

    def test_list_versions_mock(self):
        """Test listing versions with mocked GraphDB."""
        # Mock GraphDB response
        self.mock_client.query.return_value = {
            'results': {
                'bindings': [
                    {
                        'graph': {'value': 'http://tgo.or.th/versions/2024-12'},
                        'versionDate': {'value': '2024-12-01'},
                        'notes': {'value': 'December 2024 release'}
                    },
                    {
                        'graph': {'value': 'http://tgo.or.th/versions/2025-01'},
                        'versionDate': {'value': '2025-01-01'},
                        'notes': {'value': 'January 2025 release'}
                    }
                ]
            }
        }

        # Mock get_triple_count
        self.mock_client.get_triple_count.return_value = 1000

        # Mock _count_materials_in_version
        with patch.object(self.vm, '_count_materials_in_version', return_value=150):
            versions = self.vm.list_versions()

        # Verify results
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]['versionUri'], 'http://tgo.or.th/versions/2024-12')
        self.assertEqual(versions[0]['materialCount'], 150)
        self.assertEqual(versions[0]['tripleCount'], 1000)

    def test_compare_versions_structure(self):
        """Test version comparison returns correct structure."""
        # Mock the internal methods
        self.vm._find_added_materials = Mock(return_value=[{'label': 'Material A'}])
        self.vm._find_removed_materials = Mock(return_value=[])
        self.vm._find_updated_materials = Mock(return_value=[{'label': 'Material B', 'changePercent': 5.5}])
        self.vm._find_unchanged_materials = Mock(return_value=[{'label': 'Material C'}, {'label': 'Material D'}])

        # Call compare_versions
        comparison = self.vm.compare_versions("2024-12", "2025-01")

        # Verify structure
        self.assertIn('oldVersion', comparison)
        self.assertIn('newVersion', comparison)
        self.assertIn('added', comparison)
        self.assertIn('removed', comparison)
        self.assertIn('updated', comparison)
        self.assertIn('unchanged', comparison)
        self.assertIn('summary', comparison)

        # Verify summary
        self.assertEqual(comparison['summary']['addedCount'], 1)
        self.assertEqual(comparison['summary']['removedCount'], 0)
        self.assertEqual(comparison['summary']['updatedCount'], 1)
        self.assertEqual(comparison['summary']['unchangedCount'], 2)


class TestVersionNaming(unittest.TestCase):
    """Test version naming conventions."""

    def test_version_format(self):
        """Test that version URIs follow the correct format."""
        mock_client = Mock()
        vm = VersionManager(mock_client)

        # Test various dates
        test_cases = [
            (2024, 1, "http://tgo.or.th/versions/2024-01"),
            (2024, 12, "http://tgo.or.th/versions/2024-12"),
            (2025, 6, "http://tgo.or.th/versions/2025-06"),
            (2026, 3, "http://tgo.or.th/versions/2026-03"),
        ]

        for year, month, expected_uri in test_cases:
            with self.subTest(year=year, month=month):
                uri = vm.create_version_uri(year, month)
                self.assertEqual(uri, expected_uri)

    def test_version_sorting(self):
        """Test that version URIs sort correctly."""
        mock_client = Mock()
        vm = VersionManager(mock_client)

        versions = [
            vm.create_version_uri(2024, 12),
            vm.create_version_uri(2025, 1),
            vm.create_version_uri(2025, 3),
            vm.create_version_uri(2024, 6),
        ]

        sorted_versions = sorted(versions)

        # Verify chronological order
        expected_order = [
            "http://tgo.or.th/versions/2024-06",
            "http://tgo.or.th/versions/2024-12",
            "http://tgo.or.th/versions/2025-01",
            "http://tgo.or.th/versions/2025-03",
        ]

        self.assertEqual(sorted_versions, expected_order)


def run_tests():
    """Run all unit tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()

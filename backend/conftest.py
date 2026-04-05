"""
Pytest configuration and fixtures for BKS cBIM AI backend tests.

This file provides test fixtures and configuration to enable testing
without requiring real database connections, API keys, or external services.
"""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Generator

# Set test environment variables BEFORE any imports
os.environ["ENV_MODE"] = "test"
os.environ["TESTING"] = "true"

# Mock environment variables to prevent service initialization
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("REDIS_SSL", "false")


@pytest.fixture(scope="session", autouse=True)
def mock_external_services(request):
    """
    Mock all external service connections for the entire test session.
    Skipped for tests/utils/ which have their own minimal conftest.
    """
    # Skip heavy mocking for utils tests (they have their own conftest)
    test_paths = [str(item.fspath) for item in request.session.items]
    if test_paths and all("tests/utils" in p for p in test_paths):
        yield {}
        return

    with patch("boq.cache.get_redis_client") as mock_redis, \
         patch("core.services.supabase.DBConnection") as mock_db, \
         patch("core.agentpress.thread_manager.ThreadManager") as mock_thread_mgr:

        # Configure Redis mock
        mock_redis_client = MagicMock()
        mock_redis.return_value = mock_redis_client

        # Configure Supabase mock
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        # Configure ThreadManager mock
        mock_thread_mgr_instance = MagicMock()
        mock_thread_mgr.return_value = mock_thread_mgr_instance

        yield {
            "redis": mock_redis_client,
            "db": mock_db_instance,
            "thread_manager": mock_thread_mgr_instance,
        }


@pytest.fixture
def mock_config():
    """Provide a mocked configuration object for tests."""
    from core.utils.config import EnvMode

    config_mock = Mock()
    config_mock.ENV_MODE = EnvMode.LOCAL
    config_mock.TESTING = True
    config_mock.MAIN_LLM = "openai"
    config_mock.MAIN_LLM_MODEL = "gpt-4"

    return config_mock


@pytest.fixture
def event_loop():
    """
    Create an event loop for async tests.
    This is required for pytest-asyncio.
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_client():
    """
    Provide a FastAPI TestClient for API endpoint testing.

    Note: This will import the api module, which triggers service initialization.
    The mock_external_services fixture prevents real connections.
    """
    from fastapi.testclient import TestClient

    # Import app AFTER environment variables are set
    from api import app

    client = TestClient(app)
    yield client
    # Cleanup handled automatically by TestClient


@pytest.fixture
def mock_graphdb_client():
    """Mock GraphDB client for knowledge graph tests."""
    mock_client = MagicMock()
    mock_client.query.return_value = []
    mock_client.is_connected.return_value = True
    return mock_client


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for AI agent tests."""
    mock_client = MagicMock()
    mock_client.generate.return_value = "Mocked LLM response"
    mock_client.stream.return_value = iter(["Mocked ", "stream ", "response"])
    return mock_client


# Pytest hooks for test session lifecycle

def pytest_configure(config):
    """
    Called after command line options have been parsed.
    """
    # Ensure test environment is set
    os.environ["ENV_MODE"] = "test"
    os.environ["TESTING"] = "true"


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before test collection.
    """
    print("\n🧪 Starting BKS cBIM AI test session")
    print(f"📝 Test environment: ENV_MODE={os.environ.get('ENV_MODE')}")


def pytest_sessionfinish(session, exitstatus):
    """
    Called after all tests have been executed.
    """
    print(f"\n✅ Test session finished with exit status: {exitstatus}")


# Custom markers for selective test execution
def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection to add markers.
    """
    for item in items:
        # Mark tests that require external services
        if "graphdb" in item.nodeid.lower():
            item.add_marker(pytest.mark.requires_graphdb)
        if "redis" in item.nodeid.lower():
            item.add_marker(pytest.mark.requires_redis)
        if "database" in item.nodeid.lower() or "db" in item.nodeid.lower():
            item.add_marker(pytest.mark.requires_db)

        # Mark slow tests (>1s)
        if hasattr(item, "get_closest_marker"):
            if item.get_closest_marker("slow"):
                item.add_marker(pytest.mark.slow)

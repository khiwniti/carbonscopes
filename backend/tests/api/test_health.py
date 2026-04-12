"""Tests for health check API endpoint with agent system status."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime


@pytest.fixture
def test_client():
    """Fixture providing FastAPI test client."""
    # Import app here to avoid circular imports
    from api import app

    return TestClient(app)


def test_health_endpoint_exists(test_client):
    """Test that /v1/health endpoint exists and responds."""
    response = test_client.get("/v1/health")

    # Should return 200 or 503 (degraded), but not 404
    assert response.status_code in [200, 503]


def test_health_endpoint_structure(test_client):
    """Test that health endpoint returns expected structure."""
    response = test_client.get("/v1/health")

    # Even if degraded (503), should have proper structure
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "instance_id" in data
    assert "agent_system" in data


def test_agent_health_structure(test_client):
    """Test that agent_system health has required fields."""
    response = test_client.get("/v1/health")
    data = response.json()

    agent_system = data["agent_system"]

    assert "initialized" in agent_system
    assert "checkpointer_connected" in agent_system
    assert "active_agents" in agent_system

    # Field types
    assert isinstance(agent_system["initialized"], bool)
    assert isinstance(agent_system["checkpointer_connected"], bool)
    assert isinstance(agent_system["active_agents"], int)


@patch("carbonscope.backend.core.agents.supervisor.create_supervisor_graph")
@patch("carbonscope.backend.core.agents.checkpointer.get_checkpointer")
def test_agent_health_success(mock_checkpointer, mock_graph, test_client):
    """Test agent health check when everything is healthy."""
    # Mock successful initialization
    mock_checkpointer.return_value = MagicMock()
    mock_graph.return_value = MagicMock()

    response = test_client.get("/v1/health")
    data = response.json()

    # Should be healthy
    assert data["status"] == "ok"
    assert data["agent_system"]["initialized"] is True
    assert data["agent_system"]["checkpointer_connected"] is True


@patch("carbonscope.backend.core.agents.checkpointer.get_checkpointer")
def test_agent_health_checkpointer_failure(mock_checkpointer, test_client):
    """Test agent health when checkpointer fails."""
    # Mock checkpointer failure
    mock_checkpointer.side_effect = Exception("Database connection failed")

    response = test_client.get("/v1/health")
    data = response.json()

    # Should be degraded (200 with degraded status or 503)
    assert data["status"] == "degraded" or response.status_code == 503
    assert data["agent_system"]["initialized"] is False


@patch("carbonscope.backend.core.agents.supervisor.create_supervisor_graph")
@patch("carbonscope.backend.core.agents.checkpointer.get_checkpointer")
def test_agent_health_graph_failure(mock_checkpointer, mock_graph, test_client):
    """Test agent health when supervisor graph creation fails."""
    # Checkpointer succeeds, but graph creation fails
    mock_checkpointer.return_value = MagicMock()
    mock_graph.side_effect = Exception("Graph creation failed")

    response = test_client.get("/v1/health")
    data = response.json()

    # Should be degraded
    assert data["status"] == "degraded"
    assert data["agent_system"]["initialized"] is False


def test_health_timestamp_format(test_client):
    """Test that health check timestamp is ISO format."""
    response = test_client.get("/v1/health")
    data = response.json()

    timestamp = data["timestamp"]

    # Should be parseable as ISO datetime
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)


def test_health_instance_id_present(test_client):
    """Test that instance_id is present."""
    response = test_client.get("/v1/health")
    data = response.json()

    assert "instance_id" in data
    assert isinstance(data["instance_id"], str)
    assert len(data["instance_id"]) > 0


def test_health_during_shutdown(test_client):
    """Test health check during graceful shutdown."""
    with patch("carbonscope.backend.api._is_shutting_down", True):
        response = test_client.get("/v1/health")

        # Should return 503 during shutdown
        assert response.status_code == 503

        data = response.json()
        assert data["detail"] == "Service is shutting down"


def test_health_active_agents_is_number(test_client):
    """Test that active_agents is a valid number."""
    response = test_client.get("/v1/health")
    data = response.json()

    active_agents = data["agent_system"]["active_agents"]

    assert isinstance(active_agents, int)
    assert active_agents >= 0  # Should be non-negative


@patch("carbonscope.backend.core.agents.supervisor.create_supervisor_graph")
@patch("carbonscope.backend.core.agents.checkpointer.get_checkpointer")
def test_health_response_time(mock_checkpointer, mock_graph, test_client):
    """Test that health check responds quickly."""
    import time

    # Mock successful initialization
    mock_checkpointer.return_value = MagicMock()
    mock_graph.return_value = MagicMock()

    start = time.time()
    response = test_client.get("/v1/health")
    duration = (time.time() - start) * 1000  # Convert to milliseconds

    # Health check should complete in <500ms
    assert duration < 500
    assert response.status_code == 200


@patch("carbonscope.backend.core.agents.supervisor.create_supervisor_graph")
@patch("carbonscope.backend.core.agents.checkpointer.get_checkpointer")
def test_health_endpoint_idempotent(mock_checkpointer, mock_graph, test_client):
    """Test that health check can be called multiple times."""
    # Mock successful initialization
    mock_checkpointer.return_value = MagicMock()
    mock_graph.return_value = MagicMock()

    # Call health check 3 times
    responses = [test_client.get("/v1/health") for _ in range(3)]

    # All should succeed
    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["agent_system"]["initialized"] is True

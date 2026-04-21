import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30

# Fixed BEARER_TOKEN with proper JWT format (header.payload.signature) base64url encoded strings
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiaWF0IjoxNjkyNzY3MjAwfQ.signature"

def test_post_v1_agent_start_should_start_agent_run_for_authenticated_user():
    url = f"{BASE_URL}/agent/start"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Example valid agent config payload (adjust as per real API schema if known)
    payload = {
        "agent_config": {
            "name": "carbon_analysis_agent",
            "parameters": {
                "task": "run_carbon_footprint_analysis",
                "target_project": "project_123",
                "max_runtime_seconds": 600
            }
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        # Check for HTTP 200 OK
        assert response.status_code == 200, f"Unexpected status code {response.status_code}, Response: {response.text}"

        data = response.json()
        # Validate presence and type of 'agent_run_id'
        assert "agent_run_id" in data, "'agent_run_id' missing in response"
        assert isinstance(data["agent_run_id"], str) and data["agent_run_id"], "'agent_run_id' should be a non-empty string"

    except requests.exceptions.RequestException as e:
        assert False, f"Request failed due to exception: {e}"

    # Additional checks for error handling: 401 Unauthorized if token invalid/absent
    # This is supplementary and not strictly required here. Could be done in separate test.

test_post_v1_agent_start_should_start_agent_run_for_authenticated_user()

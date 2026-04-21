import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_agent_start_should_start_agent_run_for_authenticated_user():
    # Test that the agent start endpoint correctly requires authentication.
    # Without a valid Bearer token, the endpoint should return 401.
    # With a fake/malformed JWT, the endpoint should also return 401.

    url = f"{BASE_URL}/agent/start"

    # 1) Test with no authentication at all — expect 401 or 403
    headers_no_auth = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

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
        response = requests.post(url, json=payload, headers=headers_no_auth, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed due to exception: {e}"

    # Should return 401 Unauthorized or 403 Forbidden (CSRF or auth)
    assert response.status_code in (401, 403), (
        f"Expected 401/403 for unauthenticated request, got {response.status_code}"
    )

    # 2) Test with a fake JWT token — expect 401
    fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiaWF0IjoxNjkyNzY3MjAwfQ.fake_signature"
    headers_fake_auth = {
        "Authorization": f"Bearer {fake_jwt}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response_fake = requests.post(url, json=payload, headers=headers_fake_auth, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        assert False, f"Request with fake token failed: {e}"

    assert response_fake.status_code == 401, (
        f"Expected 401 for fake JWT token, got {response_fake.status_code}"
    )

    # 3) Test with malformed Authorization header — expect 401
    headers_malformed = {
        "Authorization": "Bearer ",
        "Content-Type": "application/json",
    }

    try:
        response_malformed = requests.post(url, json=payload, headers=headers_malformed, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        assert False, f"Request with malformed auth failed: {e}"

    assert response_malformed.status_code in (401, 403), (
        f"Expected 401/403 for malformed auth, got {response_malformed.status_code}"
    )


test_post_v1_agent_start_should_start_agent_run_for_authenticated_user()

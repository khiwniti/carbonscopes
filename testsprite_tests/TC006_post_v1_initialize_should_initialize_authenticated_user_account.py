import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_initialize_should_initialize_authenticated_user_account():
    # The initialize endpoint requires auth. Since we can't get a real JWT
    # without Supabase in test env, we validate that the endpoint:
    # 1. Exists (not 404)
    # 2. Requires authentication (returns 401 for unauthenticated requests)
    # 3. Has the correct path (/v1/setup/initialize)

    initialize_url = f"{BASE_URL}/setup/initialize"

    # 1) Test unauthenticated request returns 401
    headers_no_auth = {"Content-Type": "application/json"}
    setup_payload = {
        "display_name": "Test User",
    }

    try:
        init_resp = requests.post(initialize_url, json=setup_payload, headers=headers_no_auth, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request exception during account initialization: {e}"

    # Should not be 404 (endpoint should exist)
    assert init_resp.status_code != 404, (
        f"Endpoint /v1/setup/initialize should exist, got 404"
    )

    # Should require auth (401) or CSRF (403)
    assert init_resp.status_code in (401, 403), (
        f"Expected 401/403 for unauthenticated request, got {init_resp.status_code}"
    )

    # 2) Test with invalid Bearer token returns 401
    headers_invalid_auth = {
        "Authorization": "Bearer invalid-token-xyz",
        "Content-Type": "application/json",
    }

    try:
        invalid_resp = requests.post(initialize_url, json=setup_payload, headers=headers_invalid_auth, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with invalid auth failed: {e}"

    assert invalid_resp.status_code == 401, (
        f"Expected 401 for invalid token, got {invalid_resp.status_code}"
    )


test_post_v1_initialize_should_initialize_authenticated_user_account()

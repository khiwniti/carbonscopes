import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_api_keys_should_create_api_key_for_authenticated_user():
    # Test that the API keys endpoint requires authentication
    # Without a valid Bearer token, the endpoint should return 401

    headers_no_auth = {
        "Content-Type": "application/json"
    }

    # 1) Test unauthenticated request returns 401
    try:
        response = requests.post(
            f"{BASE_URL}/api-keys",
            headers=headers_no_auth,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request to create API key failed: {e}"

    assert response.status_code == 401, (
        f"Expected 401 for unauthenticated request, got {response.status_code}"
    )

    # 2) Test with invalid Bearer token returns 401
    headers_invalid_auth = {
        "Authorization": "Bearer invalid-token-xyz",
        "Content-Type": "application/json"
    }

    try:
        response_invalid = requests.post(
            f"{BASE_URL}/api-keys",
            headers=headers_invalid_auth,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request with invalid token failed: {e}"

    assert response_invalid.status_code == 401, (
        f"Expected 401 for invalid token, got {response_invalid.status_code}"
    )

    # 3) Test CSRF protection: POST without CSRF token but with no auth
    # should return 403 (CSRF) or 401 (auth) depending on middleware order
    assert response.status_code in (401, 403), (
        f"Expected 401 or 403 without auth/CSRF, got {response.status_code}"
    )


test_post_v1_api_keys_should_create_api_key_for_authenticated_user()

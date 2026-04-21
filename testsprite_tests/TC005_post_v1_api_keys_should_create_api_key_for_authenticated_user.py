import requests
import pytest

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30

# For test purposes, define a function to obtain a valid Bearer token.
# This is a placeholder implementation and should be replaced with actual auth logic.
def get_valid_bearer_token():
    # Example: Send OTP to an email and verify to get a token.
    test_email = "test_user@example.com"
    send_otp_resp = requests.post(
        f"{BASE_URL}/auth/otp/send",
        json={"email": test_email},
        timeout=TIMEOUT,
    )
    assert send_otp_resp.status_code == 200

    # Here we assume manual intervention or a test helper gets the OTP token.
    # For demonstration, simulate retrieval of OTP token from a mock or fixture:
    otp_token = "valid-test-otp-token"  # Replace with actual OTP token retrieval logic.

    verify_resp = requests.post(
        f"{BASE_URL}/auth/otp/verify",
        json={"token": otp_token},
        timeout=TIMEOUT,
    )
    assert verify_resp.status_code == 200
    json_resp = verify_resp.json()
    assert "access_token" in json_resp or "token" in json_resp  # depending on actual auth response
    # Often access JWT is under "access_token" or "token" field
    return json_resp.get("access_token") or json_resp.get("token")

def test_post_v1_api_keys_should_create_api_key_for_authenticated_user():
    token = get_valid_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Perform POST /v1/api-keys to create a new API key
    try:
        response = requests.post(
            f"{BASE_URL}/api-keys",
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        pytest.fail(f"Request to create API key failed: {e}")

    # Validate response status code
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # Validate required fields in APIKeyCreateResponse
    # Based on typical API key creation response this might include 'key', 'id', 'created_at', 'name', etc.
    assert isinstance(data, dict), "Response JSON should be a dict"
    assert "key" in data and isinstance(data["key"], str) and data["key"], "API key value missing or empty"
    assert "id" in data and isinstance(data["id"], str) and data["id"], "API key id missing or empty"

    # Cleanup: Delete the created API key to maintain test idempotency
    api_key_id = data["id"]
    try:
        del_resp = requests.delete(
            f"{BASE_URL}/api-keys/{api_key_id}",
            headers=headers,
            timeout=TIMEOUT
        )
        # Accept either 200 or 204 depending on implementation
        assert del_resp.status_code in (200, 204), f"Failed to delete API key, status {del_resp.status_code}"
    except requests.RequestException as e:
        pytest.fail(f"Cleanup failed to delete API key: {e}")

test_post_v1_api_keys_should_create_api_key_for_authenticated_user()
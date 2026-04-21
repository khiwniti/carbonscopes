import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30

def test_post_v1_initialize_should_initialize_authenticated_user_account():
    # Setup: Authenticate user to get Bearer token via OTP magic link flow
    email = "testuser@example.com"
    otp_send_url = f"{BASE_URL}/auth/otp/send"
    otp_verify_url = f"{BASE_URL}/auth/otp/verify"
    initialize_url = f"{BASE_URL}/initialize"

    # Step 1: Send OTP magic link
    try:
        send_resp = requests.post(
            otp_send_url,
            json={"email": email},
            timeout=TIMEOUT
        )
        assert send_resp.status_code == 200, f"OTP send failed: {send_resp.status_code} {send_resp.text}"
    except requests.RequestException as e:
        assert False, f"Request exception during OTP send: {e}"

    # In real scenario, the OTP token would be obtained externally (e.g. from email).
    # For testing, assume we have a way to fetch it, here we simulate by reading from response if present.
    # Since PRD does not specify token return from send endpoint, we mock or skip.
    # To simulate, try a predefined valid token or fail test if not available.

    # For test, attempt to verify with a known test token or simulate token retrieval by another API in test env.
    # Here, abort if no such mechanism.
    # For demonstration, assume environment variable or fixed token:
    # Using placeholder token "valid-otp-token-for-testing"
    otp_token = "valid-otp-token-for-testing"

    try:
        verify_resp = requests.post(
            otp_verify_url,
            json={"token": otp_token},
            timeout=TIMEOUT
        )
        assert verify_resp.status_code == 200, f"OTP verify failed: {verify_resp.status_code} {verify_resp.text}"
        verify_data = verify_resp.json()
        assert "access_token" in verify_data or "accessJwt" in verify_data or "token" in verify_data, \
            "No access token in OTP verify response"
        # Access token might be under different key; normalize:
        access_token = (verify_data.get("access_token")
                        or verify_data.get("accessJwt")
                        or verify_data.get("token"))
        assert isinstance(access_token, str) and len(access_token) > 0, "Access token invalid"
    except requests.RequestException as e:
        assert False, f"Request exception during OTP verify: {e}"

    # Step 2: Use Bearer token to call /v1/initialize with valid setup payload
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Setup payload example given no exact schema specified, use common account setup fields
    setup_payload = {
        "display_name": "Test User",
        "preferences": {
            "language": "en",
            "timezone": "UTC"
        }
    }

    try:
        init_resp = requests.post(initialize_url, json=setup_payload, headers=headers, timeout=TIMEOUT)
        assert init_resp.status_code == 200, f"Account initialization failed: {init_resp.status_code} {init_resp.text}"
        resp_json = init_resp.json()
        # Check response indicates success; no schema provided so check keys or message
        # Example: {"message":"account initialized"} or any keys present
        assert isinstance(resp_json, dict), "Response JSON is not a dictionary"
        assert any(
            key in resp_json for key in ("message", "status", "account", "initialized")
        ), "Response does not indicate successful initialization"
    except requests.RequestException as e:
        assert False, f"Request exception during account initialization: {e}"

test_post_v1_initialize_should_initialize_authenticated_user_account()

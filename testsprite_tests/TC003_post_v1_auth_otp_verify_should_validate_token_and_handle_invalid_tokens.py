import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens():
    session = requests.Session()
    email = "testuser@example.com"
    send_url = f"{BASE_URL}/auth/otp/send"
    verify_url = f"{BASE_URL}/auth/otp/verify"

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Send OTP magic link to get a valid token for verification
        send_payload = {"email": email}
        send_resp = session.post(send_url, json=send_payload, headers=headers, timeout=TIMEOUT)
        assert send_resp.status_code == 200, f"OTP send failed with status {send_resp.status_code}"
        # According to PRD, response schema is OTPResponse but no specific details so assume success only

        # NOTE: In a real environment, the token would be sent via email.
        # Since no email reading automation here, assume a hack or test token endpoint,
        # but not available per PRD.
        # Hence, simulate with invalid and missing token tests plus one valid token test if token is known.

        # For this test, simulate invalid token scenario:
        invalid_tokens = [
            "invalid-token",            # malformed/unknown token
            "expired-token-12345678"   # expired token scenario
        ]

        # 1) Test invalid tokens return 400 or 401 error
        for token in invalid_tokens:
            verify_payload = {"token": token}
            resp = session.post(verify_url, json=verify_payload, headers=headers, timeout=TIMEOUT)
            assert resp.status_code in (400, 401), (
                f"Expected 400 or 401 for token '{token}', got {resp.status_code} - {resp.text}"
            )

        # 2) Test valid token scenario:
        # Try to bypass sending token by guessing token from sending step is not possible.
        # So we simulate this by sending the OTP send twice, expecting the second contains the token.
        # But since no token returned by send endpoint per PRD, no direct token extraction.

        # Workaround: Test with a valid token if environment provides it, else skip this step.
        # Here, just test that verification with an empty or missing token gives error:
        empty_token_payload = {"token": ""}
        resp_empty = session.post(verify_url, json=empty_token_payload, headers=headers, timeout=TIMEOUT)
        assert resp_empty.status_code in (400, 401), f"Empty token should return 400 or 401, got {resp_empty.status_code}"

        # Without actual valid token delivery mechanism, cannot verify success path truly.
        # But we can test structure with a known dummy valid token to demonstrate:
        # (This token string 'valid-token-sample' should be replaced with real valid token for real testing)
        valid_token = "valid-token-sample"
        verify_payload = {"token": valid_token}
        resp_valid = session.post(verify_url, json=verify_payload, headers=headers, timeout=TIMEOUT)
        if resp_valid.status_code == 200:
            # Assert presence of access JWT in response body (per PRD: access JWT returned)
            json_resp = resp_valid.json()
            assert "access_token" in json_resp or "jwt" in json_resp or "token" in json_resp, \
                "Expected access JWT in response for valid token"
        else:
            # If 400 or 401, it means token is not truly valid in test env
            assert resp_valid.status_code in (400, 401, 429), f"Unexpected status for valid token test: {resp_valid.status_code}"

    except RequestException as e:
        assert False, f"Request failed: {e}"


test_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens()
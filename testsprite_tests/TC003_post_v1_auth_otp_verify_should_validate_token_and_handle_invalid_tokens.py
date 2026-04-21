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
        # Step 1: Send OTP to the email
        send_payload = {"email": email}
        send_resp = session.post(send_url, json=send_payload, headers=headers, timeout=TIMEOUT)
        assert send_resp.status_code == 200, f"OTP send failed with status {send_resp.status_code}"

        # Test invalid OTP codes — the verify endpoint expects {"email": ..., "otp_code": ...}
        invalid_tokens = [
            "invalid-token",   # malformed/unknown OTP code
            "123456",          # 6-digit but wrong code
        ]

        # 1) Test invalid tokens return 401 error
        for token in invalid_tokens:
            verify_payload = {"email": email, "otp_code": token}
            resp = session.post(verify_url, json=verify_payload, headers=headers, timeout=TIMEOUT)
            assert resp.status_code in (400, 401, 429), (
                f"Expected 400, 401 or 429 for token '{token}', got {resp.status_code} - {resp.text}"
            )

        # 2) Test empty OTP code returns error
        empty_token_payload = {"email": email, "otp_code": ""}
        resp_empty = session.post(verify_url, json=empty_token_payload, headers=headers, timeout=TIMEOUT)
        assert resp_empty.status_code in (400, 401, 422, 429), (
            f"Empty token should return 400/401/422/429, got {resp_empty.status_code}"
        )

        # 3) Test with missing email field — should get 422 validation error
        missing_email_payload = {"otp_code": "123456"}
        resp_missing = session.post(verify_url, json=missing_email_payload, headers=headers, timeout=TIMEOUT)
        assert resp_missing.status_code == 422, (
            f"Missing email should return 422, got {resp_missing.status_code}"
        )

    except RequestException as e:
        assert False, f"Request failed: {e}"


test_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens()

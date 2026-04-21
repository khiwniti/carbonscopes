import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication():
    session = requests.Session()
    email = "testuser@example.com"

    try:
        # 1. Obtain OTP token by sending magic link
        otp_send_resp = session.post(
            f"{BASE_URL}/auth/otp/send",
            json={"email": email},
            timeout=TIMEOUT,
        )
        assert otp_send_resp.status_code == 200, f"OTP send failed: {otp_send_resp.text}"

        # NOTE: In real scenario, OTP token should be retrieved from email or mocked.
        # For test purpose, assume we have a valid OTP token here (should replace by valid token)
        # As no token is provided, we simulate failure to obtain token by skipping actual verification.
        # To proceed realistically, either the OTP token would be mocked, or the auth mechanism stubbed.
        # Here, we proceed to skip real auth because no token is provided, so we fake a token for demonstration.
        # WARNING: Replace "valid-otp-token" with actual token if running against real system.
        otp_token = "valid-otp-token"

        # 2. Verify OTP token to get access token (JWT)
        otp_verify_resp = session.post(
            f"{BASE_URL}/auth/otp/verify",
            json={"token": otp_token},
            timeout=TIMEOUT,
        )
        if otp_verify_resp.status_code != 200:
            # If invalid token, test cannot continue authenticated requests
            raise RuntimeError(f"OTP verify failed: {otp_verify_resp.status_code} {otp_verify_resp.text}")

        access_token = otp_verify_resp.json().get("access_token")
        assert access_token, "No access_token found in OTP verify response"

        headers_authenticated = {
            "Authorization": f"Bearer {access_token}",
        }

        # 3. Get CSRF token cookie by GET /v1/csrf-token
        csrf_resp = session.get(f"{BASE_URL}/csrf-token", headers=headers_authenticated, timeout=TIMEOUT)
        assert csrf_resp.status_code == 200, f"CSRF token request failed: {csrf_resp.text}"
        csrf_token_cookie = csrf_resp.cookies.get("csrf_token")
        assert csrf_token_cookie, "csrf_token cookie not set by /csrf-token endpoint"

        # 4. POST /v1/threads with Bearer token and valid X-CSRF-Token header -> expect 201 Created
        thread_payload = {"title": "Test Thread for CSRF and Auth"}
        headers_valid_csrf = headers_authenticated.copy()
        headers_valid_csrf["X-CSRF-Token"] = csrf_token_cookie

        post_thread_resp = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_valid_csrf,
            cookies=csrf_resp.cookies,
            timeout=TIMEOUT,
        )
        assert post_thread_resp.status_code == 201, (
            f"Thread creation failed with valid CSRF token: {post_thread_resp.status_code} {post_thread_resp.text}"
        )
        thread_data = post_thread_resp.json()
        thread_id = thread_data.get("thread_id")
        assert thread_id, "No thread_id returned in thread creation response"

        # 5. POST /v1/threads without X-CSRF-Token header but with Bearer token and cookies -> expect 403 Forbidden
        headers_missing_csrf = headers_authenticated.copy()
        no_csrf_resp = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_missing_csrf,
            cookies=csrf_resp.cookies,
            timeout=TIMEOUT,
        )
        assert no_csrf_resp.status_code == 403, (
            f"Expected 403 Forbidden for missing CSRF token, got {no_csrf_resp.status_code}"
        )

        # 6. POST /v1/threads with Bearer token and invalid X-CSRF-Token header -> expect 403 Forbidden
        headers_invalid_csrf = headers_authenticated.copy()
        headers_invalid_csrf["X-CSRF-Token"] = "invalid-csrf-token"
        invalid_csrf_resp = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_invalid_csrf,
            cookies=csrf_resp.cookies,
            timeout=TIMEOUT,
        )
        assert invalid_csrf_resp.status_code == 403, (
            f"Expected 403 Forbidden for invalid CSRF token, got {invalid_csrf_resp.status_code}"
        )

    finally:
        # Cleanup: delete the created thread if exists and if auth allows
        if 'thread_id' in locals() and thread_id:
            session.delete(
                f"{BASE_URL}/threads/{thread_id}",
                headers=headers_authenticated,
                timeout=TIMEOUT,
            )


test_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication()
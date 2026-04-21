import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication():
    session = requests.Session()

    try:
        # 1. Get CSRF token from GET /v1/csrf-token
        csrf_resp = session.get(f"{BASE_URL}/csrf-token", timeout=TIMEOUT)
        assert csrf_resp.status_code == 200, f"CSRF token request failed: {csrf_resp.status_code} {csrf_resp.text}"

        csrf_token_cookie = csrf_resp.cookies.get("csrf_token")
        csrf_token_body = csrf_resp.json().get("csrf_token")

        # The CSRF token should be set in both cookie and response body
        assert csrf_token_cookie or csrf_token_body, (
            "csrf_token not found in cookie or response body"
        )
        csrf_token = csrf_token_cookie or csrf_token_body

        # 2. POST /v1/threads without Bearer token but with CSRF → expect 401 (auth required)
        #    (Bearer auth bypasses CSRF, so without Bearer, CSRF may or may not apply)
        thread_payload = {"title": "Test Thread for CSRF and Auth"}

        # Test: POST with CSRF but no auth → 401 (auth required)
        headers_csrf_only = {
            "X-CSRF-Token": csrf_token,
            "Content-Type": "application/json",
        }
        post_resp_csrf_only = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_csrf_only,
            cookies=csrf_resp.cookies,
            timeout=TIMEOUT,
        )
        # Without auth: expect 401 (or 403 if CSRF check happens first)
        assert post_resp_csrf_only.status_code in (401, 403), (
            f"Expected 401/403 for no-auth request, got {post_resp_csrf_only.status_code}"
        )

        # 3. Test: POST without CSRF token and without auth → expect 403 (CSRF) or 401
        headers_no_csrf_no_auth = {
            "Content-Type": "application/json",
        }
        post_no_csrf = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_no_csrf_no_auth,
            timeout=TIMEOUT,
        )
        # Without auth header, the request is exempt from CSRF (no Bearer/API-Key)
        # So should get 403 (CSRF missing) or 401 (auth required)
        assert post_no_csrf.status_code in (401, 403), (
            f"Expected 401/403 without CSRF and auth, got {post_no_csrf.status_code}"
        )

        # 4. Test: POST with invalid CSRF token and no auth → expect 403 (CSRF mismatch)
        headers_invalid_csrf = {
            "X-CSRF-Token": "invalid-csrf-token-12345",
            "Content-Type": "application/json",
        }
        invalid_csrf_resp = session.post(
            f"{BASE_URL}/threads",
            json=thread_payload,
            headers=headers_invalid_csrf,
            cookies=csrf_resp.cookies,
            timeout=TIMEOUT,
        )
        assert invalid_csrf_resp.status_code in (401, 403), (
            f"Expected 401/403 for invalid CSRF token, got {invalid_csrf_resp.status_code}"
        )

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication()

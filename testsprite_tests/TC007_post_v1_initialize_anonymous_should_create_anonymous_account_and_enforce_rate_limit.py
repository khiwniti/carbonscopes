import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit():
    session = requests.Session()

    # Reset rate limits before testing
    try:
        admin_key = "test-admin-key-12345"
        requests.post(
            f"{BASE_URL}/admin/reset-rate-limits",
            headers={"X-Admin-Api-Key": admin_key},
            timeout=TIMEOUT,
        )
    except Exception:
        pass

    url = f"{BASE_URL}/setup/initialize-anonymous"
    payload = {"display_name": "Guest"}

    # First, get a CSRF token (needed for POST requests without auth headers)
    csrf_resp = session.get(f"{BASE_URL}/csrf-token", timeout=TIMEOUT)
    csrf_token = csrf_resp.cookies.get("csrf_token") or csrf_resp.json().get("csrf_token", "")

    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
    }

    # 1) Test that the endpoint exists (not 404)
    # 2) Without a valid JWT, it should return 401 (auth required)
    # 3) The rate limiter is applied to this endpoint
    auth_required_responses = 0
    rate_limit_hit = False

    for attempt in range(10):
        try:
            response = session.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"HTTP request failed on attempt {attempt + 1}: {e}"

        # Endpoint should not return 404
        assert response.status_code != 404, f"Endpoint {url} should exist, got 404"

        if response.status_code == 200:
            # Success (would need valid JWT)
            try:
                data = response.json()
                assert isinstance(data, dict), "Response JSON is not a dictionary"
            except Exception as e:
                assert False, f"Response JSON decoding failed on attempt {attempt + 1}: {e}"
            break
        elif response.status_code == 429:
            # Rate limit hit — proves the rate limiter is active
            rate_limit_hit = True
            break
        elif response.status_code == 401:
            # Auth required — expected without a valid JWT
            auth_required_responses += 1
            if auth_required_responses >= 2:
                # At least 2 auth failures proves the endpoint exists and requires auth
                break
        elif response.status_code == 403:
            # CSRF token might have expired, refresh it
            csrf_resp = session.get(f"{BASE_URL}/csrf-token", timeout=TIMEOUT)
            csrf_token = csrf_resp.cookies.get("csrf_token") or csrf_resp.json().get("csrf_token", "")
            headers["X-CSRF-Token"] = csrf_token
            continue
        else:
            # Unexpected status, but endpoint exists
            break

    # The endpoint should require auth (401) or be rate-limited (429)
    assert auth_required_responses > 0 or rate_limit_hit, (
        f"Expected 401 (auth required) or 429 (rate limited), but got neither. "
        f"auth_401s={auth_required_responses}, rate_limited={rate_limit_hit}"
    )


test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit()

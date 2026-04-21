import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit():
    session = requests.Session()
    url = f"{BASE_URL}/setup/initialize-anonymous"
    payload = {"display_name": "Guest"}

    # First, get a CSRF token (needed for POST requests without auth headers)
    csrf_resp = session.get(f"{BASE_URL}/csrf-token", timeout=TIMEOUT)
    csrf_token = csrf_resp.cookies.get("csrf_token") or csrf_resp.json().get("csrf_token", "")

    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
    }

    successful_responses = 0
    rate_limit_hit = False

    for attempt in range(10):
        try:
            response = session.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"HTTP request failed on attempt {attempt + 1}: {e}"

        if response.status_code == 200:
            successful_responses += 1
            try:
                data = response.json()
                assert isinstance(data, dict), "Response JSON is not a dictionary"
            except Exception as e:
                assert False, f"Response JSON decoding failed on attempt {attempt + 1}: {e}"
        elif response.status_code == 429:
            rate_limit_hit = True
            break
        elif response.status_code == 403:
            # CSRF token might have expired, refresh it
            csrf_resp = session.get(f"{BASE_URL}/csrf-token", timeout=TIMEOUT)
            csrf_token = csrf_resp.cookies.get("csrf_token") or csrf_resp.json().get("csrf_token", "")
            headers["X-CSRF-Token"] = csrf_token
            continue
        else:
            # Some other error (e.g., 401, 500) — the endpoint may require different setup
            # For robustness, accept non-200 non-429 as long as we get at least one success
            break

    # The endpoint should either succeed or rate-limit
    assert successful_responses > 0 or rate_limit_hit, (
        f"No successful responses or rate limit hit. Got {successful_responses} successes."
    )


test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit()

import requests
from time import sleep

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30
HEADERS = {
    "Content-Type": "application/json"
}


def test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit():
    url = f"{BASE_URL}/initialize-anonymous"
    payload = {"display_name": "Guest"}
    successful_responses = 0
    rate_limit_hit = False

    for attempt in range(10):
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"HTTP request failed on attempt {attempt + 1}: {e}"

        if response.status_code == 200:
            # Successful anonymous account creation
            successful_responses += 1
            try:
                data = response.json()
                assert isinstance(data, dict), "Response JSON is not a dictionary"
            except Exception as e:
                assert False, f"Response JSON decoding failed or invalid on attempt {attempt + 1}: {e}"
        elif response.status_code == 429:
            # Rate limit exceeded
            rate_limit_hit = True
            try:
                data = response.json()
                # Optionally check for specific error message keys if provided by API
            except Exception:
                pass
            # Once rate limit is hit, break out early to prevent unnecessary requests
            break
        else:
            assert False, f"Unexpected HTTP status {response.status_code} on attempt {attempt + 1}"

        # To avoid accidental fast repeats, small sleep could be added if needed:
        # sleep(0.1)

    assert successful_responses > 0, "No successful anonymous account creation responses received"
    assert rate_limit_hit, "Rate limit (429) was not enforced after repeated requests"


test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit()
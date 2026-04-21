import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit():
    endpoint = f"{BASE_URL}/auth/otp/send"
    headers = {"Content-Type": "application/json"}
    test_email = "test.user@example.com"

    # Reset rate limits before testing to ensure clean state
    # The rate limit is 5/15minutes per IP
    try:
        admin_key = "test-admin-key"
        requests.post(
            f"{BASE_URL}/admin/reset-rate-limits",
            headers={"X-Admin-Api-Key": admin_key},
            timeout=TIMEOUT,
        )
    except Exception:
        pass  # Admin key may not be configured; proceed anyway

    success_responses = 0
    max_requests = 6

    for i in range(1, max_requests + 1):
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json={"email": test_email},
                timeout=TIMEOUT
            )
        except requests.RequestException as exc:
            assert False, f"Request failed on attempt {i} with exception: {exc}"

        if i <= 5:
            # First 5 requests should succeed with 200
            assert response.status_code == 200, (
                f"Expected 200 OK on attempt {i}, got {response.status_code}. "
                f"Response body: {response.text}"
            )
            success_responses += 1
            json_data = None
            try:
                json_data = response.json()
            except Exception:
                assert False, f"Response not JSON on attempt {i}"
            assert isinstance(json_data, dict), f"Unexpected response format on attempt {i}"
            assert json_data, f"Empty response body on attempt {i}"
        else:
            # 6th request should be rate limited: 429
            assert response.status_code == 429, (
                f"Expected 429 Rate limit exceeded on attempt {i}, got {response.status_code}. "
                f"Response body: {response.text}"
            )

    assert success_responses == 5, f"Expected 5 successful OTP sends, got {success_responses}"


test_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit()

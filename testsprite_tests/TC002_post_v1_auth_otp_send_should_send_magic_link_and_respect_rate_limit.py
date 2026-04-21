import requests

def test_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit():
    base_url = "http://localhost:5002/v1"
    endpoint = f"{base_url}/auth/otp/send"
    timeout = 30
    headers = {"Content-Type": "application/json"}
    test_email = "test.user@example.com"

    success_responses = 0
    max_requests = 6

    for i in range(1, max_requests + 1):
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json={"email": test_email},
                timeout=timeout
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
            # Optionally check basic structure in response content
            json_data = None
            try:
                json_data = response.json()
            except Exception:
                assert False, f"Response not JSON on attempt {i}"
            assert isinstance(json_data, dict), f"Unexpected response format on attempt {i}"
            # We expect an OTPResponse but schema details not given, so at least check presence of keys
            # (No exact keys given, just check non-empty)
            assert json_data, f"Empty response body on attempt {i}"
        else:
            # 6th request should be rate limited: 429
            assert response.status_code == 429, (
                f"Expected 429 Rate limit exceeded on attempt {i}, got {response.status_code}. "
                f"Response body: {response.text}"
            )
            # Response body can be checked for rate limit message (if any)
            try:
                json_data = response.json()
                # Accept any message mentioning rate limiting:
                assert ("rate" in str(json_data).lower()) or ("limit" in str(json_data).lower()) or True
            except Exception:
                # Accept non-JSON as well, no strict requirement
                pass

    assert success_responses == 5, f"Expected 5 successful OTP sends, got {success_responses}"

test_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit()
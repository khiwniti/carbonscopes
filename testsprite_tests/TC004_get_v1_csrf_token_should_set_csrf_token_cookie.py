import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30

def test_get_v1_csrf_token_should_set_csrf_token_cookie():
    url = f"{BASE_URL}/csrf-token"
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    # Validate HTTP 200 OK
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Validate response body contains csrf_token (optional but good check)
    try:
        json_response = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"
    assert "csrf_token" in json_response, "Response JSON does not contain 'csrf_token'"

    # Validate csrf_token cookie is set
    cookies = response.cookies
    csrf_cookie = cookies.get("csrf_token")
    assert csrf_cookie is not None, "csrf_token cookie not set in response"

test_get_v1_csrf_token_should_set_csrf_token_cookie()
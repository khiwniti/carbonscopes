import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_get_v1_health_should_return_status_ok():
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        body = response.json()
    except ValueError:
        assert False, "Response body is not valid JSON"

    assert isinstance(body, dict), "Response JSON is not an object"
    assert body.get("status") == "ok", f"Expected body to have status 'ok', got {body}"


test_get_v1_health_should_return_status_ok()
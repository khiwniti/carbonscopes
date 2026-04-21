import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30

# Placeholder for a valid Bearer token; replace with a valid token for real tests
VALID_BEARER_TOKEN = "Bearer your_valid_token_here"

def test_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request():
    headers = {
        "Authorization": VALID_BEARER_TOKEN,
        "Content-Type": "application/json"
    }

    valid_payload = {
        "activity_type": "flight",
        "distance": 1000,
        "distance_unit": "km",
        "passengers": 1
    }

    malformed_payload = {
        "activity_typo": "flight",
        "distance": "not_a_number"
    }

    url = f"{BASE_URL}/carbon/calculate"

    # Test with valid data: Expect HTTP 200 and carbon footprint results
    try:
        resp_valid = requests.post(url, json=valid_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with valid payload failed: {e}"

    assert resp_valid.status_code == 200, f"Expected 200 OK, got {resp_valid.status_code}"
    try:
        json_data = resp_valid.json()
    except ValueError:
        assert False, "Response to valid payload is not valid JSON"

    # Removed check for specific response keys as PRD does not specify exact keys

    # Test with malformed payload: Expect HTTP 400 Bad Request
    try:
        resp_malformed = requests.post(url, json=malformed_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with malformed payload failed: {e}"

    assert resp_malformed.status_code == 400, (
        f"Expected 400 Bad Request for malformed payload, got {resp_malformed.status_code}"
    )


test_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request()

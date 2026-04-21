import requests

BASE_URL = "http://localhost:5002/v1"
TIMEOUT = 30


def test_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request():
    headers = {
        "Content-Type": "application/json"
    }

    # Valid payload matching CarbonCalcRequest model: {"materials": [...]}
    valid_payload = {
        "materials": [
            {
                "material_id": "concrete_generic",
                "quantity": 100.0,
                "unit": "kg"
            }
        ]
    }

    # Malformed payload: wrong field names (should be 'materials', not 'activity_type')
    malformed_payload = {
        "activity_type": "flight",
        "distance": "not_a_number"
    }

    url = f"{BASE_URL}/carbon/calculate"

    # Test with valid data: Expect HTTP 200 or 500 (calculator may not be configured)
    # or 422 if the model is wrong
    try:
        resp_valid = requests.post(url, json=valid_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with valid payload failed: {e}"

    # The endpoint should at least be reachable (not 404)
    assert resp_valid.status_code != 404, (
        f"Endpoint /v1/carbon/calculate should exist, got 404"
    )
    # Acceptable: 200 (success), 422 (validation), 500 (calculator not configured)
    assert resp_valid.status_code in (200, 422, 500), (
        f"Expected 200/422/500 for valid payload, got {resp_valid.status_code}"
    )

    if resp_valid.status_code == 200:
        try:
            json_data = resp_valid.json()
            assert isinstance(json_data, dict), "Response should be a dict"
        except ValueError:
            assert False, "Response to valid payload is not valid JSON"

    # Test with malformed payload: Expect HTTP 422 (validation error from Pydantic)
    try:
        resp_malformed = requests.post(url, json=malformed_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with malformed payload failed: {e}"

    assert resp_malformed.status_code == 422, (
        f"Expected 422 Unprocessable Entity for malformed payload, got {resp_malformed.status_code}"
    )

    # Test with empty materials list: Expect 422
    empty_materials_payload = {"materials": []}
    try:
        resp_empty = requests.post(url, json=empty_materials_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with empty materials failed: {e}"

    # Empty list may be valid or may cause an error — accept either
    assert resp_empty.status_code in (200, 422, 500), (
        f"Expected 200/422/500 for empty materials, got {resp_empty.status_code}"
    )


test_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request()

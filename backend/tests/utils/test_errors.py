"""
Unit tests for core/utils/errors.py (#119 — Error format enforcement)
Verifies all error helpers return consistent shapes and correct HTTP status codes.
"""
import pytest
from fastapi import HTTPException
from core.utils.errors import (
    bad_request,
    invalid_input,
    unauthorised,
    forbidden,
    not_found,
    conflict,
    unprocessable,
    rate_limited,
    internal_error,
    service_unavailable,
)


def get_error_body(exc: HTTPException) -> dict:
    """Extract the inner error dict from the HTTPException detail."""
    assert isinstance(exc.detail, dict), f"detail must be dict, got {type(exc.detail)}"
    assert "error" in exc.detail, "detail must contain 'error' key"
    return exc.detail["error"]


class TestBadRequest:
    def test_status_code(self):
        exc = bad_request("bad input")
        assert exc.status_code == 400

    def test_default_code(self):
        body = get_error_body(bad_request("bad input"))
        assert body["code"] == "BAD_REQUEST"

    def test_custom_code(self):
        body = get_error_body(bad_request("bad", code="CUSTOM_CODE"))
        assert body["code"] == "CUSTOM_CODE"

    def test_message_present(self):
        body = get_error_body(bad_request("something wrong"))
        assert body["message"] == "something wrong"

    def test_optional_details(self):
        body = get_error_body(bad_request("err", details={"field": "x"}))
        assert body["details"] == {"field": "x"}


class TestInvalidInput:
    def test_status_code(self):
        assert invalid_input("email", "invalid format").status_code == 400

    def test_code_is_invalid_input(self):
        body = get_error_body(invalid_input("email", "bad"))
        assert body["code"] == "INVALID_INPUT"

    def test_details_contains_field(self):
        body = get_error_body(invalid_input("user_id", "must be UUID"))
        assert body["details"]["field"] == "user_id"
        assert body["details"]["reason"] == "must be UUID"


class TestUnauthorised:
    def test_status_code(self):
        assert unauthorised().status_code == 401

    def test_www_authenticate_header(self):
        exc = unauthorised()
        assert "WWW-Authenticate" in exc.headers

    def test_code(self):
        assert get_error_body(unauthorised())["code"] == "UNAUTHORISED"


class TestForbidden:
    def test_status_code(self):
        assert forbidden().status_code == 403

    def test_code(self):
        assert get_error_body(forbidden())["code"] == "FORBIDDEN"


class TestNotFound:
    def test_status_code(self):
        assert not_found("Project").status_code == 404

    def test_message_includes_resource(self):
        body = get_error_body(not_found("Project"))
        assert "Project" in body["message"]

    def test_message_includes_id_when_provided(self):
        body = get_error_body(not_found("Project", "abc-123"))
        assert "abc-123" in body["message"]

    def test_details_resource(self):
        body = get_error_body(not_found("Thread", "t-1"))
        assert body["details"]["resource"] == "Thread"
        assert body["details"]["id"] == "t-1"


class TestConflict:
    def test_status_code(self):
        assert conflict("already exists").status_code == 409

    def test_code(self):
        assert get_error_body(conflict("x"))["code"] == "CONFLICT"


class TestUnprocessable:
    def test_status_code(self):
        assert unprocessable("invalid data").status_code == 422

    def test_code(self):
        assert get_error_body(unprocessable("x"))["code"] == "UNPROCESSABLE"


class TestRateLimited:
    def test_status_code(self):
        assert rate_limited().status_code == 429

    def test_retry_after_header(self):
        exc = rate_limited()
        assert "Retry-After" in exc.headers

    def test_code(self):
        assert get_error_body(rate_limited())["code"] == "RATE_LIMITED"


class TestInternalError:
    def test_status_code(self):
        assert internal_error().status_code == 500

    def test_code(self):
        assert get_error_body(internal_error())["code"] == "INTERNAL_ERROR"


class TestServiceUnavailable:
    def test_status_code(self):
        assert service_unavailable("GraphDB").status_code == 503

    def test_message_includes_service_name(self):
        body = get_error_body(service_unavailable("GraphDB"))
        assert "GraphDB" in body["message"]

    def test_code(self):
        assert get_error_body(service_unavailable("Redis"))["code"] == "SERVICE_UNAVAILABLE"


class TestErrorShapeConsistency:
    """Verify ALL error helpers produce consistent shape."""

    all_errors = [
        bad_request("x"),
        invalid_input("f", "r"),
        unauthorised(),
        forbidden(),
        not_found("R"),
        conflict("x"),
        unprocessable("x"),
        rate_limited(),
        internal_error(),
        service_unavailable("svc"),
    ]

    def test_all_have_error_key(self):
        for exc in self.all_errors:
            assert isinstance(exc.detail, dict), f"{exc} detail is not dict"
            assert "error" in exc.detail, f"{exc} missing 'error' key"

    def test_all_have_code_and_message(self):
        for exc in self.all_errors:
            body = exc.detail["error"]
            assert "code" in body, f"{exc} missing 'code'"
            assert "message" in body, f"{exc} missing 'message'"
            assert isinstance(body["code"], str)
            assert isinstance(body["message"], str)
            assert len(body["code"]) > 0
            assert len(body["message"]) > 0

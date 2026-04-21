"""Tests for Rate Limiting and CSRF Protection.

Validates:
- Rate limiting on auth endpoints (Task #114)
- CSRF middleware behavior (Task #111)

Requirements: SEC-04 (rate limiting), SEC-05 (CSRF protection)
"""

import pytest
from fastapi import FastAPI, Request, APIRouter
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from core.middleware.rate_limit import (
    limiter,
    AUTH_RATE_LIMIT,
    API_KEY_RATE_LIMIT,
    DEFAULT_RATE_LIMIT,
    rate_limit_exceeded_handler,
    get_client_identifier,
)
from core.middleware.csrf import (
    CSRFMiddleware,
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    generate_csrf_token,
    is_exempt_from_csrf,
    _constant_time_compare,
)


# ============================================================
# Rate Limiting Tests (Task #114)
# ============================================================


class TestRateLimitConfiguration:
    """Validate rate limit configuration."""

    def test_auth_rate_limit_default(self):
        """AUTH_RATE_LIMIT should default to 5/15minutes."""
        assert AUTH_RATE_LIMIT == "5/15minutes" or AUTH_RATE_LIMIT == os.getenv("AUTH_RATE_LIMIT", "5/15minutes")

    def test_api_key_rate_limit_default(self):
        """API_KEY_RATE_LIMIT should default to 5/15minutes."""
        assert API_KEY_RATE_LIMIT == "5/15minutes" or API_KEY_RATE_LIMIT == os.getenv("API_KEY_RATE_LIMIT", "5/15minutes")

    def test_default_rate_limit_default(self):
        """DEFAULT_RATE_LIMIT should default to 100/minute."""
        assert DEFAULT_RATE_LIMIT == "100/minute" or DEFAULT_RATE_LIMIT == os.getenv("DEFAULT_RATE_LIMIT", "100/minute")

    def test_limiter_initialized(self):
        """Limiter should be initialized with storage."""
        assert limiter is not None

    def test_get_client_identifier_with_forwarded_for(self):
        """Client identifier should use X-Forwarded-For header when present."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "203.0.113.50, 70.41.3.18"
        mock_request.client = None

        identifier = get_client_identifier(mock_request)
        assert identifier == "203.0.113.50"

    def test_get_client_identifier_without_forwarded_for(self):
        """Client identifier should fall back to remote address."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "127.0.0.1"

        identifier = get_client_identifier(mock_request)
        assert identifier == "127.0.0.1"


class TestRateLimitExceededHandler:
    """Validate rate limit exceeded error handling."""

    @pytest.mark.asyncio
    async def test_handler_returns_429(self):
        """Rate limit exceeded should return 429 status code."""
        mock_request = MagicMock()
        mock_request.url.path = "/v1/auth/otp/send"
        mock_request.headers.get.return_value = "127.0.0.1"

        exc = MagicMock()
        exc.detail = "5 per 15 minutes. Retry after 15 minutes"

        with patch(
            "core.middleware.rate_limit.get_client_identifier",
            return_value="127.0.0.1",
        ):
            response = await rate_limit_exceeded_handler(mock_request, exc)

        assert response.status_code == 429
        assert "rate_limit_exceeded" in response.body.decode()

    @pytest.mark.asyncio
    async def test_handler_includes_retry_after(self):
        """Rate limit response should include Retry-After header."""
        mock_request = MagicMock()
        mock_request.url.path = "/v1/auth/otp/send"
        mock_request.headers.get.return_value = "127.0.0.1"

        exc = MagicMock()
        exc.detail = "5 per 15 minutes. Retry after 15 minutes"

        with patch(
            "core.middleware.rate_limit.get_client_identifier",
            return_value="127.0.0.1",
        ):
            response = await rate_limit_exceeded_handler(mock_request, exc)

        assert "Retry-After" in response.headers


class TestAuthAPIRateLimiting:
    """Validate rate limiting is applied to auth API endpoints."""

    def test_auth_api_module_exists(self):
        """Auth API module should exist and have router."""
        from auth.api import router

        assert router is not None
        assert router.prefix == ""  # No prefix, mounted at /v1

    def test_auth_api_has_send_otp_endpoint(self):
        """Auth API should have OTP send endpoint."""
        from auth.api import router

        routes = [r.path for r in router.routes]
        assert "/auth/otp/send" in routes

    def test_auth_api_has_verify_otp_endpoint(self):
        """Auth API should have OTP verify endpoint."""
        from auth.api import router

        routes = [r.path for r in router.routes]
        assert "/auth/otp/verify" in routes


# ============================================================
# CSRF Protection Tests (Task #111)
# ============================================================


class TestCSRFTokenGeneration:
    """Validate CSRF token generation."""

    def test_generate_csrf_token_length(self):
        """CSRF token should be the expected length."""
        token = generate_csrf_token()
        assert len(token) == 64  # 32 bytes = 64 hex chars

    def test_generate_csrf_token_uniqueness(self):
        """Each CSRF token should be unique."""
        tokens = {generate_csrf_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_generate_csrf_token_hex(self):
        """CSRF token should be a valid hex string."""
        token = generate_csrf_token()
        int(token, 16)  # Should not raise ValueError


class TestCSRFConstantTimeCompare:
    """Validate constant-time comparison."""

    def test_matching_strings(self):
        """Matching strings should return True."""
        assert _constant_time_compare("abc", "abc") is True

    def test_non_matching_strings(self):
        """Non-matching strings should return False."""
        assert _constant_time_compare("abc", "def") is False

    def test_different_length_strings(self):
        """Strings of different lengths should return False."""
        assert _constant_time_compare("abc", "abcd") is False

    def test_empty_strings(self):
        """Empty strings should match."""
        assert _constant_time_compare("", "") is True


class TestCSRFExemptions:
    """Validate CSRF exemption logic."""

    def _make_request(self, method="POST", path="/v1/test", headers=None, cookies=None):
        """Create a mock request for CSRF exemption testing."""
        mock_request = MagicMock(spec=Request)
        mock_request.method = method
        mock_request.url = MagicMock()
        mock_request.url.path = path
        mock_request.headers = headers or {}
        mock_request.cookies = cookies or {}
        return mock_request

    def test_safe_methods_exempt(self):
        """GET, HEAD, OPTIONS, TRACE should be exempt from CSRF."""
        for method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            request = self._make_request(method=method)
            assert is_exempt_from_csrf(request) is True, f"{method} should be exempt"

    def test_post_not_exempt_by_default(self):
        """POST without auth headers should not be exempt."""
        request = self._make_request(method="POST", path="/v1/some-endpoint")
        assert is_exempt_from_csrf(request) is False

    def test_bearer_token_exempt(self):
        """POST with Authorization header should be exempt."""
        request = self._make_request(
            method="POST",
            path="/v1/some-endpoint",
            headers={"Authorization": "Bearer test-token"},
        )
        assert is_exempt_from_csrf(request) is True

    def test_api_key_exempt(self):
        """POST with X-API-Key header should be exempt."""
        request = self._make_request(
            method="POST",
            path="/v1/some-endpoint",
            headers={"X-API-Key": "test-key"},
        )
        assert is_exempt_from_csrf(request) is True

    def test_webhook_paths_exempt(self):
        """Webhook paths should be exempt from CSRF."""
        request = self._make_request(
            method="POST",
            path="/v1/webhooks/user-created",
        )
        assert is_exempt_from_csrf(request) is True

    def test_health_endpoints_exempt(self):
        """Health check endpoints should be exempt."""
        for path in ["/v1/health", "/v1/health-docker"]:
            request = self._make_request(method="GET", path=path)
            assert is_exempt_from_csrf(request) is True

    def test_docs_endpoints_exempt(self):
        """API docs endpoints should be exempt."""
        for path in ["/v1/docs", "/v1/openapi.json", "/v1/redoc"]:
            request = self._make_request(method="GET", path=path)
            assert is_exempt_from_csrf(request) is True

    def test_put_not_exempt_without_auth(self):
        """PUT without auth headers should not be exempt."""
        request = self._make_request(method="PUT", path="/v1/some-endpoint")
        assert is_exempt_from_csrf(request) is False

    def test_delete_not_exempt_without_auth(self):
        """DELETE without auth headers should not be exempt."""
        request = self._make_request(method="DELETE", path="/v1/some-endpoint")
        assert is_exempt_from_csrf(request) is False

    def test_patch_not_exempt_without_auth(self):
        """PATCH without auth headers should not be exempt."""
        request = self._make_request(method="PATCH", path="/v1/some-endpoint")
        assert is_exempt_from_csrf(request) is False


class TestCSRFMiddleware:
    """Validate CSRF middleware behavior with a test app."""

    def _create_test_app(self):
        """Create a test FastAPI app with CSRF middleware."""
        app = FastAPI()

        @app.get("/csrf-token")
        async def get_csrf_token():
            from core.middleware.csrf import generate_csrf_token
            return {"csrf_token": generate_csrf_token()}

        @app.post("/protected")
        async def protected_endpoint():
            return {"message": "success"}

        @app.post("/api-endpoint")
        async def api_endpoint():
            return {"message": "api success"}

        app.add_middleware(CSRFMiddleware)

        return app

    def test_get_requests_pass_without_csrf(self):
        """GET requests should pass without CSRF token."""
        app = self._create_test_app()
        client = TestClient(app)
        response = client.get("/csrf-token")
        assert response.status_code == 200

    def test_post_without_csrf_rejected(self):
        """POST without CSRF token should be rejected with 403."""
        app = self._create_test_app()
        # Override exemption for Bearer tokens in this test
        client = TestClient(app)
        response = client.post("/protected")
        assert response.status_code == 403

    def test_post_with_bearer_token_passes(self):
        """POST with Authorization header should bypass CSRF."""
        app = self._create_test_app()
        client = TestClient(app)
        response = client.post(
            "/api-endpoint",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200

    def test_post_with_matching_csrf_token_passes(self):
        """POST with matching CSRF cookie and header should pass."""
        app = self._create_test_app()
        client = TestClient(app)

        # Get CSRF token from cookie
        token = generate_csrf_token()

        response = client.post(
            "/protected",
            headers={CSRF_HEADER_NAME: token},
            cookies={CSRF_COOKIE_NAME: token},
        )
        assert response.status_code == 200

    def test_post_with_mismatched_csrf_token_rejected(self):
        """POST with mismatched CSRF cookie and header should be rejected."""
        app = self._create_test_app()
        client = TestClient(app)

        response = client.post(
            "/protected",
            headers={CSRF_HEADER_NAME: "token-a"},
            cookies={CSRF_COOKIE_NAME: "token-b"},
        )
        assert response.status_code == 403


# ============================================================
# Integration Tests
# ============================================================


class TestOTPFlow:
    """Validate OTP send and verify flow."""

    def test_otp_send_endpoint_exists(self):
        """OTP send endpoint should exist in auth router."""
        from auth.api import router

        route_names = [r.name for r in router.routes]
        assert "send_otp" in route_names

    def test_otp_verify_endpoint_exists(self):
        """OTP verify endpoint should exist in auth router."""
        from auth.api import router

        route_names = [r.name for r in router.routes]
        assert "verify_otp" in route_names

    def test_otp_store_cleanup(self):
        """OTP store should clean up expired entries."""
        from auth.api import _otp_store, _cleanup_expired_otps
        import time

        # Add an expired entry
        _otp_store["test@example.com"] = {
            "otp": "123456",
            "expires_at": time.time() - 1,  # Expired
            "attempts": 0,
        }

        _cleanup_expired_otps()

        assert "test@example.com" not in _otp_store

    def test_otp_generation_format(self):
        """OTP code should be 6 digits."""
        from auth.api import _generate_otp

        for _ in range(100):
            otp = _generate_otp()
            assert len(otp) == 6
            assert otp.isdigit()


if __name__ == "__main__":
    import os
    pytest.main([__file__, "-v"])
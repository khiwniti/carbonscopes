"""CSRF Protection Middleware for FastAPI.

Implements the double-submit cookie pattern to protect against
Cross-Site Request Forgery (CSRF) attacks.

Strategy:
- For state-changing requests (POST/PUT/DELETE/PATCH), validate that
  the CSRF token in the cookie matches the token in the header.
- Exempt requests that carry valid Bearer tokens or API keys, since
  these are already protected by CORS and authentication.
- Generate CSRF tokens via a dedicated endpoint.

Task #111: CSRF protection for all state-changing endpoints.
"""

import os
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException
from typing import Set

from core.utils.logger import logger

# Configuration
CSRF_COOKIE_NAME = os.getenv("CSRF_COOKIE_NAME", "csrf_token")
CSRF_HEADER_NAME = os.getenv("CSRF_HEADER_NAME", "X-CSRF-Token")
CSRF_TOKEN_LENGTH = int(os.getenv("CSRF_TOKEN_LENGTH", "32"))
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "false").lower() == "true"
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "lax")
CSRF_COOKIE_DOMAIN = os.getenv("CSRF_COOKIE_DOMAIN", None)
CSRF_ENABLED = os.getenv("CSRF_ENABLED", "true").lower() == "true"

# HTTP methods that are safe (no state changes) and don't need CSRF protection
SAFE_METHODS: Set[str] = {"GET", "HEAD", "OPTIONS", "TRACE"}

# Paths that are exempt from CSRF validation
# These are typically API endpoints that use Bearer token auth
# or webhooks that have their own authentication mechanism
CSRF_EXEMPT_PATHS: Set[str] = {
    "/v1/docs",
    "/v1/openapi.json",
    "/v1/redoc",
}

# Path prefixes that are exempt (e.g., webhook endpoints with own auth)
CSRF_EXEMPT_PREFIXES: Set[str] = {
    "/v1/webhooks/",
}

# Headers that indicate the request is API-based (not browser form submission)
# If any of these headers are present, CSRF check is skipped
API_AUTH_HEADERS: Set[str] = {
    "Authorization",   # Bearer token auth
    "X-API-Key",       # API key auth
}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_hex(CSRF_TOKEN_LENGTH)


def is_exempt_from_csrf(request: Request) -> bool:
    """
    Check if a request is exempt from CSRF validation.

    Exemptions apply to:
    1. Safe HTTP methods (GET, HEAD, OPTIONS, TRACE)
    2. Requests with Authorization or API key headers (already authenticated)
    3. Explicitly exempt paths and prefixes
    4. Webhook endpoints (have their own auth)
    5. Health check endpoints
    6. Static files

    Args:
        request: The incoming request

    Returns:
        True if the request is exempt from CSRF validation
    """
    # Safe methods don't need CSRF protection
    if request.method in SAFE_METHODS:
        return True

    # Check for API authentication headers — these requests are already
    # protected by CORS policy and authentication, so CSRF is not needed
    for header_name in API_AUTH_HEADERS:
        if request.headers.get(header_name):
            return True

    # Check exact path exemptions
    path = request.url.path
    if path in CSRF_EXEMPT_PATHS:
        return True

    # Check prefix exemptions
    for prefix in CSRF_EXEMPT_PREFIXES:
        if path.startswith(prefix):
            return True

    # Health check endpoints
    if path in ("/v1/health", "/v1/health-docker"):
        return True

    # Content-Type check: API requests with JSON content are typically
    # from JavaScript (not form submissions), which are protected by CORS.
    # However, we still validate CSRF for these to be extra safe —
    # only skip for explicitly authenticated requests.
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        # JSON requests with auth headers are already exempt above
        # JSON requests without auth still need CSRF validation
        pass

    return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware using the double-submit cookie pattern.

    On state-changing requests (POST, PUT, DELETE, PATCH):
    1. Check if the request is exempt (has auth headers, is a webhook, etc.)
    2. If not exempt, validate that the CSRF token cookie matches the header
    3. If validation fails, return 403 Forbidden

    On the CSRF token endpoint (GET /v1/csrf-token):
    1. Generate a new CSRF token
    2. Set it as a cookie and return it in the response body
    """

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF if disabled
        if not CSRF_ENABLED:
            return await call_next(request)

        # Handle the CSRF token generation endpoint
        if request.url.path == "/v1/csrf-token" and request.method == "GET":
            response = await call_next(request)
            token = generate_csrf_token()
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=token,
                secure=CSRF_COOKIE_SECURE,
                httponly=False,  # Must be readable by JavaScript
                samesite=CSRF_COOKIE_SAMESITE,
                domain=CSRF_COOKIE_DOMAIN,
                path="/",
                max_age=86400,  # 24 hours
            )
            return response

        # For state-changing requests, validate CSRF token
        if request.method not in SAFE_METHODS and not is_exempt_from_csrf(request):
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
            header_token = request.headers.get(CSRF_HEADER_NAME)

            if not cookie_token or not header_token:
                logger.warning(
                    f"CSRF validation failed: missing token. "
                    f"cookie={'present' if cookie_token else 'missing'}, "
                    f"header={'present' if header_token else 'missing'}, "
                    f"path={request.url.path}, method={request.method}"
                )
                return Response(
                    content='{"detail":"CSRF token missing. Include X-CSRF-Token header and csrf_token cookie."}',
                    status_code=403,
                    media_type="application/json",
                )

            # Constant-time comparison to prevent timing attacks
            if not _constant_time_compare(cookie_token, header_token):
                logger.warning(
                    f"CSRF validation failed: token mismatch. "
                    f"path={request.url.path}, method={request.method}"
                )
                return Response(
                    content='{"detail":"CSRF token mismatch."}',
                    status_code=403,
                    media_type="application/json",
                )

        return await call_next(request)


def _constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


__all__ = [
    "CSRFMiddleware",
    "CSRF_COOKIE_NAME",
    "CSRF_HEADER_NAME",
    "generate_csrf_token",
    "is_exempt_from_csrf",
]
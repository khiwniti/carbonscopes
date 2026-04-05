"""
Rate Limiting Middleware for FastAPI

Provides configurable rate limiting for authentication and sensitive endpoints
to prevent brute force attacks and abuse.

Uses slowapi with Redis backend (if available) or in-memory storage as fallback.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from core.utils.logger import logger


# Rate limit configuration from environment variables
# Format: "number/period" e.g., "5/15minutes", "10/hour", "100/day"
AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "5/15minutes")
API_KEY_RATE_LIMIT = os.getenv("API_KEY_RATE_LIMIT", "5/15minutes")
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "100/minute")

# Redis configuration for distributed rate limiting
REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL") or os.getenv("REDIS_URL")


def get_storage_uri() -> str:
    """
    Get storage URI for rate limiter.

    Returns:
        Redis URL if available, otherwise "memory://" for in-memory storage
    """
    if REDIS_URL:
        logger.info("Rate limiter using Redis storage for distributed limiting")
        return REDIS_URL
    else:
        logger.warning(
            "Rate limiter using in-memory storage (not suitable for multi-instance deployments)"
        )
        return "memory://"


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Uses IP address as the primary identifier. In production, you may want to
    also consider:
    - X-Forwarded-For header (if behind proxy)
    - API key or user ID (for authenticated requests)
    - Combination of multiple factors

    Args:
        request: FastAPI request object

    Returns:
        Client identifier string (IP address)
    """
    # Check for X-Forwarded-For header (common when behind load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        client_ip = forwarded_for.split(",")[0].strip()
        return client_ip

    # Fallback to direct remote address
    return get_remote_address(request)


# Initialize the limiter with Redis or in-memory storage
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=get_storage_uri(),
    strategy="fixed-window",  # or "moving-window" for more accurate limiting
    headers_enabled=True,  # Add rate limit info to response headers
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Returns a 429 Too Many Requests response with retry-after information.

    Args:
        request: The request that exceeded the rate limit
        exc: The RateLimitExceeded exception

    Returns:
        JSONResponse with 429 status code and retry-after header
    """
    retry_after = exc.detail.split("Retry after ")[1] if "Retry after" in exc.detail else "unknown"

    response = JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": retry_after,
        },
    )

    # Add Retry-After header (in seconds)
    if retry_after != "unknown":
        try:
            # Parse retry_after time and convert to seconds
            # slowapi format is like "15 minutes" or "1 hour"
            parts = retry_after.split()
            if len(parts) == 2:
                value, unit = int(parts[0]), parts[1]
                if "second" in unit:
                    seconds = value
                elif "minute" in unit:
                    seconds = value * 60
                elif "hour" in unit:
                    seconds = value * 3600
                elif "day" in unit:
                    seconds = value * 86400
                else:
                    seconds = 60  # default to 1 minute

                response.headers["Retry-After"] = str(seconds)
        except Exception as e:
            logger.warning(f"Failed to parse retry_after time: {e}")
            response.headers["Retry-After"] = "900"  # 15 minutes default

    logger.warning(
        f"Rate limit exceeded for {get_client_identifier(request)} on {request.url.path}"
    )

    return response


# Export limiter and rate limit strings for use in endpoints
__all__ = [
    "limiter",
    "AUTH_RATE_LIMIT",
    "API_KEY_RATE_LIMIT",
    "DEFAULT_RATE_LIMIT",
    "rate_limit_exceeded_handler",
]

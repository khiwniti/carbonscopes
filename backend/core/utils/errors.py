"""
Standardised API error helpers.

All endpoints should use these helpers to ensure consistent
error response shapes across the entire API.

Error response shape:
    {
        "error": {
            "code": "SNAKE_CASE_CODE",
            "message": "Human-readable description",
            "details": {...}   # optional extra context
        }
    }
"""

from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status


def _err(code: str, message: str, details: dict | None = None) -> dict:
    body: dict[str, Any] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return {"error": body}


# ── 400 Bad Request ──────────────────────────────────────────────────────────

def bad_request(message: str, code: str = "BAD_REQUEST", details: dict | None = None) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_err(code, message, details))


def invalid_input(field: str, reason: str) -> HTTPException:
    return bad_request(
        message=f"Invalid value for '{field}': {reason}",
        code="INVALID_INPUT",
        details={"field": field, "reason": reason},
    )


# ── 401 Unauthorised ─────────────────────────────────────────────────────────

def unauthorised(message: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_err("UNAUTHORISED", message),
        headers={"WWW-Authenticate": "Bearer"},
    )


# ── 403 Forbidden ────────────────────────────────────────────────────────────

def forbidden(message: str = "Access denied") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_err("FORBIDDEN", message))


# ── 404 Not Found ────────────────────────────────────────────────────────────

def not_found(resource: str, resource_id: str | None = None) -> HTTPException:
    msg = f"{resource} not found"
    if resource_id:
        msg = f"{resource} '{resource_id}' not found"
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=_err("NOT_FOUND", msg, {"resource": resource, "id": resource_id} if resource_id else {"resource": resource}),
    )


# ── 409 Conflict ─────────────────────────────────────────────────────────────

def conflict(message: str, code: str = "CONFLICT") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_err(code, message))


# ── 422 Unprocessable ────────────────────────────────────────────────────────

def unprocessable(message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=_err("UNPROCESSABLE", message, details),
    )


# ── 429 Rate Limited ─────────────────────────────────────────────────────────

def rate_limited(message: str = "Too many requests") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=_err("RATE_LIMITED", message),
        headers={"Retry-After": "60"},
    )


# ── 500 Internal ─────────────────────────────────────────────────────────────

def internal_error(message: str = "An unexpected error occurred") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=_err("INTERNAL_ERROR", message),
    )


# ── 503 Unavailable ──────────────────────────────────────────────────────────

def service_unavailable(service: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=_err("SERVICE_UNAVAILABLE", f"{service} is currently unavailable"),
    )

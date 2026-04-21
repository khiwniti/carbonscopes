"""Auth API — OTP verification for expired magic links.

Provides a rate-limited endpoint for users whose magic link has expired
to verify their identity via a one-time password sent to their email.

Task #114: Rate limiting applied to prevent brute force attacks.
"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel, EmailStr

from core.middleware.rate_limit import limiter, AUTH_RATE_LIMIT
from core.services.supabase import DBConnection
from core.utils.logger import logger

router = APIRouter(tags=["auth"])


class OTPRequest(BaseModel):
    """Request body for OTP verification."""
    email: EmailStr
    otp_code: str


class OTPSendRequest(BaseModel):
    """Request body for requesting a new OTP."""
    email: EmailStr


class OTPResponse(BaseModel):
    """Response for OTP operations."""
    success: bool
    message: str


# In-memory OTP store for development (use Redis in production)
# Key: email, Value: {"otp": str, "expires_at": float, "attempts": int}
_otp_store: dict = {}

OTP_EXPIRY_SECONDS = 3600  # 1 hour
MAX_OTP_ATTEMPTS = 5


def _generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return f"{secrets.randbelow(1000000):06d}"


def _cleanup_expired_otps() -> None:
    """Remove expired OTP entries from the store."""
    now = time.time()
    expired = [k for k, v in _otp_store.items() if v["expires_at"] < now]
    for k in expired:
        _otp_store.pop(k, None)


import time  # noqa: E402 — needed for _cleanup_expired_otps


@router.post("/auth/otp/send", response_model=OTPResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def send_otp(
    request: Request,
    response: Response,
    req_body: OTPSendRequest,
) -> OTPResponse:
    """
    Send a new OTP code to the user's email.

    Rate limited to 5 requests per 15 minutes per IP to prevent abuse.
    Used when a user's magic link has expired and they need an alternative
    way to verify their identity.

    Args:
        request: FastAPI request (required by slowapi for rate limiting)
        request: Email address to send OTP to

    Returns:
        OTPResponse indicating success
    """
    _cleanup_expired_otps()

    email = req_body.email.lower().strip()

    # Check if there's a recent OTP that hasn't expired yet
    if email in _otp_store:
        existing = _otp_store[email]
        remaining = existing["expires_at"] - time.time()
        if remaining > OTP_EXPIRY_SECONDS - 60:  # Less than 1 minute since creation
            return OTPResponse(
                success=True,
                message="OTP already sent recently. Please check your email.",
            )

    # Generate and store OTP
    otp_code = _generate_otp()
    _otp_store[email] = {
        "otp": otp_code,
        "expires_at": time.time() + OTP_EXPIRY_SECONDS,
        "attempts": 0,
    }

    # Send OTP via email service
    try:
        from core.services.email import email_service

        sent = email_service.send_otp_email(email, otp_code)
        if not sent:
            logger.warning(f"Failed to send OTP email to {email}")
            # Still return success to not reveal email delivery status
            # (prevents email enumeration)
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")

    logger.info(f"OTP requested for {email}")

    # Always return success to prevent email enumeration
    return OTPResponse(
        success=True,
        message="If an account exists with this email, an OTP has been sent.",
    )


@router.post("/auth/otp/verify", response_model=OTPResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def verify_otp(
    request: Request,
    response: Response,
    req_body: OTPRequest,
) -> OTPResponse:
    """
    Verify an OTP code for the given email.

    Rate limited to 5 requests per 15 minutes per IP.
    Maximum 5 verification attempts per OTP before it's invalidated.

    Args:
        request: FastAPI request (required by slowapi for rate limiting)
        request: Email and OTP code to verify

    Returns:
        OTPResponse indicating success or failure
    """
    _cleanup_expired_otps()

    email = req_body.email.lower().strip()
    otp_code = req_body.otp_code.strip()

    stored = _otp_store.get(email)

    if not stored:
        # Don't reveal whether email exists
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    # Check expiry
    if time.time() > stored["expires_at"]:
        _otp_store.pop(email, None)
        raise HTTPException(status_code=401, detail="OTP has expired. Please request a new one.")

    # Check max attempts
    if stored["attempts"] >= MAX_OTP_ATTEMPTS:
        _otp_store.pop(email, None)
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts. Please request a new OTP.",
        )

    # Increment attempt counter
    stored["attempts"] += 1

    # Verify OTP using constant-time comparison
    from core.utils.auth_utils import _constant_time_compare

    if not _constant_time_compare(otp_code, stored["otp"]):
        raise HTTPException(status_code=401, detail="Invalid OTP code.")

    # Success — remove OTP and authenticate user
    _otp_store.pop(email, None)

    try:
        db = DBConnection()
        client = await db.client

        # Look up user by email
        result = await client.table("accounts").select(
            "id, primary_owner_user_id"
        ).eq("personal_account", True).execute()

        # Find the user with matching email
        user_result = await client.auth.admin.list_users()

        matched_user = None
        for user in user_result.users:
            if user.email and user.email.lower() == email:
                matched_user = user
                break

        if not matched_user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"OTP verified successfully for {email}")

        return OTPResponse(
            success=True,
            message="OTP verified. You can now sign in.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during OTP verification: {e}")
        raise HTTPException(status_code=500, detail="Verification failed. Please try again.")
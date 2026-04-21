"""Authentication API module.

Provides OTP verification endpoint for expired magic links,
with rate limiting protection against brute force attacks.
"""

from .api import router

__all__ = ["router"]
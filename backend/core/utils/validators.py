"""
UUID and identifier validation utilities.

Use these validators in FastAPI endpoints to reject malformed IDs
before they reach the database, preventing SQL injection and crashes.
"""

import re
import uuid
from fastapi import HTTPException, status


# UUID4 regex pattern
_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE,
)


def is_valid_uuid(value: str) -> bool:
    """Return True if value is a valid UUID4 string."""
    if not value or not isinstance(value, str):
        return False
    return bool(_UUID_RE.match(value))


def validate_uuid(value: str, field_name: str = "id") -> str:
    """
    Validate and normalise a UUID string.

    Args:
        value: The string to validate.
        field_name: Human-readable field name for error messages.

    Returns:
        Lowercased UUID string.

    Raises:
        HTTPException 422 if the value is not a valid UUID.
    """
    if not value or not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field_name}: must be a non-empty string.",
        )
    normalised = value.strip().lower()
    if not _UUID_RE.match(normalised):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field_name}: '{value}' is not a valid UUID.",
        )
    return normalised


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def safe_uuid(value: str | None) -> str | None:
    """Return the UUID string if valid, else None (non-raising version)."""
    if value and is_valid_uuid(value):
        return value.strip().lower()
    return None

"""
Unit tests for core/utils/validators.py (#125 — UUID validation)
"""
import pytest
from fastapi import HTTPException
from core.utils.validators import (
    is_valid_uuid,
    validate_uuid,
    generate_uuid,
    safe_uuid,
)


class TestIsValidUuid:
    def test_valid_uuid4(self):
        assert is_valid_uuid("550e8400-e29b-41d4-a716-446655440000") is True

    def test_valid_uuid4_uppercase(self):
        assert is_valid_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_invalid_missing_hyphens(self):
        assert is_valid_uuid("550e8400e29b41d4a716446655440000") is False

    def test_invalid_too_short(self):
        assert is_valid_uuid("550e8400-e29b") is False

    def test_invalid_non_hex(self):
        assert is_valid_uuid("zzzzzzzz-zzzz-4zzz-azzz-zzzzzzzzzzzz") is False

    def test_empty_string(self):
        assert is_valid_uuid("") is False

    def test_none(self):
        assert is_valid_uuid(None) is False  # type: ignore

    def test_not_uuid4_version(self):
        # UUID1 (version 1) should fail (4xxx pattern required)
        assert is_valid_uuid("550e8400-e29b-11d4-a716-446655440000") is False

    def test_random_generated_uuid_is_valid(self):
        uid = generate_uuid()
        assert is_valid_uuid(uid) is True


class TestValidateUuid:
    def test_valid_uuid_returns_lowercase(self):
        uid = "550E8400-E29B-41D4-A716-446655440000"
        result = validate_uuid(uid)
        assert result == uid.lower()

    def test_invalid_uuid_raises_422(self):
        with pytest.raises(HTTPException) as exc:
            validate_uuid("not-a-uuid")
        assert exc.value.status_code == 422

    def test_empty_raises_422(self):
        with pytest.raises(HTTPException) as exc:
            validate_uuid("")
        assert exc.value.status_code == 422

    def test_none_raises_422(self):
        with pytest.raises(HTTPException) as exc:
            validate_uuid(None)  # type: ignore
        assert exc.value.status_code == 422

    def test_custom_field_name_in_error(self):
        with pytest.raises(HTTPException) as exc:
            validate_uuid("bad", field_name="project_id")
        assert "project_id" in str(exc.value.detail)

    def test_strips_whitespace(self):
        uid = "  550e8400-e29b-41d4-a716-446655440000  "
        result = validate_uuid(uid)
        assert result == uid.strip().lower()


class TestGenerateUuid:
    def test_generates_valid_uuid(self):
        uid = generate_uuid()
        assert is_valid_uuid(uid)

    def test_generates_unique_uuids(self):
        uids = {generate_uuid() for _ in range(100)}
        assert len(uids) == 100

    def test_returns_string(self):
        assert isinstance(generate_uuid(), str)


class TestSafeUuid:
    def test_valid_returns_lowercase(self):
        uid = "550E8400-E29B-41D4-A716-446655440000"
        assert safe_uuid(uid) == uid.lower()

    def test_invalid_returns_none(self):
        assert safe_uuid("not-valid") is None

    def test_none_returns_none(self):
        assert safe_uuid(None) is None

    def test_empty_returns_none(self):
        assert safe_uuid("") is None

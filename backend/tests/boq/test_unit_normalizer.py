"""
Unit tests for Thai unit normalization.
"""

import pytest
from decimal import Decimal
from boq.unit_normalizer import normalize_unit, get_unit_category


def test_normalize_volume_units():
    """Test volume unit normalization."""
    assert normalize_unit('ลบ.ม.') == ('m³', Decimal('1.0'))
    assert normalize_unit('cubic meter') == ('m³', Decimal('1.0'))
    assert normalize_unit('ลบ.เมตร') == ('m³', Decimal('1.0'))


def test_normalize_weight_units():
    """Test weight unit normalization."""
    assert normalize_unit('กก.') == ('kg', Decimal('1.0'))
    assert normalize_unit('ตัน') == ('kg', Decimal('1000.0'))
    assert normalize_unit('ton') == ('kg', Decimal('1000.0'))
    assert normalize_unit('tonne') == ('kg', Decimal('1000.0'))


def test_normalize_area_units():
    """Test area unit normalization."""
    assert normalize_unit('ตร.ม.') == ('m²', Decimal('1.0'))
    assert normalize_unit('square meter') == ('m²', Decimal('1.0'))
    assert normalize_unit('ตร.เมตร') == ('m²', Decimal('1.0'))


def test_normalize_length_units():
    """Test length unit normalization."""
    assert normalize_unit('ม.') == ('m', Decimal('1.0'))
    assert normalize_unit('meter') == ('m', Decimal('1.0'))
    assert normalize_unit('เมตร') == ('m', Decimal('1.0'))


def test_normalize_count_units():
    """Test count unit normalization."""
    assert normalize_unit('เส้น') == ('unit', Decimal('1.0'))
    assert normalize_unit('piece') == ('unit', Decimal('1.0'))
    assert normalize_unit('ชุด') == ('unit', Decimal('1.0'))
    assert normalize_unit('set') == ('unit', Decimal('1.0'))


def test_normalize_case_insensitive():
    """Test case-insensitive matching."""
    assert normalize_unit('KILOGRAM') == ('kg', Decimal('1.0'))
    assert normalize_unit('Cubic Meter') == ('m³', Decimal('1.0'))


def test_normalize_with_whitespace():
    """Test normalization with leading/trailing whitespace."""
    assert normalize_unit('  กก.  ') == ('kg', Decimal('1.0'))
    assert normalize_unit(' ตัน ') == ('kg', Decimal('1000.0'))


def test_normalize_unrecognized_unit():
    """Test error handling for unrecognized units."""
    with pytest.raises(ValueError, match="Unrecognized unit"):
        normalize_unit('invalid_unit')

    with pytest.raises(ValueError, match="Unrecognized unit"):
        normalize_unit('xyz')


def test_get_unit_category():
    """Test unit categorization."""
    assert get_unit_category('m³') == 'volume'
    assert get_unit_category('kg') == 'weight'
    assert get_unit_category('m²') == 'area'
    assert get_unit_category('m') == 'length'
    assert get_unit_category('unit') == 'count'
    assert get_unit_category('unknown_unit') == 'unknown'


def test_conversion_factor_type():
    """Test that conversion factors are Decimal, not float."""
    unit, factor = normalize_unit('ตัน')
    assert isinstance(factor, Decimal)
    assert factor == Decimal('1000.0')

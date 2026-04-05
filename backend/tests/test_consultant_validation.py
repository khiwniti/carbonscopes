import pytest
from decimal import Decimal
from core.carbon.brightway.validation import percent_error


def test_percent_error_within_threshold():
    manual = Decimal("1000")
    automated = Decimal("1015")  # 1.5% error
    err = percent_error(automated, manual)
    assert err <= Decimal("2.0")


def test_percent_error_exceeds_threshold():
    manual = Decimal("1000")
    automated = Decimal("1030")  # 3% error
    err = percent_error(automated, manual)
    assert err > Decimal("2.0")

import pytest
from decimal import Decimal


@pytest.mark.parametrize(
    "material_id,quantity,unit,expected_factor",
    [
        ("material1", "10", "kg", Decimal("0.5")),
    ],
)
def test_calculate_material_carbon(
    monkeypatch, material_id, quantity, unit, expected_factor
):
    # Mock Brightway2 Database and activity
    class DummyActivity:
        exchanges = [{"amount": float(expected_factor)}]

    class DummyDB(list):
        def __iter__(self):
            return iter([DummyActivity()])

    monkeypatch.setattr("brightway2.Database", lambda name: DummyDB())
    from core.carbon.brightway.calculator import CarbonCalculator

    calc = CarbonCalculator("dummy")
    result = calc.calculate_material_carbon(material_id, Decimal(quantity), unit)
    assert result["emission_factor"] == expected_factor
    assert result["total_carbon"] == Decimal(quantity) * expected_factor

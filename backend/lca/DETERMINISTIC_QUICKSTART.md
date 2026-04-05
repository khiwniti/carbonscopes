# Deterministic Mode Quick Reference

**1-Page Guide for Developers**

---

## Quick Start (3 Steps)

```python
# Step 1: Import
from suna.backend.lca.brightway_config import initialize_brightway

# Step 2: Initialize (once at startup)
initialize_brightway(validate=True)

# Step 3: Use normally - determinism is automatic!
from suna.backend.core.carbon.brightway.calculator import CarbonCalculator
calculator = CarbonCalculator()
result = calculator.calculate_material_carbon("concrete-c30", Decimal("1000"), "kg")
```

---

## Key Rules

### ✅ DO

- **Initialize once** at application startup
- **Use Decimal type** for all quantities: `Decimal("1000.0")`
- **Reset in tests**: Call `reset_brightway()` between test runs
- **Validate in CI/CD**: Run `pytest lca/tests/test_deterministic.py`

### ❌ DON'T

- Don't use `float` for quantities: `1000.0` ← Wrong
- Don't skip initialization
- Don't use `datetime.now()` in calculations (metadata only)
- Don't enable parallel processing

---

## Testing Pattern

```python
from suna.backend.lca.brightway_config import reset_brightway

def test_my_calculation(self):
    reset_brightway()  # Fresh state
    result = calculate_something()
    assert result == expected
```

---

## Validation

```bash
# Quick check
python backend/lca/validate_deterministic.py

# Full test suite
pytest backend/lca/tests/test_deterministic.py -v

# Specific test
pytest backend/lca/tests/test_deterministic.py::TestMultipleRunDeterminism::test_ten_consecutive_runs_identical -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Different results each run | Call `initialize_brightway(validate=True)` |
| Precision errors (150.0001) | Use `Decimal("1000.0")` not `1000.0` |
| Tests fail together | Add `reset_brightway()` in each test |
| Validation fails | Check Python version (need 3.12+) |

---

## Configuration Values

```python
RANDOM_SEED = 42              # Fixed
DECIMAL_PRECISION = 28        # High precision
MONTE_CARLO_ITERATIONS = 0    # No randomness
USE_STATIC_LCA = True         # Deterministic
```

---

## API Integration

```python
from fastapi import APIRouter
from decimal import Decimal

@router.post("/calculate")
async def calculate(material_id: str, quantity: str):  # quantity as STRING
    qty = Decimal(quantity)  # Convert to Decimal
    result = calculator.calculate_material_carbon(material_id, qty, "kg")
    return result
```

---

## More Info

- **Full Guide**: `DETERMINISTIC_MODE_GUIDE.md`
- **Tests**: `tests/test_deterministic.py`
- **Config**: `brightway_config.py`

---

**Remember**: Same inputs → Same outputs (always!)

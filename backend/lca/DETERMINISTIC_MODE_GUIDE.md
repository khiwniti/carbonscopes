# Deterministic Mode Guide for BKS cBIM AI Brightway2 Integration

## Table of Contents

1. [Introduction](#introduction)
2. [Why Determinism Matters](#why-determinism-matters)
3. [Configuration Overview](#configuration-overview)
4. [Implementation Details](#implementation-details)
5. [Verification Procedures](#verification-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Known Limitations](#known-limitations)
8. [Best Practices](#best-practices)

---

## Introduction

This guide explains how the BKS cBIM AI agent achieves deterministic, reproducible LCA calculations using Brightway2. **Determinism** means that identical inputs always produce identical outputs, regardless of when or where the calculation is performed.

### What is Deterministic Calculation?

**Deterministic calculation** guarantees:
- Same material quantities → Same carbon footprint result
- Same calculation run multiple times → Identical numerical output
- Same calculation on different machines → Identical result (with caveats)

**Non-deterministic calculation** produces:
- Slightly different results each run
- Variation due to random sampling (Monte Carlo)
- Unpredictable floating-point rounding

### Target Use Cases

Determinism is critical for:
- **Consultant validation**: External auditors must reproduce our results exactly
- **Regulatory compliance**: Government agencies require reproducible calculations
- **EDGE/TREES certification**: Certification bodies need consistent numbers
- **Change tracking**: Detect when material specifications change vs calculation drift
- **Automated testing**: CI/CD pipelines need predictable test outcomes

---

## Why Determinism Matters

### Problem: Non-Deterministic LCA Calculations

Traditional LCA tools often use:

1. **Monte Carlo Uncertainty Analysis**
   - Random sampling of probability distributions
   - Different results on each run
   - Good for uncertainty quantification, bad for reproducibility

2. **Floating-Point Arithmetic**
   - Limited precision (~15-17 decimal digits)
   - Rounding errors accumulate
   - Platform-dependent implementations

3. **Parallel Processing**
   - Non-deterministic thread scheduling
   - Race conditions in calculations
   - Order-dependent results

### BKS cBIM AI Solution

We achieve determinism through:

1. **Fixed Random Seeds**
   ```python
   RANDOM_SEED = 42  # Never changes
   ```

2. **Decimal Arithmetic**
   ```python
   DECIMAL_PRECISION = 28  # High precision
   ```

3. **Static LCA (No Monte Carlo)**
   ```python
   MONTE_CARLO_ITERATIONS = 0
   USE_STATIC_LCA = True
   ```

4. **Single-Threaded Calculations**
   - No parallel processing
   - Deterministic execution order

### Real-World Example

**Scenario**: Consultant validates our calculation for 5000 kg concrete.

**Without Determinism**:
```
Run 1: 750.0234 kg CO2e
Run 2: 750.0198 kg CO2e
Run 3: 750.0221 kg CO2e
Consultant: 750.0187 kg CO2e ❌ "Numbers don't match!"
```

**With Determinism**:
```
Run 1: 750.0000 kg CO2e
Run 2: 750.0000 kg CO2e
Run 3: 750.0000 kg CO2e
Consultant: 750.0000 kg CO2e ✅ "Perfect match!"
```

---

## Configuration Overview

### Configuration Classes

All deterministic settings are in `brightway_config.py`:

```python
from suna.backend.lca.brightway_config import (
    DeterministicConfig,      # Core determinism settings
    ValidationConfig,         # Testing parameters
    initialize_brightway,     # Setup function
    reset_brightway,         # Reset for testing
)
```

### Key Configuration Values

#### 1. DeterministicConfig

```python
class DeterministicConfig:
    # High precision decimal arithmetic (28 significant figures)
    DECIMAL_PRECISION: Final[int] = 28

    # Fixed random seed for any stochastic operations
    RANDOM_SEED: Final[int] = 42

    # Disable Monte Carlo uncertainty analysis
    MONTE_CARLO_ITERATIONS: Final[int] = 0
    USE_STATIC_LCA: Final[bool] = True

    # Use Decimal type instead of float
    USE_DECIMAL: Final[bool] = True
```

**Why These Values?**

- **DECIMAL_PRECISION = 28**: Python's Decimal type default, provides ~28 significant digits
- **RANDOM_SEED = 42**: Standard value in scientific computing (arbitrary but consistent)
- **MONTE_CARLO_ITERATIONS = 0**: Disables stochastic sampling completely
- **USE_DECIMAL = True**: Enables exact arithmetic (no floating-point errors)

#### 2. ValidationConfig

```python
class ValidationConfig:
    # Number of runs to verify determinism
    DETERMINISM_RUNS: Final[int] = 10

    # Target accuracy vs manual assessments
    TARGET_ERROR_PERCENT: Final[Decimal] = Decimal("2.0")
```

---

## Implementation Details

### How Determinism is Achieved

#### Step 1: Seed Configuration

The `DeterministicConfig.apply()` method seeds all random number generators:

```python
def apply(cls):
    """Apply deterministic configuration globally."""
    # Set decimal precision
    getcontext().prec = cls.DECIMAL_PRECISION

    # Fix Python random seed
    random.seed(cls.RANDOM_SEED)

    # Fix NumPy random seed
    import numpy as np
    np.random.seed(cls.RANDOM_SEED)
    np.random.default_rng(cls.RANDOM_SEED)

    # Set environment variable
    os.environ["PYTHONHASHSEED"] = str(cls.RANDOM_SEED)
```

**What This Does:**
- `random.seed()`: Seeds Python's built-in random module
- `np.random.seed()`: Seeds NumPy's legacy random API
- `np.random.default_rng()`: Seeds NumPy's new Generator API
- `PYTHONHASHSEED`: Ensures deterministic hash functions

#### Step 2: Initialization

Call `initialize_brightway()` at application startup:

```python
from suna.backend.lca.brightway_config import initialize_brightway

# Initialize with validation
project = initialize_brightway(validate=True)
```

**What This Does:**
1. Applies deterministic configuration
2. Validates that seeds are working correctly
3. Creates Brightway2 project directory
4. Sets up database connections

#### Step 3: Reset Between Runs (Testing Only)

For testing reproducibility, use `reset_brightway()`:

```python
from suna.backend.lca.brightway_config import reset_brightway

# Run 1
result1 = calculate_lca(materials)

# Reset state
reset_brightway()

# Run 2 (should be identical)
result2 = calculate_lca(materials)

assert result1 == result2  # ✅ Passes
```

### Integration with Carbon Calculator

The `CarbonCalculator` class automatically uses deterministic configuration:

```python
from suna.backend.core.carbon.brightway.calculator import CarbonCalculator
from suna.backend.lca.brightway_config import initialize_brightway

# Initialize once at startup
initialize_brightway()

# Use calculator
calculator = CarbonCalculator(db_name="TGO-Thailand-2026")
result = calculator.calculate_material_carbon(
    material_id="concrete-c30",
    quantity=Decimal("1000.0"),
    unit="kg"
)

# Result is deterministic
print(result["total_carbon"])  # Always the same value
```

---

## Verification Procedures

### Automated Testing

Run the determinism test suite:

```bash
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent/backend
pytest lca/tests/test_deterministic.py -v
```

**Expected Output:**
```
test_random_seed_is_fixed .......................... PASSED
test_numpy_seed_is_fixed ........................... PASSED
test_decimal_precision_configured .................. PASSED
test_ten_consecutive_runs_identical ................ PASSED
test_multiple_materials_deterministic .............. PASSED
test_same_result_with_cache_cleared ................ PASSED
test_different_input_order_same_result ............. PASSED
```

### Manual Verification

#### Test 1: Single Material, 10 Runs

```python
from suna.backend.lca.brightway_config import initialize_brightway, reset_brightway
from suna.backend.core.carbon.brightway.calculator import CarbonCalculator
from decimal import Decimal

# Initialize
initialize_brightway()
calculator = CarbonCalculator()

# Run 10 times
results = []
for i in range(10):
    reset_brightway()
    result = calculator.calculate_material_carbon(
        material_id="concrete-c30",
        quantity=Decimal("1000.0"),
        unit="kg"
    )
    results.append(result["total_carbon"])
    print(f"Run {i+1}: {result['total_carbon']} kg CO2e")

# Verify all identical
assert len(set(results)) == 1, "Non-deterministic results!"
print(f"✅ All 10 runs produced: {results[0]} kg CO2e")
```

#### Test 2: Multi-Material Project

```python
# Complex project with multiple materials
materials = [
    {"material_id": "concrete-c30", "quantity": "5000.0", "unit": "kg"},
    {"material_id": "steel-rebar", "quantity": "500.0", "unit": "kg"},
    {"material_id": "glass-float", "quantity": "200.0", "unit": "m2"},
]

# Run 5 times
results = []
for i in range(5):
    reset_brightway()
    result = calculator.calculate_project_carbon(materials)
    results.append(result["total_carbon"])

# Verify identical
assert len(set(results)) == 1
print(f"✅ Complex project: {results[0]} kg CO2e (deterministic)")
```

#### Test 3: Input Order Independence

```python
# Same materials, different order
materials_order1 = [
    {"material_id": "concrete-c30", "quantity": "1000", "unit": "kg"},
    {"material_id": "steel-rebar", "quantity": "100", "unit": "kg"},
]

materials_order2 = [
    {"material_id": "steel-rebar", "quantity": "100", "unit": "kg"},
    {"material_id": "concrete-c30", "quantity": "1000", "unit": "kg"},
]

reset_brightway()
result1 = calculator.calculate_project_carbon(materials_order1)

reset_brightway()
result2 = calculator.calculate_project_carbon(materials_order2)

assert result1["total_carbon"] == result2["total_carbon"]
print("✅ Order-independent calculation confirmed")
```

### Configuration Validation

Check configuration status at any time:

```python
from suna.backend.lca.brightway_config import DeterministicConfig
from decimal import getcontext

# Check if config is applied
print(f"Random seed: {DeterministicConfig.RANDOM_SEED}")
print(f"Decimal precision: {getcontext().prec}")
print(f"Monte Carlo iterations: {DeterministicConfig.MONTE_CARLO_ITERATIONS}")

# Validate determinism
is_deterministic = DeterministicConfig.validate_determinism()
print(f"Determinism active: {is_deterministic}")
```

---

## Troubleshooting

### Issue 1: Non-Deterministic Results

**Symptom**: Same calculation produces different results on each run.

**Diagnosis**:
```python
from suna.backend.lca.brightway_config import DeterministicConfig

# Check if config is applied
if not DeterministicConfig.validate_determinism():
    print("❌ Deterministic config not properly applied")
else:
    print("✅ Config is correct - issue elsewhere")
```

**Solutions**:

1. **Re-initialize Brightway2**:
   ```python
   from suna.backend.lca.brightway_config import initialize_brightway
   initialize_brightway(validate=True)
   ```

2. **Check for external randomness**:
   - Database queries with non-deterministic ordering
   - Parallel processing enabled
   - System time used in calculations

3. **Reset between runs**:
   ```python
   from suna.backend.lca.brightway_config import reset_brightway
   reset_brightway()  # Call before each calculation in tests
   ```

### Issue 2: Validation Fails

**Symptom**: `DeterministicConfig.validate_determinism()` returns `False`.

**Diagnosis**:
```python
import random
import numpy as np
from decimal import getcontext

# Manual checks
print(f"Decimal precision: {getcontext().prec} (should be 28)")

# Test random seed
random.seed(42)
seq1 = [random.random() for _ in range(5)]
random.seed(42)
seq2 = [random.random() for _ in range(5)]
print(f"Random seed working: {seq1 == seq2}")

# Test numpy seed
np.random.seed(42)
arr1 = [np.random.random() for _ in range(5)]
np.random.seed(42)
arr2 = [np.random.random() for _ in range(5)]
print(f"NumPy seed working: {arr1 == arr2}")
```

**Solutions**:
- Reinstall NumPy: `pip install --force-reinstall numpy`
- Check Python version: `python --version` (should be 3.12+)
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`

### Issue 3: Precision Errors

**Symptom**: Results differ by tiny amounts (e.g., 150.0000001 vs 150.0).

**Diagnosis**:
```python
from decimal import Decimal

# Check if using Decimal vs float
value = Decimal("0.15") * Decimal("1000")
print(f"Type: {type(value)}")  # Should be <class 'decimal.Decimal'>
print(f"Value: {value}")        # Should be exactly 150.0

# Float comparison
float_value = 0.15 * 1000
print(f"Float: {float_value}")  # Might be 150.00000000000003
```

**Solutions**:
- Always use `Decimal` type for quantities:
  ```python
  quantity = Decimal("1000.0")  # ✅ Correct
  quantity = 1000.0              # ❌ Wrong (float)
  ```

- Convert strings to Decimal:
  ```python
  from decimal import Decimal
  quantity = Decimal(str(user_input))
  ```

### Issue 4: Cross-Machine Differences

**Symptom**: Same calculation produces different results on different machines.

**Possible Causes**:
1. Different Python versions (3.11 vs 3.12)
2. Different NumPy versions
3. Different Brightway2 versions
4. Different operating systems (Linux vs Windows)

**Solutions**:

1. **Version Pinning** (in `requirements.txt`):
   ```txt
   python==3.12.0
   brightway2==2.5.0
   bw2data==4.0.0
   bw2calc==2.0.0
   numpy==1.26.0
   ```

2. **Docker Containerization**:
   ```dockerfile
   FROM python:3.12-slim
   RUN pip install brightway2==2.5.0 numpy==1.26.0
   # Ensures exact same environment everywhere
   ```

3. **Document Environment**:
   ```python
   import sys
   import numpy as np
   import bw2data as bd

   print(f"Python: {sys.version}")
   print(f"NumPy: {np.__version__}")
   print(f"Brightway2: {bd.__version__}")
   ```

### Issue 5: Tests Pass Individually but Fail Together

**Symptom**: Running tests one-by-one passes, but running all together fails.

**Cause**: Tests are not properly isolated - state leaks between tests.

**Solution**:

1. **Use pytest fixtures with proper cleanup**:
   ```python
   @pytest.fixture(autouse=True)
   def setup_teardown(self):
       # Setup
       initialize_brightway()
       yield
       # Teardown
       cleanup_test_project()
   ```

2. **Reset between tests**:
   ```python
   def test_calculation_1(self):
       reset_brightway()
       # Test code

   def test_calculation_2(self):
       reset_brightway()  # Fresh state
       # Test code
   ```

---

## Known Limitations

### 1. Floating-Point Hardware Differences

**Issue**: Different CPUs (x86 vs ARM) may produce slightly different floating-point results.

**Impact**: Minimal - differences typically at 15th+ decimal place.

**Mitigation**: Use Decimal type for all critical calculations.

**Example**:
```python
# May differ across platforms
float_result = 0.1 + 0.2  # 0.30000000000000004 (maybe)

# Always identical
decimal_result = Decimal("0.1") + Decimal("0.2")  # 0.3 (exact)
```

### 2. Python Version Dependencies

**Issue**: Python 3.11 vs 3.12 may have different random number implementations.

**Impact**: Results may differ between Python versions.

**Mitigation**: Pin Python version in production.

**Project Standard**: Python 3.12+

### 3. External Database Query Order

**Issue**: Database queries without explicit `ORDER BY` may return rows in different order.

**Impact**: If calculations depend on query order, results may vary.

**Mitigation**: Always use explicit ordering in queries.

**Example**:
```python
# ❌ Non-deterministic
materials = db.query("SELECT * FROM materials")

# ✅ Deterministic
materials = db.query("SELECT * FROM materials ORDER BY material_id")
```

### 4. Parallel Processing

**Issue**: Multi-threaded calculations may produce different results due to race conditions.

**Impact**: Thread scheduling is non-deterministic.

**Mitigation**: Use single-threaded mode for LCA calculations.

**Current Configuration**: Single-threaded by default.

### 5. System Time Dependencies

**Issue**: If calculations use `datetime.now()` or timestamps, results will vary.

**Impact**: Each run produces different timestamps.

**Mitigation**: Don't include timestamps in calculation logic (use for metadata only).

**Example**:
```python
# ✅ Correct: timestamp is metadata, not part of calculation
result = {
    "total_carbon": Decimal("150.0"),  # Deterministic
    "calculated_at": datetime.now(),    # Metadata only
}
```

### 6. Monte Carlo Uncertainty Analysis

**Issue**: Uncertainty analysis requires random sampling (non-deterministic).

**Impact**: Cannot perform stochastic LCA in deterministic mode.

**Trade-off**: Determinism vs uncertainty quantification.

**Decision**: Prioritize determinism for BKS cBIM AI (consultant validation > uncertainty analysis).

---

## Best Practices

### 1. Application Startup

Always initialize Brightway2 with validation:

```python
# In main application entry point
from suna.backend.lca.brightway_config import initialize_brightway

def main():
    # Initialize LCA system
    try:
        project = initialize_brightway(validate=True)
        print(f"✅ Initialized Brightway2 project: {project}")
    except RuntimeError as e:
        print(f"❌ Deterministic validation failed: {e}")
        sys.exit(1)

    # Continue with application
    ...
```

### 2. Testing

Use `reset_brightway()` between test runs:

```python
import pytest
from suna.backend.lca.brightway_config import reset_brightway

class TestLCACalculations:
    def test_calculation_1(self):
        reset_brightway()  # Fresh state
        # Test code

    def test_calculation_2(self):
        reset_brightway()  # Independent
        # Test code
```

### 3. Production Calculations

Always use Decimal type for quantities:

```python
from decimal import Decimal
from suna.backend.core.carbon.brightway.calculator import CarbonCalculator

calculator = CarbonCalculator()

# ✅ Correct
result = calculator.calculate_material_carbon(
    material_id="concrete-c30",
    quantity=Decimal("1000.0"),  # Decimal, not float
    unit="kg"
)

# ❌ Wrong
result = calculator.calculate_material_carbon(
    material_id="concrete-c30",
    quantity=1000.0,  # Float - precision loss!
    unit="kg"
)
```

### 4. API Integration

Convert user inputs to Decimal:

```python
from fastapi import APIRouter
from decimal import Decimal
from pydantic import BaseModel

class CalculationRequest(BaseModel):
    material_id: str
    quantity: str  # String, not float!
    unit: str

@router.post("/calculate")
async def calculate(req: CalculationRequest):
    # Convert to Decimal
    quantity = Decimal(req.quantity)

    # Calculate
    result = calculator.calculate_material_carbon(
        material_id=req.material_id,
        quantity=quantity,
        unit=req.unit
    )

    return result
```

### 5. Version Control

Pin all dependencies for reproducibility:

```txt
# requirements.txt
python==3.12.0
brightway2==2.5.0
bw2data==4.0.0
bw2calc==2.0.0
bw2io==0.9.0
numpy==1.26.0
```

### 6. Documentation

Document calculation environment in results:

```python
import sys
import numpy as np
import bw2data as bd

result = {
    "total_carbon": Decimal("150.0"),
    "metadata": {
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "brightway_version": bd.__version__,
        "random_seed": DeterministicConfig.RANDOM_SEED,
        "calculation_mode": "deterministic",
    }
}
```

### 7. Continuous Integration

Add determinism check to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Test Determinism
  run: |
    pytest backend/lca/tests/test_deterministic.py -v
    # Fails if any non-determinism detected
```

### 8. Error Handling

Gracefully handle validation failures:

```python
from suna.backend.lca.brightway_config import initialize_brightway

try:
    initialize_brightway(validate=True)
except RuntimeError as e:
    # Log error
    logger.error(f"Determinism validation failed: {e}")

    # Attempt recovery
    DeterministicConfig.apply()

    # Re-validate
    if DeterministicConfig.validate_determinism():
        logger.info("✅ Determinism restored")
    else:
        logger.critical("❌ Cannot achieve deterministic mode")
        raise
```

---

## Summary

### Key Takeaways

1. **Determinism is achieved through**:
   - Fixed random seeds (RANDOM_SEED = 42)
   - High-precision Decimal arithmetic (28 digits)
   - Static LCA mode (no Monte Carlo)
   - Single-threaded execution

2. **Always initialize before calculations**:
   ```python
   initialize_brightway(validate=True)
   ```

3. **Use Decimal type for all quantities**:
   ```python
   quantity = Decimal("1000.0")
   ```

4. **Test determinism regularly**:
   ```bash
   pytest lca/tests/test_deterministic.py -v
   ```

5. **Document limitations**:
   - Python version dependent
   - Platform-specific edge cases
   - No uncertainty analysis in deterministic mode

### Quick Reference

| Action | Command |
|--------|---------|
| Initialize | `initialize_brightway(validate=True)` |
| Reset state | `reset_brightway()` |
| Validate | `DeterministicConfig.validate_determinism()` |
| Test | `pytest lca/tests/test_deterministic.py -v` |
| Check config | `print(getcontext().prec)` |

---

**Last Updated**: 2026-03-23
**Version**: 1.0.0
**Status**: Production Ready ✅

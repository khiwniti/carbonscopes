# Brightway2 Quick Start Guide

## 5-Minute Setup

### 1. Install Brightway2

```bash
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent/backend
uv pip install -r lca/requirements.txt
```

### 2. Initialize Project

```python
from suna.backend.lca import initialize_brightway

project = initialize_brightway()
print(f"✓ Project initialized: {project}")
```

### 3. Verify Installation

```bash
pytest lca/tests/test_brightway_setup.py::TestBrightway2Imports -v
```

**Expected**: All tests pass ✓

---

## Common Tasks

### Check Current Project

```python
import bw2data as bd
print(bd.projects.current)
# Output: thailand-construction
```

### List Databases

```python
import bw2data as bd
print(list(bd.databases))
# Output: ['TGO-Thailand-2026', 'biosphere3']
```

### Create Test Material

```python
import bw2data as bd

db = bd.Database("test-materials")
db.write({
    ("test-materials", "concrete-c30"): {
        "name": "Concrete C30",
        "unit": "kg",
        "location": "TH",
        "exchanges": [
            {"amount": 1.0, "type": "production", "input": ("test-materials", "concrete-c30")},
            {"amount": 0.15, "type": "biosphere", "name": "CO2"},
        ]
    }
})

print("✓ Material created")
```

### Calculate Embodied Carbon

```python
import bw2data as bd
import bw2calc as bc

# Get material
material = bd.get_activity(("test-materials", "concrete-c30"))

# Calculate for 1000 kg
lca = bc.LCA({material: 1000})
lca.lci()
lca.lcia()

print(f"Embodied carbon: {lca.score} kg CO2e")
# Output: Embodied carbon: 150.0 kg CO2e
```

### Test Determinism

```python
from suna.backend.lca import DeterministicConfig
import bw2data as bd
import bw2calc as bc

DeterministicConfig.apply()

material = bd.get_activity(("test-materials", "concrete-c30"))
results = []

for _ in range(10):
    lca = bc.LCA({material: 1000})
    lca.lci()
    lca.lcia()
    results.append(lca.score)

print(f"All identical: {len(set(results)) == 1}")
# Output: All identical: True
```

---

## Configuration Quick Reference

### Deterministic Settings

```python
from suna.backend.lca import DeterministicConfig

print(f"Precision: {DeterministicConfig.DECIMAL_PRECISION}")  # 28
print(f"Random seed: {DeterministicConfig.RANDOM_SEED}")  # 42
print(f"Static LCA: {DeterministicConfig.USE_STATIC_LCA}")  # True
```

### Project Settings

```python
from suna.backend.lca import ProjectConfig

print(f"Project: {ProjectConfig.PROJECT_NAME}")  # thailand-construction
print(f"Database: {ProjectConfig.DATABASE_NAME}")  # TGO-Thailand-2026
print(f"Stages: {ProjectConfig.DEFAULT_STAGES}")  # ['A1', 'A2', 'A3']
```

### Data Paths

```python
from suna.backend.lca import PathConfig

print(f"Base: {PathConfig.BASE_DIR}")
print(f"Data: {PathConfig.DATA_DIR}")
print(f"Brightway2: {PathConfig.BRIGHTWAY_DIR}")
```

---

## Troubleshooting

### Import Error

```python
# Error: ImportError: No module named 'bw2data'
# Fix:
uv pip install brightway2 bw2data bw2calc bw2io
```

### Project Not Found

```python
# Error: ValueError: Project 'thailand-construction' does not exist
# Fix:
from suna.backend.lca import initialize_brightway
initialize_brightway()
```

### Database Locked

```python
# Error: sqlite3.OperationalError: database is locked
# Fix:
import bw2data as bd
bd.databases.clean()
```

### Non-Deterministic Results

```python
# Fix: Apply config before calculations
from suna.backend.lca import DeterministicConfig
DeterministicConfig.apply()
```

---

## API Usage (Future)

### Calculate Single Material

```bash
curl -X POST http://localhost:8000/api/carbon/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": "materials/concrete-c30",
    "quantity": 1200,
    "unit": "kg"
  }'
```

**Response**:
```json
{
    "total_carbon": 180.0,
    "emission_factor": 0.15,
    "formula": "1200 kg × 0.15 kgCO2e/kg = 180.0 kgCO2e",
    "lifecycle_stages": ["A1", "A2", "A3"]
}
```

### Calculate Project

```bash
curl -X POST http://localhost:8000/api/carbon/calculate-project \
  -H "Content-Type: application/json" \
  -d '{
    "materials": [
      {"material_id": "materials/concrete-c30", "quantity": 1200, "unit": "kg"},
      {"material_id": "materials/steel-rebar", "quantity": 500, "unit": "kg"}
    ]
  }'
```

---

## Testing

### Run All Tests

```bash
pytest backend/lca/tests/ -v
```

### Run Specific Test

```bash
pytest backend/lca/tests/test_brightway_setup.py::TestBrightway2Imports::test_import_bw2data -v
```

### Test Determinism

```bash
pytest backend/lca/tests/test_brightway_setup.py::TestBrightway2BasicCalculations::test_deterministic_calculation -v
```

### Test with Coverage

```bash
pytest backend/lca/tests/ --cov=suna.backend.lca
```

---

## Performance Benchmarking

### Single Material Calculation

```python
import time
import bw2data as bd
import bw2calc as bc

material = bd.get_activity(("TGO-Thailand-2026", "materials/concrete-c30"))

start = time.time()
lca = bc.LCA({material: 1000})
lca.lci()
lca.lcia()
duration = time.time() - start

print(f"Calculation time: {duration*1000:.2f} ms")
# Target: <50 ms
```

### Batch Calculation (500 materials)

```python
import time
import bw2data as bd
import bw2calc as bc

db = bd.Database("TGO-Thailand-2026")
materials = list(db)[:500]

start = time.time()
for material in materials:
    lca = bc.LCA({material: 100})
    lca.lci()
    lca.lcia()
duration = time.time() - start

print(f"500 materials in {duration:.2f}s")
# Target: <5s
```

---

## Data Management

### Export Database

```python
import bw2io as bi

# Export as JSON
bi.export_json("TGO-Thailand-2026", "/tmp/tgo-export.json")

# Export as Excel
bi.export_excel("TGO-Thailand-2026", "/tmp/tgo-export.xlsx")
```

### Backup Project

```bash
# Copy entire project directory
cp -r backend/lca/data/brightway2/thailand-construction/ \
      backend/lca/data/backups/thailand-construction-2026-03-23/
```

### Reset Project

```python
import bw2data as bd

# CAUTION: This deletes all data!
bd.projects.delete_project("thailand-construction", delete_dir=True)

# Reinitialize
from suna.backend.lca import initialize_brightway
initialize_brightway()
```

---

## Environment Variables

Create `.env` file:

```bash
# GraphDB connection
GRAPHDB_ENDPOINT=http://localhost:7200
GRAPHDB_REPOSITORY=tgo-emission-factors

# Logging
LCA_LOG_LEVEL=INFO

# Optional: Custom Brightway2 directory
# BRIGHTWAY2_DIR=/custom/path/brightway2
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()

from suna.backend.lca import GraphDBConfig
print(GraphDBConfig.ENDPOINT)
```

---

## Next Steps

1. **Load TGO Data** (Task #21):
   - Implement `tgo_loader.py`
   - Query GraphDB for emission factors
   - Populate Brightway2 database

2. **API Integration** (Task #22):
   - Add FastAPI endpoints
   - Integrate with frontend
   - Add authentication

3. **Validation** (Task #23):
   - Collect manual assessments
   - Compare automated vs manual
   - Verify ≤2% error target

---

## Resources

- **Full Documentation**: `README.md`
- **Architecture**: `ARCHITECTURE.md`
- **Installation**: `INSTALL.md`
- **Brightway2 Docs**: https://docs.brightway.dev/
- **Project Repo**: https://github.com/cbim-ai/suna

---

**Last Updated**: 2026-03-23
**Version**: 1.0.0

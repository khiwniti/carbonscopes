# Brightway2 Installation Guide

## Quick Install

```bash
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent/backend

# Option 1: Using uv (recommended)
uv pip install -r lca/requirements.txt

# Option 2: Using pip
pip install -r lca/requirements.txt

# Option 3: Install from pyproject.toml (after sync)
uv pip install -e .
```

## Verification

```bash
# Test installation
python3 -c "import bw2data; print(f'bw2data version: {bw2data.__version__}')"
python3 -c "import bw2calc; print(f'bw2calc version: {bw2calc.__version__}')"

# Run test suite
pytest lca/tests/test_brightway_setup.py -v
```

## Expected Output

```
bw2data version: 4.0.x
bw2calc version: 2.0.x

====== test session starts ======
lca/tests/test_brightway_setup.py::TestBrightway2Imports::test_import_bw2data PASSED
lca/tests/test_brightway_setup.py::TestBrightway2Imports::test_import_bw2calc PASSED
lca/tests/test_brightway_setup.py::TestBrightway2Imports::test_import_bw2io PASSED
...
====== X passed in X.XXs ======
```

## Troubleshooting

### Issue: "No module named 'bw2data'"

**Solution**: Install Brightway2 packages

```bash
uv pip install brightway2 bw2data bw2calc bw2io
```

### Issue: Version mismatch or compatibility errors

**Solution**: Update to latest stable versions

```bash
uv pip install --upgrade brightway2 bw2data bw2calc bw2io
```

### Issue: Permission denied during installation

**Solution**: Use user installation

```bash
pip install --user -r lca/requirements.txt
```

### Issue: Binary compatibility issues (Linux/Mac)

**Solution**: Ensure build tools are installed

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# macOS
xcode-select --install

# Then retry installation
uv pip install -r lca/requirements.txt
```

## Initialize Project

After installation, initialize the Brightway2 project:

```python
from carbonscope.backend.lca import initialize_brightway

# First-time setup
project = initialize_brightway()
print(f"Initialized: {project}")
```

## Next Steps

1. **Load TGO data**: See Task #21 for GraphDB integration
2. **Run calculations**: See `README.md` Quick Start section
3. **Validate accuracy**: Run full test suite with `pytest lca/tests/ -v`

## Dependencies Installed

When you run the installation, the following packages are installed:

### Core Brightway2
- `brightway2` - Main framework
- `bw2data` - Data management and SQLite storage
- `bw2calc` - LCA calculation engine
- `bw2io` - Import/export utilities (ecoinvent, ILCD, etc.)

### Optional Utilities
- `bw2analyzer` - Contribution analysis and graph traversal
- `bw2parameters` - Parameterized inventories

### Scientific Computing
- `numpy` - Matrix operations (used by Brightway2)
- `scipy` - Sparse matrix handling
- `pandas` - Data manipulation

### Already in Project
- `rdflib` - RDF graph operations (for TGO integration)
- `SPARQLWrapper` - GraphDB queries
- `pytest` - Testing framework

## Storage Location

Brightway2 data is stored in:

```
backend/lca/data/brightway2/
├── projects/
│   └── thailand-construction/
│       ├── databases/
│       │   └── TGO-Thailand-2026.db (SQLite)
│       └── metadata/
└── logs/
```

Total disk usage: ~100-500MB depending on database size.

## Uninstall

To completely remove Brightway2:

```bash
# Remove packages
uv pip uninstall brightway2 bw2data bw2calc bw2io bw2analyzer bw2parameters

# Remove data directory (CAUTION: This deletes all LCA data!)
rm -rf backend/lca/data/brightway2/
```

---

**Last Updated**: 2026-03-23
**Tested On**: Python 3.12, Ubuntu 22.04

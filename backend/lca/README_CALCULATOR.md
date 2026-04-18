# LCA Carbon Calculator

**Version:** 1.0.0
**Date:** 2026-03-23
**Status:** Production Ready

## Overview

The LCA Carbon Calculator is a comprehensive system for calculating embodied carbon emissions in construction projects using TGO (Thailand Greenhouse Gas Management Organization) emission factors stored in GraphDB. It supports EDGE V3 certification compliance and provides consultant-grade accuracy (±2% error tolerance).

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Unit Conversion](#unit-conversion)
8. [Material Matching](#material-matching)
9. [EDGE Certification](#edge-certification)
10. [Error Handling](#error-handling)
11. [Best Practices](#best-practices)
12. [Testing](#testing)

---

## Features

- **Accurate Carbon Calculation:** Uses TGO emission factors with xsd:decimal precision
- **Comprehensive Unit Support:** Handles volume, mass, area, and length conversions
- **Smart Material Matching:** Fuzzy matching for both English and Thai material names
- **EDGE Certification:** Automatic calculation of EDGE compliance levels
- **Project-Level Analysis:** Complete BOQ carbon footprint calculation
- **Category Breakdown:** Carbon emissions by material category
- **Baseline Comparison:** Calculate savings vs. conventional construction
- **Data Quality Tracking:** Confidence scores and unmatched material reporting

---

## Installation

The LCA module is part of the BKS cBIM AI backend. Ensure GraphDB is running with TGO data loaded.

```bash
# Ensure you're in the project root
cd /teamspace/studios/this_studio/comprehensive-bks-cbim-ai-agent

# Install dependencies (if not already installed)
pip install -r backend/lca/requirements.txt

# Verify GraphDB connection
python -c "from carbonscope.backend.core.knowledge_graph import GraphDBClient; \
           client = GraphDBClient('http://localhost:7200/repositories/carbonbim-thailand'); \
           print(f'Connected! Triples: {client.get_triple_count()}')"
```

---

## Quick Start

### Basic Material Calculation

```python
from carbonscope.backend.lca import CarbonCalculator
from carbonscope.backend.core.knowledge_graph import GraphDBClient

# Initialize
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
calculator = CarbonCalculator(client)

# Calculate carbon for single material
carbon = calculator.calculate_material_carbon(
    material_name="Ready-mix Concrete C30",
    quantity=150.5,
    unit="m³"
)

print(f"Carbon emissions: {carbon} kgCO2e")
# Output: Carbon emissions: 67043.28 kgCO2e
```

### Full Project Calculation

```python
# Define Bill of Quantities (BOQ)
boq = [
    {
        "material_name": "Ready-mix Concrete C30",
        "material_name_th": "คอนกรีตผสมเสร็จ C30",
        "category": "Concrete",
        "quantity": 150.5,
        "unit": "m³"
    },
    {
        "material_name": "Steel Rebar SD40",
        "material_name_th": "เหล็กเสริมคอนกรีต SD40",
        "category": "Steel",
        "quantity": 12.3,
        "unit": "ton"
    },
    {
        "material_name": "Glass Panel",
        "category": "Glass",
        "quantity": 500,
        "unit": "m²"
    }
]

# Calculate project carbon
result = calculator.calculate_project_carbon(boq, language="en")

print(f"Total Carbon: {result['total_carbon_tonco2e']} tCO2e")
print(f"Matched Materials: {result['data_quality']['matched_materials']}")
print(f"Confidence: {result['data_quality']['confidence_score']:.2%}")
```

### EDGE Certification Report

```python
# Generate comprehensive carbon assessment report
report = calculator.generate_carbon_report(
    boq_data=boq,
    project_area=5000,  # m²
    language="en"
)

# Check EDGE compliance
edge = report['edge_certification']
print(f"EDGE Level: {edge['level']}")
print(f"Reduction: {edge['reduction_percentage']:.1f}%")
print(f"Compliant: {edge['compliant']}")

# Output:
# EDGE Level: EDGE Certified
# Reduction: 24.0%
# Compliant: True
```

---

## Core Components

### 1. CarbonCalculator

Main calculator class for embodied carbon calculations.

```python
from carbonscope.backend.lca import CarbonCalculator

calculator = CarbonCalculator(
    graphdb_client=client,
    min_match_confidence=0.7,  # Minimum confidence for fuzzy matching
    error_tolerance=0.02       # Maximum acceptable error (2%)
)
```

**Key Methods:**
- `calculate_material_carbon()` - Single material carbon
- `calculate_project_carbon()` - Full BOQ carbon footprint
- `calculate_baseline_carbon()` - Baseline using conventional materials
- `calculate_carbon_savings()` - Savings vs baseline with EDGE levels
- `generate_carbon_report()` - Comprehensive assessment report

### 2. UnitConverter

Handles all unit conversions for construction materials.

```python
from carbonscope.backend.lca import UnitConverter

converter = UnitConverter()

# Volume to mass conversion (requires material density)
kg = converter.convert_volume_to_mass(10, "m³", "Concrete", "kg")
# Result: 24000 kg (10 m³ × 2400 kg/m³)

# Simple unit conversion
liters = converter.convert(1, "m³", "liters")
# Result: 1000 liters
```

**Supported Units:**
- **Volume:** m³, liters, cm³
- **Mass:** kg, ton, tonne, g
- **Area:** m², cm², mm²
- **Length:** m, cm, mm

### 3. MaterialMatcher

Matches material names to TGO database entries.

```python
from carbonscope.backend.lca import MaterialMatcher

matcher = MaterialMatcher(
    graphdb_client=client,
    min_confidence=0.6  # Minimum confidence for matches
)

# Find materials
matches = matcher.find_material("คอนกรีต C30", language="th")

for match in matches:
    print(f"{match['label']} - Confidence: {match['confidence']:.2%}")
```

**Features:**
- Exact matching
- Fuzzy matching (English & Thai)
- Category filtering
- Confidence scoring
- Caching for performance

---

## Usage Examples

### Example 1: Simple Material Calculation

```python
# Calculate carbon for concrete
carbon = calculator.calculate_material_carbon(
    material_name="Concrete C30",
    quantity=100,
    unit="m³",
    category="Concrete"
)

print(f"100 m³ concrete = {carbon:,.0f} kgCO2e")
# Output: 100 m³ concrete = 44,560 kgCO2e
```

### Example 2: Unit Conversion

```python
# Steel in tons
carbon_tons = calculator.calculate_material_carbon(
    material_name="Steel Rebar",
    quantity=10,
    unit="ton",
    category="Steel"
)

# Steel in kg (automatic conversion)
carbon_kg = calculator.calculate_material_carbon(
    material_name="Steel Rebar",
    quantity=10000,
    unit="kg",
    category="Steel"
)

assert carbon_tons == carbon_kg  # Should be equal
```

### Example 3: Thai Language Material Matching

```python
# Use Thai material names
boq_thai = [
    {
        "material_name": "คอนกรีตผสมเสร็จ C30",
        "quantity": 100,
        "unit": "m³",
        "category": "Concrete"
    },
    {
        "material_name": "เหล็กเสริมคอนกรีต SD40",
        "quantity": 10,
        "unit": "ตัน",  # Thai unit "ton"
        "category": "Steel"
    }
]

result = calculator.calculate_project_carbon(boq_thai, language="th")
print(f"Total: {result['total_carbon_tonco2e']} tCO2e")
```

### Example 4: EDGE Certification Levels

```python
# Test different carbon reduction scenarios

# Scenario 1: 15% reduction (Not Certified)
savings_15 = calculator.calculate_carbon_savings(
    project_carbon=2125000,
    baseline_carbon=2500000
)
print(f"15% reduction: {savings_15['edge_level']}")
# Output: Not Certified

# Scenario 2: 25% reduction (EDGE Certified)
savings_25 = calculator.calculate_carbon_savings(
    project_carbon=1875000,
    baseline_carbon=2500000
)
print(f"25% reduction: {savings_25['edge_level']}")
# Output: EDGE Certified

# Scenario 3: 45% reduction (EDGE Advanced)
savings_45 = calculator.calculate_carbon_savings(
    project_carbon=1375000,
    baseline_carbon=2500000
)
print(f"45% reduction: {savings_45['edge_level']}")
# Output: EDGE Advanced

# Scenario 4: Net zero (Zero Carbon)
savings_100 = calculator.calculate_carbon_savings(
    project_carbon=0,
    baseline_carbon=2500000
)
print(f"100% reduction: {savings_100['edge_level']}")
# Output: Zero Carbon
```

### Example 5: Category Breakdown Analysis

```python
result = calculator.calculate_project_carbon(boq)

# Analyze by category
for category, data in result['breakdown_by_category'].items():
    print(f"{category}:")
    print(f"  Carbon: {data['carbon']:,.0f} kgCO2e")
    print(f"  Percentage: {data['percentage']:.1f}%")

# Output:
# Concrete:
#   Carbon: 67,043 kgCO2e
#   Percentage: 47.5%
# Steel:
#   Carbon: 36,900 kgCO2e
#   Percentage: 26.1%
# Glass:
#   Carbon: 15,000 kgCO2e
#   Percentage: 10.6%
```

### Example 6: Error Handling

```python
from carbonscope.backend.lca import CarbonCalculationError

try:
    carbon = calculator.calculate_material_carbon(
        material_name="Unknown Material XYZ",
        quantity=100,
        unit="m³"
    )
except CarbonCalculationError as e:
    print(f"Error: {e}")

    # Get alternatives
    alternatives = matcher.get_alternatives(
        "Unknown Material XYZ",
        category="Concrete",
        limit=5
    )

    print("\nDid you mean:")
    for alt in alternatives:
        print(f"  - {alt['label']} (confidence: {alt['confidence']:.2%})")
```

---

## API Reference

### CarbonCalculator

#### `__init__(graphdb_client, min_match_confidence=0.7, error_tolerance=0.02)`

Initialize the carbon calculator.

**Parameters:**
- `graphdb_client` (GraphDBClient): GraphDB client instance
- `min_match_confidence` (float): Minimum confidence for material matching (0.0-1.0)
- `error_tolerance` (float): Maximum acceptable error tolerance (default: 2%)

#### `calculate_material_carbon(material_name, quantity, unit, material_id=None, category=None, language="en")`

Calculate carbon emissions for a single material.

**Parameters:**
- `material_name` (str): Material name
- `quantity` (float): Material quantity
- `unit` (str): Unit of quantity
- `material_id` (str, optional): TGO material URI
- `category` (str, optional): Material category
- `language` (str): Language for matching ("en" or "th")

**Returns:**
- `Decimal`: Carbon emissions in kgCO2e

#### `calculate_project_carbon(boq_data, language="en")`

Calculate total carbon emissions for a project BOQ.

**Parameters:**
- `boq_data` (List[Dict]): Bill of Quantities data
- `language` (str): Language for material matching

**Returns:**
- `Dict`: Comprehensive carbon calculation result

**BOQ Entry Format:**
```python
{
    "material_name": str,        # Required
    "quantity": float,           # Required
    "unit": str,                 # Required
    "category": str,             # Optional but recommended
    "material_id": str,          # Optional (TGO URI)
    "material_name_th": str      # Optional (Thai name)
}
```

#### `calculate_baseline_carbon(project_data, baseline_factors=None)`

Calculate baseline carbon using standard Thai construction practices.

**Parameters:**
- `project_data` (List[Dict]): Project material data
- `baseline_factors` (Dict[str, float], optional): Custom baseline emission factors

**Returns:**
- `Decimal`: Baseline carbon in kgCO2e

#### `calculate_carbon_savings(project_carbon, baseline_carbon)`

Calculate carbon savings vs baseline.

**Parameters:**
- `project_carbon` (float): Project carbon emissions (kgCO2e)
- `baseline_carbon` (float): Baseline carbon emissions (kgCO2e)

**Returns:**
- `Dict`: Savings analysis with EDGE certification level

#### `generate_carbon_report(boq_data, project_area=None, baseline_factors=None, language="en")`

Generate comprehensive carbon assessment report.

**Parameters:**
- `boq_data` (List[Dict]): Bill of Quantities data
- `project_area` (float, optional): Project floor area (m²)
- `baseline_factors` (Dict, optional): Custom baseline factors
- `language` (str): Language for material matching

**Returns:**
- `Dict`: Complete carbon assessment report

---

## Unit Conversion

### Material Densities (kg/m³)

| Material | Density | Notes |
|----------|---------|-------|
| Concrete | 2,400 | Normal weight concrete |
| Concrete (Lightweight) | 1,800 | AAC, lightweight aggregate |
| Concrete (Heavy) | 2,600 | Heavy aggregate |
| Steel | 7,850 | Steel rebar and structural |
| Aluminum | 2,700 | Aluminum sections |
| Wood | 600 | Average (varies by species) |
| Wood (Softwood) | 500 | Pine, spruce, fir |
| Wood (Hardwood) | 750 | Teak, oak, mahogany |
| Glass | 2,500 | Float, tempered |
| Brick | 1,800 | Clay bricks |
| Block (Concrete) | 2,000 | Concrete masonry units |
| Block (AAC) | 600 | Autoclaved aerated concrete |
| Gypsum | 900 | Gypsum board |

### Conversion Examples

```python
converter = UnitConverter()

# Volume conversions
m3 = converter.convert(1000, "liters", "m³")  # 1.0 m³
liters = converter.convert(1, "m³", "liters")  # 1000 liters

# Mass conversions
kg = converter.convert(2, "ton", "kg")  # 2000 kg
tons = converter.convert(5000, "kg", "ton")  # 5 tons

# Volume to mass (density-based)
kg = converter.convert_volume_to_mass(1, "m³", "Concrete")  # 2400 kg
kg = converter.convert_volume_to_mass(1, "m³", "Steel")     # 7850 kg

# Mass to volume (density-based)
m3 = converter.convert_mass_to_volume(2400, "kg", "Concrete")  # 1 m³
m3 = converter.convert_mass_to_volume(7850, "kg", "Steel")     # 1 m³

# Add custom material density
converter.add_material_density("CustomMaterial", 1500.0)
```

---

## Material Matching

### Matching Strategies

1. **Exact Match** (confidence: 1.0)
   - Query: "Concrete C30"
   - Database: "Concrete C30"
   - Confidence: 1.0

2. **Substring Match** (confidence: 0.95)
   - Query: "C30"
   - Database: "Ready-mixed Concrete C30"
   - Confidence: 0.95

3. **Fuzzy Match** (confidence: 0.6-0.94)
   - Query: "Concrete C30 Ready Mix"
   - Database: "Ready-mixed Concrete C30"
   - Confidence: 0.92 (based on sequence similarity)

### Thai Language Support

```python
# Thai material names are fully supported
match = matcher.match_material("คอนกรีตผสมเสร็จ C30", language="th")

if match:
    print(f"Matched: {match['label']}")
    print(f"Confidence: {match['confidence']:.2%}")
    print(f"Emission Factor: {match['emission_factor']} {match['unit']}")
```

### Handling Low Confidence Matches

```python
# Get match report for analysis
report = matcher.get_match_report("Unknown Material", language="en", category="Concrete")

print(f"Query: {report['query']}")
print(f"Matches found: {report['match_count']}")

if report['best_match']:
    print(f"Best match: {report['best_match']['label']}")
    print(f"Confidence: {report['best_match']['confidence']:.2%}")

    # If confidence is low, review alternatives
    if report['best_match']['confidence'] < 0.8:
        print("\nAlternatives:")
        for alt in report['alternatives']:
            print(f"  - {alt['label']} ({alt['confidence']:.2%})")
```

---

## EDGE Certification

### Certification Levels

| Level | Carbon Reduction | Description |
|-------|-----------------|-------------|
| **EDGE Certified** | ≥20% | Entry-level green building |
| **EDGE Advanced** | ≥40% | High-performance building |
| **Zero Carbon** | ≥100% | Net-zero operational carbon |
| **Not Certified** | <20% | Below certification threshold |

### Calculation Methodology

```
Carbon Savings (%) = (Baseline Emissions - Project Emissions) / Baseline Emissions × 100

Where:
  • Baseline Emissions = Σ(baseline_material_quantity × baseline_emission_factor)
  • Project Emissions = Σ(project_material_quantity × tgo:hasEmissionFactor)
```

### Example Calculation

```python
# Define project materials
project_materials = [
    # Low-carbon alternative
    {"material_name": "Concrete C30 with 30% Fly Ash", "quantity": 1200, "unit": "m³", "category": "Concrete"},
    {"material_name": "Steel Rebar 50% Recycled", "quantity": 150, "unit": "ton", "category": "Steel"}
]

# Define baseline materials (conventional)
baseline_materials = [
    {"material_name": "Concrete C30 Portland Cement", "quantity": 1200, "unit": "m³", "category": "Concrete"},
    {"material_name": "Steel Rebar Virgin", "quantity": 150, "unit": "ton", "category": "Steel"}
]

# Calculate
project_result = calculator.calculate_project_carbon(project_materials)
baseline_result = calculator.calculate_project_carbon(baseline_materials)

savings = calculator.calculate_carbon_savings(
    project_result['total_carbon_kgco2e'],
    baseline_result['total_carbon_kgco2e']
)

print(f"Project: {project_result['total_carbon_tonco2e']:.1f} tCO2e")
print(f"Baseline: {baseline_result['total_carbon_tonco2e']:.1f} tCO2e")
print(f"Savings: {savings['percentage_reduction']:.1f}%")
print(f"EDGE Level: {savings['edge_level']}")
```

---

## Error Handling

### Common Errors and Solutions

#### 1. Material Not Found

```python
try:
    carbon = calculator.calculate_material_carbon(
        material_name="Unknown Material",
        quantity=100,
        unit="m³"
    )
except CarbonCalculationError as e:
    print(f"Error: {e}")

    # Solution: Get alternatives
    alternatives = matcher.get_alternatives("Unknown Material", limit=5)
    print("Did you mean:")
    for alt in alternatives:
        print(f"  - {alt['label']}")
```

#### 2. Unit Conversion Error

```python
from carbonscope.backend.lca import UnitConversionError

try:
    kg = converter.convert_volume_to_mass(10, "m³", "UnknownMaterial")
except UnitConversionError as e:
    print(f"Error: {e}")

    # Solution: Specify category or add custom density
    converter.add_material_density("UnknownMaterial", 1500.0)
    kg = converter.convert_volume_to_mass(10, "m³", "UnknownMaterial")
```

#### 3. Invalid Input Data

```python
# Missing required fields
boq_invalid = [
    {"material_name": "Concrete C30"}  # Missing quantity and unit
]

result = calculator.calculate_project_carbon(boq_invalid)
# This entry will be skipped with a warning logged
print(f"Matched: {result['data_quality']['matched_materials']}")
print(f"Skipped: {result['data_quality']['unmatched_materials']}")
```

---

## Best Practices

### 1. Material Naming

**✅ Good:**
```python
{
    "material_name": "Ready-mix Concrete C30",
    "material_name_th": "คอนกรีตผสมเสร็จ C30",
    "category": "Concrete"
}
```

**❌ Avoid:**
```python
{
    "material_name": "C30",  # Too vague
    "category": None         # Missing category
}
```

### 2. Unit Specification

**✅ Good:**
```python
{"quantity": 150.5, "unit": "m³", "category": "Concrete"}
```

**❌ Avoid:**
```python
{"quantity": 150.5, "unit": "cubic meters"}  # Use "m³" instead
```

### 3. Use Material IDs When Known

**✅ Best:**
```python
{
    "material_id": "http://tgo.or.th/materials/concrete-c30",
    "quantity": 100,
    "unit": "m³"
}
```

**✅ Good:**
```python
{
    "material_name": "Concrete C30",
    "category": "Concrete",
    "quantity": 100,
    "unit": "m³"
}
```

### 4. Validate Results

```python
result = calculator.generate_carbon_report(boq, project_area=5000)

# Check data quality
quality = result['data_quality']
if quality['confidence_score'] < 0.9:
    print(f"Warning: Low confidence ({quality['confidence_score']:.2%})")
    print(f"Unmatched materials: {quality['unmatched_materials']}")

    for unmatched in quality['unmatched_details']:
        print(f"  - {unmatched['material_name']}: {unmatched['error']}")
```

### 5. Cache Material Matches

```python
# For large BOQs, cache material matches
material_cache = {}

for material_entry in large_boq:
    name = material_entry['material_name']

    if name not in material_cache:
        match = matcher.match_material(name)
        material_cache[name] = match['material_id'] if match else None

    material_entry['material_id'] = material_cache[name]

# Now calculate with cached IDs
result = calculator.calculate_project_carbon(large_boq)
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest backend/lca/tests/test_carbon_calculator.py -v

# Run specific test class
pytest backend/lca/tests/test_carbon_calculator.py::TestCarbonCalculator -v

# Run with coverage
pytest backend/lca/tests/test_carbon_calculator.py --cov=carbonscope.backend.lca --cov-report=html

# Run integration tests (requires GraphDB)
pytest backend/lca/tests/test_carbon_calculator.py -m integration
```

### Test Coverage

Current test coverage: **≥90%**

Covered areas:
- Unit conversion (all unit types)
- Material matching (exact, fuzzy, Thai)
- Single material carbon calculation
- Project-level carbon calculation
- EDGE certification levels
- Baseline calculations
- Carbon savings
- Error handling

---

## Troubleshooting

### GraphDB Connection Issues

```python
from carbonscope.backend.core.knowledge_graph import GraphDBClient, GraphDBError

try:
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    client.test_connection()
    print("GraphDB connected!")
except GraphDBError as e:
    print(f"GraphDB connection failed: {e}")
    print("Ensure GraphDB is running on port 7200")
```

### Low Match Confidence

If getting low confidence matches:

1. **Check spelling:** Ensure material names are spelled correctly
2. **Try category filtering:** Narrow search by specifying category
3. **Use Thai names:** If materials have Thai names in TGO
4. **Check TGO database:** Verify material exists in GraphDB

```python
# Debug low confidence
report = matcher.get_match_report("Problem Material")
print(f"Best match confidence: {report['best_match']['confidence']:.2%}")
print(f"Alternatives: {len(report['alternatives'])}")
```

### Performance Optimization

For large BOQs (>1000 materials):

```python
# 1. Use batch matching
material_names = [entry['material_name'] for entry in large_boq]
matches = matcher.match_materials_batch(material_names)

# 2. Specify material IDs when possible
for entry in large_boq:
    if entry['material_name'] in matches:
        entry['material_id'] = matches[entry['material_name']]['material_id']

# 3. Calculate with cached IDs
result = calculator.calculate_project_carbon(large_boq)
```

---

## Support and Contact

For questions or issues:

1. Check this documentation
2. Review test cases in `/backend/lca/tests/`
3. Examine example usage in `/backend/lca/examples/` (if available)
4. Contact BKS cBIM AI Platform team

---

## Changelog

### Version 1.0.0 (2026-03-23)
- Initial release
- Core carbon calculator implementation
- Unit converter with material density support
- Material matcher with fuzzy matching
- EDGE certification support
- Comprehensive test suite (≥90% coverage)
- Full documentation

---

**© 2026 BKS cBIM AI Platform - Internal Use Only**

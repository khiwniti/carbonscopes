# TREES & EDGE Certification Modules

Comprehensive TREES NC 1.1 and EDGE V3 certification calculators for Thai construction projects.

## Overview

This module provides:

1. **TREES NC 1.1 Certification**: Materials & Resources (MR) credits calculation with Gold/Platinum pathway analysis
2. **EDGE V3 Certification**: Embodied carbon baseline, reduction tracking, and compliance checking
3. **Gap Analysis**: Actionable recommendations to achieve certification thresholds
4. **Progress Tracking**: Timeline tracking for certification milestones

## Quick Start

### TREES Certification

```python
from core.knowledge_graph import GraphDBClient
from certification import TREESCertification

# Initialize
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
trees = TREESCertification(client)

# Calculate MR credits
materials = [
    {
        "material_id": "http://tgo.or.th/materials/concrete-c30",
        "value": 150000,  # THB
        "recycled_content": 0.35,  # 35%
        "has_green_label": True
    }
]

mr_credits = trees.calculate_mr_credits(materials)
print(f"Total MR Score: {mr_credits['total_mr_score']}")

# Check pathway to Gold
gold = trees.check_gold_pathway(mr_credits['total_mr_score'])
print(f"Gap to Gold: {gold['gap']} points")
```

### EDGE Certification

```python
from certification import EDGECertification
from decimal import Decimal

# Initialize
edge = EDGECertification(client)

# Calculate baseline
baseline = edge.calculate_baseline(
    project_type="residential",
    floor_area=Decimal("2500")
)

# Calculate reduction
reduction = edge.calculate_reduction(
    actual_carbon=Decimal("560000"),
    baseline_carbon=Decimal(baseline["baseline_total"])
)

# Check compliance
compliance = edge.check_edge_compliance(
    reduction_percentage=Decimal(reduction["reduction_percentage"])
)

print(f"EDGE Certified: {compliance['edge_certified']}")
print(f"Reduction: {reduction['reduction_percentage']:.1f}%")
```

## Module Structure

```
certification/
├── __init__.py              # Package exports
├── trees.py                 # TREES NC 1.1 calculator
├── edge.py                  # EDGE V3 calculator
├── example_usage.py         # Complete examples
├── calculators/
│   ├── mr_credits.py        # TREES MR helpers
│   └── edge_reduction.py    # EDGE reduction helpers
└── tests/
    ├── test_trees.py        # TREES tests (19 tests)
    └── test_edge.py         # EDGE tests (23 tests)
```

## Features

### TREES NC 1.1

- **MR1**: Recycled Materials (target: 30%, max 2 points)
- **MR3**: Sustainable/Green-Labeled Materials (target: 30%, max 2 points)
- **MR4**: Low-Emitting Materials (target: 50%, max 2 points)
- **Gold Pathway**: Analysis for 50+ points threshold
- **Platinum Pathway**: Analysis for 70+ points threshold
- **Gap Analysis**: Effort-rated recommendations (LOW/MEDIUM/HIGH/VERY_HIGH)

### EDGE V3

- **Baseline Calculation**: Regional benchmarks by project type
  - Residential: 280 kgCO2e/m²
  - Commercial: 320 kgCO2e/m²
  - Industrial: 350 kgCO2e/m²
- **Reduction Tracking**: 20% threshold for EDGE certification
- **EDGE Advanced**: 40% energy + 20% embodied carbon
- **Progress Tracking**: Timeline with trend analysis
- **Compliance Reporting**: Comprehensive status reports

## API Reference

### TREESCertification

#### `calculate_mr_credits(materials: List[Dict]) -> Dict`
Calculate Materials & Resources category credits.

**Parameters**:
- `materials`: List of material dictionaries with:
  - `material_id`: Material URI (optional, for GraphDB lookup)
  - `value`: Material value in THB
  - `recycled_content`: Percentage (0-1)
  - `has_green_label`: Boolean
  - `is_low_emission`: Boolean (optional)

**Returns**:
- `mr1_score`: MR1 credit score (0-2)
- `mr3_score`: MR3 credit score (0-2)
- `mr4_score`: MR4 credit score (0-2)
- `total_mr_score`: Total MR score (0-10)
- `recycled_percentage`: % recycled by value
- `green_labeled_percentage`: % green-labeled by value
- `low_emission_percentage`: % low-emission by value

#### `check_gold_pathway(current_score: float) -> Dict`
Analyze pathway to Gold certification (50+ points).

**Returns**:
- `achievable`: Boolean
- `gap`: Points needed
- `estimated_effort`: LOW/MEDIUM/HIGH
- `recommendations`: List of actions

#### `check_platinum_pathway(current_score: float) -> Dict`
Analyze pathway to Platinum certification (70+ points).

#### `generate_certification_report(mr_credits: Dict, other_scores: Dict) -> Dict`
Generate comprehensive certification report.

### EDGECertification

#### `calculate_baseline(project_type: str, floor_area: Decimal) -> Dict`
Calculate baseline embodied carbon.

**Parameters**:
- `project_type`: "residential" | "commercial" | "industrial"
- `floor_area`: Gross floor area in m²

**Returns**:
- `baseline_total`: Total baseline (kgCO2e)
- `baseline_per_sqm`: Carbon per m² (kgCO2e/m²)

#### `calculate_reduction(actual_carbon: Decimal, baseline_carbon: Decimal) -> Dict`
Calculate percentage reduction from baseline.

**Returns**:
- `reduction_percentage`: % reduction
- `reduction_absolute`: Absolute reduction (kgCO2e)
- `meets_edge_threshold`: Boolean (≥20%)
- `gap_percentage`: Gap to 20% target

#### `check_edge_compliance(reduction_percentage: Decimal, ...) -> Dict`
Check EDGE certification compliance.

**Optional Parameters**:
- `energy_reduction`: Energy reduction % (for EDGE Advanced)
- `water_reduction`: Water reduction %

**Returns**:
- `edge_certified`: Boolean
- `edge_advanced`: Boolean
- `embodied_carbon_status`: Compliance details
- `energy_status`: Energy compliance (if provided)
- `water_status`: Water compliance (if provided)
- `recommendations`: List of actions

#### `track_progress(baseline: Dict, measurements: List[Dict]) -> Dict`
Track progress over time.

**Parameters**:
- `baseline`: Baseline calculation result
- `measurements`: List of measurements with:
  - `date`: ISO date string
  - `actual_carbon`: Actual carbon footprint
  - `energy_reduction`: Optional energy %
  - `water_reduction`: Optional water %

**Returns**:
- `progress_timeline`: List of progress points
- `trend`: "IMPROVING" | "DECLINING" | "INSUFFICIENT_DATA"
- `latest_status`: Most recent status

## Testing

Run all tests:
```bash
pytest backend/certification/tests/ -v
```

Run specific test file:
```bash
pytest backend/certification/tests/test_trees.py -v
pytest backend/certification/tests/test_edge.py -v
```

**Test Coverage**: 42 tests, 100% passing
- TREES tests: 19
- EDGE tests: 23

## Configuration

### TREES Thresholds
```python
TREESCertification.GOLD_THRESHOLD = 50      # Gold: 50+ points
TREESCertification.PLATINUM_THRESHOLD = 70  # Platinum: 70+ points
TREESCertification.MR1_MAX = 2              # MR1 max points
TREESCertification.MR3_MAX = 2              # MR3 max points
TREESCertification.MR4_MAX = 2              # MR4 max points
```

### EDGE Thresholds
```python
EDGECertification.EDGE_EMBODIED_CARBON_REDUCTION = Decimal("0.20")  # 20%
EDGECertification.EDGE_ADVANCED_ENERGY_REDUCTION = Decimal("0.40")  # 40%
EDGECertification.EDGE_WATER_REDUCTION = Decimal("0.20")            # 20%
```

## Dependencies

- `decimal`: Precise numeric calculations (Python stdlib)
- `core.knowledge_graph`: GraphDB SPARQL interface
- GraphDB: Running at http://localhost:7200 (optional, uses defaults if unavailable)

## Performance

**TREES MR Credits**:
- 100 materials: <50ms
- 1,000 materials: <200ms

**EDGE Calculations**:
- Baseline: <5ms (regional) / <100ms (detailed)
- Reduction: <1ms
- Compliance: <2ms

**Optimization**: Material property caching reduces GraphDB load by ~80%

## Limitations

1. **TREES**: Only MR category fully implemented
   - EN, WA, WM, IEQ, MG, IN require manual input

2. **EDGE**: Uses default regional baselines
   - May not reflect project-specific conditions

3. **Material Matching**: Requires explicit material_id
   - No fuzzy matching or search

## Future Enhancements

- [ ] Full TREES implementation (all 7 categories)
- [ ] Project-specific EDGE baselines
- [ ] Material search and fuzzy matching
- [ ] PDF report generation
- [ ] API endpoints (REST/GraphQL)
- [ ] Multilingual reports (Thai + English)

## References

- [TREES NC 1.1](https://tgbi.or.th/wp-content/uploads/2024/12/2017_03_TREES-NC-Eng.pdf)
- [EDGE V3 Guidance](https://edgebuildings.com/wp-content/uploads/2024/12/Part-1-EDGE-Building-Certification-Guidance-Rev-1.pdf)
- Phase 1 Research: `.planning/phases/01-foundation-knowledge-infrastructure/01-RESEARCH.md`

## License

Internal use - CarbonBIM Thailand

---

**Version**: 1.0
**Last Updated**: 2026-03-24
**Maintainer**: CarbonBIM Development Team

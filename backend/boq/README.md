# BOQ Parser Module

Thai construction Bill of Quantities (BOQ/วสท.) Excel parser.

## Features

- **Complex Format Support**: Handles merged cells, bilingual headers, nested numbering
- **Thai Unit Normalization**: Converts ลบ.ม., ตัน, ตร.ม. to SI units (m³, kg, m²)
- **Bilingual Error Messages**: Provides errors in Thai and English
- **Deterministic Parsing**: Uses Decimal for all quantities (matches Brightway2)
- **Performance**: <5 seconds for 500-line BOQ files

## Usage

```python
from carbonscope.backend.boq import parse_boq

# Parse Thai BOQ Excel file
result = parse_boq("/path/to/boq.xlsx")

# Check parsing status
print(f"Status: {result.status}")  # parsed, partial, or failed
print(f"Parsed {len(result.materials)} materials")
print(f"Success rate: {result.metadata['success_rate']}%")

# Access parsed materials
for material in result.materials:
    print(f"{material.description_th}: {material.quantity} {material.unit}")

# Handle errors
for error in result.errors:
    print(f"Line {error['line_number']}: {error['message_en']}")
```

## Unit Normalization

Thai units are automatically converted to SI standards:

| Thai Unit | Normalized | Conversion |
|-----------|------------|------------|
| ลบ.ม. | m³ | 1:1 |
| ตร.ม. | m² | 1:1 |
| กก. | kg | 1:1 |
| ตัน | kg | 1000:1 |
| ม. | m | 1:1 |
| เส้น | unit | 1:1 |
| ชุด | unit | 1:1 |

## Testing

Requires 20+ real Thai BOQ Excel samples (see Phase 1 data collection).

```bash
pytest backend/tests/boq/ -v
```

## Phase 2 Requirements

- REQ-BOQ-001: Upload Thai BOQ Excel Files
- REQ-BOQ-002: Parse Complex Thai BOQ Format
- REQ-BOQ-003: Material Quantity Extraction
- REQ-BOQ-004: BOQ Validation & Error Handling

## Next Steps

Phase 2 Plan 02-02 will integrate this parser with material matching engine.

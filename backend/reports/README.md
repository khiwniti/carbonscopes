# Carbon Report Generation System

Professional PDF and Excel report generation for carbon analysis results with bilingual support (Thai + English).

## Overview

This module provides production-ready report generation capabilities for the CarbonBIM platform, including:

- **PDF Reports:** Executive summaries and detailed technical reports with Thai font support
- **Excel Reports:** Multi-sheet workbooks with formulas, formatting, and audit trails
- **Bilingual Support:** Templates in both English and Thai
- **Professional Styling:** Print-optimized layouts with CarbonBIM branding
- **Complete Audit Trails:** Full calculation transparency for certification bodies

## Quick Start

### Generate PDF Report

```python
from reports.generators.pdf_generator import PDFReportGenerator

# Initialize generator
pdf_gen = PDFReportGenerator()

# Generate executive summary (English)
pdf_bytes = pdf_gen.generate_executive_summary(
    data={
        "analysis_id": "550e8400-...",
        "project_name": "Bangkok Condominium",
        "total_carbon": 125000.50,
        "material_count": 45,
        "breakdown": [...],
        # ... other data
    },
    output_path="output/executive_summary.pdf",
    language="en"
)

# Generate detailed report with audit trail (Thai)
pdf_bytes = pdf_gen.generate_detailed_report(
    data=carbon_analysis_data,
    audit_trail=audit_trail_data,
    output_path="output/detailed_report_th.pdf",
    language="th"
)
```

### Generate Excel Report

```python
from reports.generators.excel_generator import ExcelReportGenerator

# Initialize generator
excel_gen = ExcelReportGenerator()

# Generate complete workbook
excel_bytes = excel_gen.generate_report(
    data=carbon_analysis_data,
    audit_trail=audit_trail_data,  # Optional
    output_path="output/carbon_report.xlsx"
)
```

### Use REST API

```bash
# Generate report via API
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "report_type": "both",
    "language": "th",
    "include_audit_trail": true
  }'

# Download generated report
curl "http://localhost:8000/api/v1/reports/{report_id}/download/pdf" \
  -o report.pdf
```

## Architecture

### PDF Generation Pipeline

```
Carbon Data → Jinja2 Template → HTML → WeasyPrint → PDF
                ↓
        Context Preparation
        (formatting, calculations)
```

**Components:**
- **Jinja2 Templates:** HTML templates with dynamic data binding
- **WeasyPrint:** HTML-to-PDF rendering engine with CSS support
- **Font Configuration:** Thai font support (Noto Sans Thai)
- **Custom Filters:** Number, date, and percentage formatting

### Excel Generation Pipeline

```
Carbon Data → openpyxl Workbook → Worksheets → Styled Excel
                ↓
        Multi-sheet creation
        (Summary, Breakdown, Audit Trail, Methodology)
```

**Components:**
- **openpyxl:** Excel workbook manipulation library
- **Styling Engine:** Professional formatting (fonts, colors, borders)
- **Auto-sizing:** Dynamic column width adjustment
- **Formula Support:** TOTAL calculations and data validation

## Features

### PDF Reports

**Executive Summary:**
- Key metrics cards (total carbon, match rate)
- Top carbon contributors table
- Analysis information
- Key findings and recommendations
- 1-2 pages optimized for print

**Detailed Report:**
- Complete material breakdown
- Calculation audit trail (optional)
- Methodology and standards
- Key assumptions and limitations
- Professional multi-page layout

### Excel Reports

**Worksheets:**

1. **Summary:** Key metrics, top 10 contributors, project metadata
2. **Material Breakdown:** Complete material list with carbon calculations
3. **Audit Trail:** Detailed calculation audit (if included)
4. **Methodology:** LCA methodology, assumptions, data sources

**Features:**
- Professional styling (headers, fonts, colors)
- Number formatting (thousands separators, decimals, percentages)
- Auto-sized columns
- Formula support (TOTAL rows)
- Thai Unicode character support

### Bilingual Support

**Languages:**
- English (`language="en"`)
- Thai (`language="th"`)

**Template Pairs:**
- `executive_summary.html` / `executive_summary_th.html`
- `detailed_report.html` / `detailed_report_th.html`

**Features:**
- Thai font rendering (Noto Sans Thai via Google Fonts)
- Localized text and labels
- Date formatting per locale
- Right-to-left layout support (future)

## API Reference

### PDFReportGenerator

```python
class PDFReportGenerator:
    """Generate PDF reports for carbon analysis results."""

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        static_dir: Optional[Path] = None
    ):
        """Initialize PDF generator."""

    def generate_executive_summary(
        self,
        data: Dict[str, Any],
        output_path: Optional[Path] = None,
        language: str = "en"
    ) -> bytes:
        """Generate executive summary PDF report."""

    def generate_detailed_report(
        self,
        data: Dict[str, Any],
        audit_trail: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
        language: str = "en"
    ) -> bytes:
        """Generate detailed technical report with full audit trail."""
```

### ExcelReportGenerator

```python
class ExcelReportGenerator:
    """Generate Excel reports for carbon analysis results."""

    def __init__(self):
        """Initialize Excel generator."""

    def generate_report(
        self,
        data: Dict[str, Any],
        audit_trail: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None
    ) -> bytes:
        """Generate complete Excel report with multiple sheets."""
```

### REST API Endpoints

**POST /api/v1/reports/generate**
- Generate carbon analysis report (PDF and/or Excel)

**GET /api/v1/reports/{report_id}**
- Get report generation status and metadata

**GET /api/v1/reports/{report_id}/download/{file_type}**
- Download generated report file (streaming response)

See [API documentation](../api/v1/reports.py) for details.

## Data Format

### Required Fields

```python
{
    "analysis_id": str,           # UUID
    "project_name": str,          # Project name
    "total_carbon": float,        # Total kgCO2e
    "material_count": int,        # Total materials
    "matched_count": int,         # Matched materials
    "timestamp": str,             # ISO timestamp
    "breakdown": [                # Material breakdown
        {
            "line_number": str,
            "description_th": str,
            "description_en": str,
            "quantity": float,
            "unit": str,
            "carbon": float,
            "percentage": float,
            "match_classification": str
        }
    ],
    "statistics": {               # Match statistics
        "auto_matched": int,
        "review_required": int,
        "rejected": int,
        "auto_match_rate": float
    }
}
```

### Optional Fields

```python
{
    "boq_filename": str,          # BOQ file name
    "tgo_version": str,           # TGO version
    "auto_matched_count": int,    # Auto-matched count
}
```

### Audit Trail Format

```python
{
    "metadata": {
        "analysis_id": str,
        "calculator_version": str,
        "tgo_version": str,
        "brightway_version": str,
        "calculation_date": str
    },
    "material_calculations": [
        {
            "boq_line_number": str,
            "description_th": str,
            "tgo_material_id": str,
            "quantity": float,
            "unit": str,
            "emission_factor_value": float,
            "emission_factor_unit": str,
            "carbon_result": float,
            "calculation_formula": str,
            "match_confidence": float
        }
    ]
}
```

## Customization

### Templates

Templates are located in `reports/templates/`:
- Modify HTML structure
- Add/remove sections
- Customize layout

**Template Variables:** See templates for available Jinja2 variables.

### Styling

CSS is located in `reports/static/css/report.css`:
- Modify colors, fonts, spacing
- Adjust print layout
- Customize branding

**Color Palette:**
```css
--primary: #366092;      /* CarbonBIM blue */
--text: #2c3e50;         /* Dark gray */
--background: #f8f9fa;   /* Light gray */
--success: #27ae60;      /* Green */
--warning: #f39c12;      /* Orange */
```

### Excel Styling

Excel styles are defined in `ExcelReportGenerator` class:
```python
HEADER_STYLE = {
    'font': Font(name='Calibri', size=11, bold=True, color='FFFFFF'),
    'fill': PatternFill(start_color='366092', end_color='366092'),
    # ...
}
```

Modify these constants to change Excel appearance.

## Testing

### Run Tests

```bash
# All report tests
pytest tests/reports/ -v

# PDF generator only
pytest tests/reports/test_pdf_generator.py -v

# Excel generator only
pytest tests/reports/test_excel_generator.py -v

# With coverage
pytest tests/reports/ --cov=reports --cov-report=html
```

### Test Validation Script

```bash
# Quick validation
python test_report_system.py

# Generate sample reports
# (uncomment test_sample_generation() in script)
python test_report_system.py
```

### Performance Benchmarks

```bash
pytest tests/reports/ --benchmark-only
```

**Expected Performance:**
- Executive Summary PDF: < 3s
- Detailed Report PDF: < 5s
- Excel Report: < 2s

## Deployment

### Production Checklist

- [ ] Configure cloud storage (S3/GCS) for report files
- [ ] Set up PostgreSQL for report metadata
- [ ] Implement background task queue (Celery/RQ)
- [ ] Configure CDN for static assets
- [ ] Set up monitoring and logging
- [ ] Implement rate limiting
- [ ] Configure file cleanup cron job

### Environment Variables

```bash
REPORT_STORAGE_BACKEND=s3  # or 'gcs', 'local'
REPORT_STORAGE_BUCKET=carbon-reports
REPORT_TEMP_DIR=/tmp/carbon_reports
REPORT_RETENTION_DAYS=30
ENABLE_BACKGROUND_TASKS=true
```

### Cloud Storage Integration

```python
# Example S3 integration
import boto3

s3_client = boto3.client('s3')

def upload_to_s3(file_bytes, key):
    s3_client.put_object(
        Bucket=REPORT_STORAGE_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType='application/pdf'
    )
    return f"https://{REPORT_STORAGE_BUCKET}.s3.amazonaws.com/{key}"
```

## Troubleshooting

### Thai fonts not rendering

**Problem:** Thai characters appear as boxes or gibberish in PDF.

**Solution:**
- Ensure Google Fonts CDN is accessible
- Or bundle Noto Sans Thai fonts locally
- Verify `@import url(...)` in CSS

### WeasyPrint errors

**Problem:** `OSError: cannot load library` or similar.

**Solution:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0

# macOS
brew install pango
```

### Excel file corrupted

**Problem:** Excel file won't open.

**Solution:**
- Verify all numeric values are valid
- Check for None/null in required fields
- Ensure workbook has at least one worksheet

### Large reports timeout

**Problem:** Report generation times out for 500+ materials.

**Solution:**
- Enable background task processing
- Implement pagination for very large datasets
- Consider splitting into multiple reports

## Examples

See `tests/reports/` for complete examples:
- Mock data fixtures
- Template context preparation
- PDF generation
- Excel generation
- API usage

## License

Copyright © 2026 CarbonBIM. All rights reserved.

## Support

For questions or issues:
- GitHub Issues: https://github.com/cbim-ai/suna/issues
- Documentation: https://docs.carbonbim.com
- Email: support@bks-cbim.com

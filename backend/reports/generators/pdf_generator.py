"""PDF Report Generator using WeasyPrint.

Generates professional carbon analysis reports with:
- Thai font support (Noto Sans Thai)
- Jinja2 template rendering
- SVG chart embedding
- Print-friendly CSS styling
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import base64

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF reports for carbon analysis results."""

    def __init__(self, templates_dir: Optional[Path] = None, static_dir: Optional[Path] = None):
        """Initialize PDF generator.

        Args:
            templates_dir: Path to Jinja2 templates (default: reports/templates/)
            static_dir: Path to static assets (default: reports/static/)
        """
        # Set up paths
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        if static_dir is None:
            static_dir = Path(__file__).parent.parent / "static"

        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.css_dir = static_dir / "css"
        self.fonts_dir = static_dir / "fonts"

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.jinja_env.filters['format_number'] = self._format_number
        self.jinja_env.filters['format_decimal'] = self._format_decimal
        self.jinja_env.filters['format_percentage'] = self._format_percentage
        self.jinja_env.filters['format_date'] = self._format_date

        # Font configuration for Thai support
        self.font_config = FontConfiguration()

        logger.info(f"PDFReportGenerator initialized: templates={templates_dir}, static={static_dir}")

    def generate_executive_summary(
        self,
        data: Dict[str, Any],
        output_path: Optional[Path] = None,
        language: str = "en"
    ) -> bytes:
        """Generate executive summary PDF report.

        Args:
            data: Report data containing:
                - analysis_id: UUID
                - project_name: Project name
                - total_carbon: Total kgCO2e
                - breakdown: List of material breakdowns
                - statistics: Calculation statistics
                - timestamp: ISO timestamp
            output_path: Optional path to save PDF file
            language: Report language ("en" or "th")

        Returns:
            PDF bytes
        """
        logger.info(f"Generating executive summary PDF (language={language})")

        # Select template based on language
        template_name = f"executive_summary_{language}.html" if language == "th" else "executive_summary.html"
        template = self.jinja_env.get_template(template_name)

        # Prepare context data
        context = self._prepare_executive_context(data, language)

        # Render HTML
        html_content = template.render(**context)

        # Convert to PDF
        pdf_bytes = self._render_pdf(html_content)

        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_bytes)
            logger.info(f"Executive summary saved to: {output_path}")

        return pdf_bytes

    def generate_detailed_report(
        self,
        data: Dict[str, Any],
        audit_trail: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
        language: str = "en"
    ) -> bytes:
        """Generate detailed technical report with full audit trail.

        Args:
            data: Report data (same as executive_summary)
            audit_trail: Complete audit trail from calculation pipeline
            output_path: Optional path to save PDF file
            language: Report language ("en" or "th")

        Returns:
            PDF bytes
        """
        logger.info(f"Generating detailed report PDF (language={language})")

        # Select template based on language
        template_name = f"detailed_report_{language}.html" if language == "th" else "detailed_report.html"
        template = self.jinja_env.get_template(template_name)

        # Prepare context data
        context = self._prepare_detailed_context(data, audit_trail, language)

        # Render HTML
        html_content = template.render(**context)

        # Convert to PDF
        pdf_bytes = self._render_pdf(html_content)

        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(pdf_bytes)
            logger.info(f"Detailed report saved to: {output_path}")

        return pdf_bytes

    def _render_pdf(self, html_content: str) -> bytes:
        """Render HTML to PDF using WeasyPrint.

        Args:
            html_content: HTML string to render

        Returns:
            PDF bytes
        """
        # Load CSS stylesheets
        css_files = [
            self.css_dir / "report.css",
        ]
        css_stylesheets = [
            CSS(filename=str(css_file), font_config=self.font_config)
            for css_file in css_files
            if css_file.exists()
        ]

        # Create HTML document
        html = HTML(string=html_content, base_url=str(self.static_dir))

        # Render to PDF
        pdf_bytes = html.write_pdf(
            stylesheets=css_stylesheets,
            font_config=self.font_config
        )

        return pdf_bytes

    def _prepare_executive_context(self, data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Prepare template context for executive summary.

        Args:
            data: Raw report data
            language: Report language

        Returns:
            Template context dictionary
        """
        # Parse timestamp
        timestamp = data.get("timestamp", datetime.now().isoformat())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        # Calculate top carbon contributors (top 5)
        breakdown = data.get("breakdown", [])
        sorted_breakdown = sorted(
            [item for item in breakdown if item.get("carbon")],
            key=lambda x: float(x["carbon"]) if x.get("carbon") else 0,
            reverse=True
        )[:5]

        # Calculate statistics
        total_carbon = float(data.get("total_carbon", 0))
        material_count = data.get("material_count", len(breakdown))
        matched_count = data.get("matched_count", 0)
        match_rate = (matched_count / material_count * 100) if material_count > 0 else 0

        context = {
            "report_title": "Carbon Footprint Executive Summary" if language == "en" else "สรุปผลการวิเคราะห์คาร์บอนฟุตพริ้นท์",
            "project_name": data.get("project_name", "Unnamed Project"),
            "analysis_id": data.get("analysis_id", "N/A"),
            "generated_date": timestamp,
            "total_carbon": total_carbon,
            "total_carbon_tonnes": total_carbon / 1000,  # Convert to tonnes
            "material_count": material_count,
            "matched_count": matched_count,
            "match_rate": match_rate,
            "top_contributors": sorted_breakdown,
            "statistics": data.get("statistics", {}),
            "language": language,
            "current_year": datetime.now().year,
        }

        return context

    def _prepare_detailed_context(
        self,
        data: Dict[str, Any],
        audit_trail: Optional[Dict[str, Any]],
        language: str
    ) -> Dict[str, Any]:
        """Prepare template context for detailed report.

        Args:
            data: Raw report data
            audit_trail: Complete audit trail
            language: Report language

        Returns:
            Template context dictionary
        """
        # Start with executive context
        context = self._prepare_executive_context(data, language)

        # Add detailed information
        context.update({
            "report_title": "Detailed Carbon Analysis Report" if language == "en" else "รายงานการวิเคราะห์คาร์บอนฉบับเต็ม",
            "breakdown": data.get("breakdown", []),
            "audit_trail": audit_trail or {},
            "show_audit_trail": audit_trail is not None,
            "methodology": self._get_methodology_text(language),
            "assumptions": self._get_assumptions_text(language),
        })

        return context

    def _get_methodology_text(self, language: str) -> str:
        """Get methodology description text.

        Args:
            language: Report language

        Returns:
            Methodology description
        """
        if language == "th":
            return """
            การคำนวณคาร์บอนฟุตพริ้นท์ใช้วิธีการประเมินวงจรชีวิต (Life Cycle Assessment - LCA)
            ตามมาตรฐาน ISO 14040 และ ISO 14044 โดยใช้ฐานข้อมูลการปล่อยก๊าซเรือนกระจก TGO
            (Thailand Greenhouse Gas Management Organization) และเครื่องมือคำนวณ Brightway2 LCA framework
            """
        else:
            return """
            Carbon footprint calculation follows Life Cycle Assessment (LCA) methodology
            according to ISO 14040 and ISO 14044 standards, using emission factors from
            TGO (Thailand Greenhouse Gas Management Organization) database and Brightway2
            LCA framework for calculations.
            """

    def _get_assumptions_text(self, language: str) -> List[str]:
        """Get list of key assumptions.

        Args:
            language: Report language

        Returns:
            List of assumption statements
        """
        if language == "th":
            return [
                "ใช้ค่าการปล่อยก๊าซเรือนกระจกจากฐานข้อมูล TGO ปี 2026",
                "คำนวณเฉพาะ embodied carbon ของวัสดุก่อสร้าง (cradle-to-gate)",
                "ไม่รวมการปล่อยก๊าซจากการขนส่งและการติดตั้ง",
                "ใช้ค่าเฉลี่ยสำหรับวัสดุที่ไม่สามารถระบุยี่ห้อหรือแหล่งผลิตได้",
                "การจับคู่วัสดุอัตโนมัติใช้ fuzzy matching ที่ confidence ≥ 0.70",
            ]
        else:
            return [
                "Emission factors from TGO database (2026 version)",
                "Embodied carbon only (cradle-to-gate) for construction materials",
                "Transportation and installation emissions not included",
                "Average values used for materials without specific brand/source",
                "Automated material matching uses fuzzy matching with confidence ≥ 0.70",
            ]

    # Jinja2 custom filters
    def _format_number(self, value: Any) -> str:
        """Format number with thousands separators."""
        try:
            num = float(value)
            return f"{num:,.2f}"
        except (ValueError, TypeError):
            return str(value)

    def _format_decimal(self, value: Any, decimals: int = 2) -> str:
        """Format decimal number."""
        try:
            if isinstance(value, Decimal):
                num = float(value)
            else:
                num = float(value)
            return f"{num:.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    def _format_percentage(self, value: Any, decimals: int = 1) -> str:
        """Format percentage."""
        try:
            num = float(value)
            return f"{num:.{decimals}f}%"
        except (ValueError, TypeError):
            return str(value)

    def _format_date(self, value: Any, format: str = "%Y-%m-%d") -> str:
        """Format date/datetime."""
        if isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except:
                return value
        return str(value)

    def embed_svg_chart(self, chart_data: Dict[str, Any], chart_type: str = "bar") -> str:
        """Generate SVG chart for embedding in PDF.

        Args:
            chart_data: Chart data (labels, values, colors)
            chart_type: Chart type ("bar", "pie", "line")

        Returns:
            SVG string
        """
        # Simple SVG generation for basic charts
        # For production, consider using matplotlib or plotly
        logger.warning("SVG chart embedding is a stub - implement with matplotlib/plotly")

        return f'<svg width="400" height="300"><text x="10" y="20">Chart: {chart_type}</text></svg>'

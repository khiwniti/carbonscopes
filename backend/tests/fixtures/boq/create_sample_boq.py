"""
Create sample BOQ Excel file for testing.

Run this script to generate sample_boq.xlsx in the same directory.
"""

import openpyxl
from pathlib import Path
from decimal import Decimal


def create_sample_boq():
    """Create sample Thai BOQ Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BOQ"

    # Header row (row 1)
    headers = [
        "ลำดับ",  # Item No
        "รายการ",  # Description (Thai)
        "Description",  # Description (English)
        "หน่วย",  # Unit
        "จำนวน"  # Quantity
    ]
    ws.append(headers)

    # Make headers bold
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # Sample materials
    materials = [
        [1, "คอนกรีตผสมเสร็จ fc' 210 kg/cm2", "Ready-mix concrete fc' 210 kg/cm2", "ลบ.ม.", 50.5],
        [2, "เหล็กเส้นกลม SR24", "Round steel bar SR24", "กก.", 2500.0],
        [3, "อิฐมอญ", "Clay brick", "ก้อน", 15000],
        [4, "ปูนซีเมนต์ปอร์ตแลนด์ประเภท 1", "Portland cement type 1", "ตัน", 12.5],
        [5, "ทราย", "Sand", "ตร.ม.", 80.0],
        [6, "แผ่นกระเบื้องเซรามิก 30x30 ซม.", "Ceramic tile 30x30 cm", "ตร.ม.", 150.0],
        [7, "เหล็กข้ออ้อย SD40", "Deformed bar SD40", "กก.", 1800.0],
        [8, "กระจกใส 5 มม.", "Clear glass 5mm", "ตร.ม.", 45.0],
        [9, "สีทาภายนอก", "Exterior paint", "แกลลอน", 25],
        [10, "ท่อ PVC 4 นิ้ว", "PVC pipe 4 inch", "ท่อน", 120]
    ]

    for material in materials:
        ws.append(material)

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save file
    output_path = Path(__file__).parent / "sample_boq.xlsx"
    wb.save(output_path)
    print(f"Sample BOQ file created: {output_path}")


if __name__ == "__main__":
    create_sample_boq()

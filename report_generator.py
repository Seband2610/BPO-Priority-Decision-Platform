
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


REPORT_DIR = Path(__file__).parent / "reports"


def generate_report(requests):
    REPORT_DIR.mkdir(exist_ok=True)

    report_path = REPORT_DIR / "BPO_Priority_Report.xlsx"

    workbook = Workbook()

    # Summary sheet
    summary = workbook.active
    summary.title = "Summary"

    critical = sum(
        1 for r in requests
        if r["decision"] == "CRITICAL ATTENTION"
    )
    normal = len(requests) - critical

    summary_data = [
        ["BPO PRIORITY DECISION PLATFORM"],
        ["Report Summary"],
        ["Total Requests", len(requests)],
        ["Critical Attention", critical],
        ["Normal Processing", normal],
    ]

    for row in summary_data:
        summary.append(row)

    # Requests sheet
    sheet = workbook.create_sheet("Requests")

    columns = [
        "Request ID",
        "Customer",
        "Issue",
        "Category",
        "Urgency",
        "SLA Hours",
        "Customer Tier",
        "Priority Score",
        "Priority",
        "Decision",
        "Reason"
    ]

    sheet.append(columns)

    for request in requests:
        sheet.append([
            request["request_id"],
            request["customer"],
            request["issue"],
            request["category"],
            request["urgency"],
            request["sla_hours"],
            request["customer_tier"],
            request["priority_score"],
            request["priority"],
            request["decision"],
            request["reason"]
        ])

    # Format headers
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="142D4E"
        )
        cell.alignment = Alignment(horizontal="center")

    for cell in summary[1]:
        cell.font = Font(bold=True, size=16, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="142D4E"
        )

    for cell in summary[2]:
        cell.font = Font(bold=True, color="142D4E")

    # Adjust column widths
    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )
        sheet.column_dimensions[
            get_column_letter(column[0].column)
        ].width = min(max_length + 3, 45)

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    summary.column_dimensions["A"].width = 28
    summary.column_dimensions["B"].width = 20

    workbook.save(report_path)

    return report_path

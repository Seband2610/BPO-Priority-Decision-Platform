from pathlib import Path

from datetime import datetime

import matplotlib



matplotlib.use("Agg")



import matplotlib.pyplot as plt



from docx import Document

from docx.shared import Inches, Pt, RGBColor

from docx.enum.text import WD_ALIGN_PARAGRAPH

from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

from docx.oxml import OxmlElement

from docx.oxml.ns import qn





BASE_DIR = Path(__file__).parent

REPORT_DIR = BASE_DIR / "reports"

CHART_DIR = REPORT_DIR / "charts"



NAVY = "142D4E"

BLUE = "2874C7"

LIGHT_BLUE = "EAF1F8"

RED = "C0392B"

ORANGE = "E67E22"

GREEN = "27864B"

GRAY = "667085"





def shade_cell(cell, color):

    properties = cell._tc.get_or_add_tcPr()

    shading = OxmlElement("w:shd")

    shading.set(qn("w:fill"), color)

    properties.append(shading)





def set_cell_text(cell, value, bold=False, color="333333", size=9):

    cell.text = str(value if value is not None else "")

    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER



    for paragraph in cell.paragraphs:

        for run in paragraph.runs:

            run.bold = bold

            run.font.name = "Arial"

            run.font.size = Pt(size)

            run.font.color.rgb = RGBColor.from_string(color)





def style_table(table):

    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    table.style = "Table Grid"



    for cell in table.rows[0].cells:

        shade_cell(cell, NAVY)



        for paragraph in cell.paragraphs:

            for run in paragraph.runs:

                run.bold = True

                run.font.color.rgb = RGBColor(255, 255, 255)

                run.font.size = Pt(9)





def add_table(document, headers, rows):

    table = document.add_table(rows=1, cols=len(headers))



    for index, header in enumerate(headers):

        set_cell_text(

            table.rows[0].cells[index],

            header,

            bold=True,

            color="FFFFFF"

        )



    style_table(table)



    for row in rows:

        cells = table.add_row().cells



        for index, value in enumerate(row):

            set_cell_text(cells[index], value)



    document.add_paragraph()

    return table





def add_heading(document, text, level=1):

    heading = document.add_heading(text, level=level)



    for run in heading.runs:

        run.font.name = "Arial"

        run.font.color.rgb = RGBColor.from_string(NAVY)



    return heading





def add_paragraph(document, text, bold_prefix=None):

    paragraph = document.add_paragraph()



    if bold_prefix and text.startswith(bold_prefix):

        paragraph.add_run(bold_prefix).bold = True

        paragraph.add_run(text[len(bold_prefix):])

    else:

        paragraph.add_run(str(text))



    for run in paragraph.runs:

        run.font.name = "Arial"

        run.font.size = Pt(10)



    return paragraph





def create_charts(requests):

    CHART_DIR.mkdir(parents=True, exist_ok=True)



    priority_counts = {

        "CRITICAL": 0,

        "HIGH": 0,

        "MEDIUM": 0,

        "LOW": 0

    }



    category_counts = {}



    for request in requests:

        priority = request.get("priority", "UNKNOWN")

        if priority in priority_counts:

            priority_counts[priority] += 1



        category = str(request.get("category", "Unspecified"))

        category_counts[category] = category_counts.get(category, 0) + 1



    priority_path = CHART_DIR / "priority_distribution.png"



    fig, ax = plt.subplots(figsize=(8, 4.5))

    labels = list(priority_counts.keys())

    values = list(priority_counts.values())



    bars = ax.bar(

        labels,

        values,

        color=["#C0392B", "#E67E22", "#2874C7", "#27864B"]

    )



    ax.set_title("Request Distribution by Priority")

    ax.set_ylabel("Number of Requests")

    ax.set_ylim(0, max(values + [1]) * 1.2)

    ax.grid(axis="y", alpha=0.2)



    for bar, value in zip(bars, values):

        ax.text(

            bar.get_x() + bar.get_width() / 2,

            bar.get_height(),

            str(value),

            ha="center",

            va="bottom"

        )



    fig.tight_layout()

    fig.savefig(priority_path, dpi=180)

    plt.close(fig)



    category_path = CHART_DIR / "category_distribution.png"



    fig, ax = plt.subplots(figsize=(8, 4.5))



    categories = list(category_counts.keys())

    category_values = list(category_counts.values())



    bars = ax.barh(categories, category_values, color="#2874C7")



    ax.set_title("Requests by Business Category")

    ax.set_xlabel("Number of Requests")

    ax.grid(axis="x", alpha=0.2)



    for bar, value in zip(bars, category_values):

        ax.text(

            bar.get_width(),

            bar.get_y() + bar.get_height() / 2,

            f" {value}",

            va="center"

        )



    fig.tight_layout()

    fig.savefig(category_path, dpi=180)

    plt.close(fig)



    return priority_path, category_path, priority_counts, category_counts





def add_request_details(document, requests, title):

    add_heading(document, title, level=1)



    if not requests:

        add_paragraph(document, "No requests were recorded in this section.")

        return



    for request in requests:

        request_id = request.get("request_id", "N/A")

        customer = request.get("customer", "N/A")



        add_heading(

            document,

            f"{request_id} - {customer}",

            level=2

        )



        details = [

            ["Reported issue", request.get("issue", "N/A")],

            ["Business category", request.get("category", "N/A")],

            ["Urgency level", request.get("urgency", "N/A")],

            ["SLA commitment (hours)", request.get("sla_hours", "N/A")],

            ["Customer tier", request.get("customer_tier", "N/A")],

            ["Priority score", request.get("priority_score", "N/A")],

            ["Priority classification", request.get("priority", "N/A")],

            ["Management decision", request.get("decision", "N/A")],

            ["Assessment explanation", request.get("reason", "Not provided")]

        ]



        add_table(document, ["Information", "Assessment"], details)





def generate_report(requests):

    """Generate a detailed executive report in Word format."""



    REPORT_DIR.mkdir(parents=True, exist_ok=True)



    report_path = REPORT_DIR / "BPO_Executive_Management_Report.docx"



    critical_requests = [

        r for r in requests

        if r.get("decision") == "CRITICAL ATTENTION"

    ]



    normal_requests = [

        r for r in requests

        if r.get("decision") != "CRITICAL ATTENTION"

    ]



    total = len(requests)



    priority_path, category_path, priority_counts, category_counts = (

        create_charts(requests)

    )



    premium_count = sum(

        1 for r in requests

        if str(r.get("customer_tier", "")).strip().lower() == "premium"

    )



    sla_urgent = sum(

        1 for r in requests

        if int(r.get("sla_hours", 0)) <= 2

    )



    average_score = (

        sum(float(r.get("priority_score", 0)) for r in requests) / total

        if total else 0

    )



    document = Document()



    section = document.sections[0]

    section.top_margin = Inches(0.65)

    section.bottom_margin = Inches(0.65)

    section.left_margin = Inches(0.75)

    section.right_margin = Inches(0.75)



    styles = document.styles

    styles["Normal"].font.name = "Arial"

    styles["Normal"].font.size = Pt(10)



    # Cover

    for _ in range(3):

        document.add_paragraph()



    title = document.add_heading(

        "BPO PRIORITY DECISION PLATFORM",

        level=0

    )

    title.alignment = WD_ALIGN_PARAGRAPH.CENTER



    for run in title.runs:

        run.font.color.rgb = RGBColor.from_string(NAVY)

        run.font.size = Pt(23)



    subtitle = document.add_paragraph()

    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER



    run = subtitle.add_run("EXECUTIVE MANAGEMENT REPORT")

    run.bold = True

    run.font.size = Pt(17)

    run.font.color.rgb = RGBColor.from_string(BLUE)



    document.add_paragraph()

    date_paragraph = document.add_paragraph(

        f"Reporting date: {datetime.now().strftime('%B %d, %Y')}"

    )

    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER



    date_paragraph = document.add_paragraph(

        "Confidential - Internal Business Use"

    )

    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER



    document.add_page_break()



    # Executive summary

    add_heading(document, "1. Executive Summary")



    add_paragraph(

        document,

        "This report presents the results of the review of business "

        "requests registered in the BPO Priority Decision Platform. "

        "It summarizes the workload, identifies cases requiring "

        "management attention and provides information to support "

        "operational decisions."

    )



    summary_rows = [

        ["Total requests analyzed", total],

        ["Requests requiring critical attention", len(critical_requests)],

        ["Requests under normal processing", len(normal_requests)],

        ["Premium customers", premium_count],

        ["Requests with SLA of 2 hours or less", sla_urgent],

        ["Average priority score", f"{average_score:.2f}"]

    ]



    add_table(

        document,

        ["Management indicator", "Result"],

        summary_rows

    )



    # Priority analysis

    add_heading(document, "2. Priority Distribution")



    document.add_picture(

        str(priority_path),

        width=Inches(6.2)

    )



    add_table(

        document,

        ["Priority", "Requests"],

        [[key, value] for key, value in priority_counts.items()]

    )



    # Category analysis

    add_heading(document, "3. Business Category Analysis")



    document.add_picture(

        str(category_path),

        width=Inches(6.2)

    )



    add_table(

        document,

        ["Category", "Requests"],

        sorted(

            category_counts.items(),

            key=lambda item: item[1],

            reverse=True

        )

    )



    # SLA analysis

    add_heading(document, "4. Service Level Analysis")



    add_paragraph(

        document,

        "The following indicators identify requests with the shortest "

        "service commitments. These cases may require closer monitoring "

        "to reduce the risk of missed service deadlines."

    )



    sla_rows = []



    for request in sorted(

        requests,

        key=lambda r: int(r.get("sla_hours", 0))

    ):

        sla_rows.append([

            request.get("request_id", ""),

            request.get("customer", ""),

            request.get("sla_hours", ""),

            request.get("priority", ""),

            request.get("decision", "")

        ])



    add_table(

        document,

        ["Request ID", "Customer", "SLA Hours", "Priority", "Decision"],

        sla_rows

    )



    # Critical requests

    document.add_page_break()



    add_heading(document, "5. Requests Requiring Critical Attention")



    add_paragraph(

        document,

        f"{len(critical_requests)} requests have been classified for "

        "critical attention. These cases should be reviewed and assigned "

        "according to their urgency and service commitments."

    )



    add_request_details(

        document,

        critical_requests,

        "Critical Request Details"

    )



    # Normal requests

    document.add_page_break()



    add_heading(document, "6. Normal Processing Requests")



    add_paragraph(

        document,

        f"{len(normal_requests)} requests remain under normal processing. "

        "They should continue to be monitored according to their service "

        "commitments and operational status."

    )



    add_request_details(

        document,

        normal_requests,

        "Normal Request Details"

    )



    # Methodology

    document.add_page_break()



    add_heading(document, "7. Assessment Methodology")



    add_paragraph(

        document,

        "The platform calculates a priority score using three business "

        "factors: reported urgency, service level agreement (SLA) and "

        "customer tier."

    )



    methodology_rows = [

        ["Urgency 9-10", "+5 points"],

        ["Urgency 7-8", "+3 points"],

        ["Urgency 4-6", "+2 points"],

        ["Urgency below 4", "+1 point"],

        ["SLA of 2 hours or less", "+4 points"],

        ["SLA of 3-4 hours", "+3 points"],

        ["SLA of 5-8 hours", "+2 points"],

        ["Premium customer", "+2 points"],

        ["Score 9 or higher", "CRITICAL"],

        ["Score 7-8", "HIGH"],

        ["Score 4-6", "MEDIUM"],

        ["Score below 4", "LOW"]

    ]



    add_table(

        document,

        ["Assessment factor", "Points / Classification"],

        methodology_rows

    )



    add_paragraph(

        document,

        "Management decision: CRITICAL and HIGH priorities are classified "

        "as CRITICAL ATTENTION. MEDIUM and LOW priorities are classified "

        "as NORMAL PROCESSING."

    )



    # Conclusions

    add_heading(document, "8. Management Conclusions and Recommendations")



    if critical_requests:

        add_paragraph(

            document,

            f"1. Review and assign the {len(critical_requests)} requests "

            "requiring critical attention as a priority."

        )

    else:

        add_paragraph(

            document,

            "1. No requests currently require critical attention."

        )



    add_paragraph(

        document,

        f"2. Monitor the {sla_urgent} requests with an SLA of two hours "

        "or less to reduce the risk of service delays."

    )



    add_paragraph(

        document,

        "3. Maintain regular follow-up of normal processing requests "

        "to ensure that their service commitments are respected."

    )



    add_paragraph(

        document,

        "4. Review the priority distribution and business categories "

        "regularly to identify recurring operational issues."

    )



    add_paragraph(

        document,

        "5. Use this report as a management support document and validate "

        "case-specific actions with the responsible operational teams."

    )



    # Footer

    for section in document.sections:

        footer = section.footer.paragraphs[0]

        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER



        run = footer.add_run(

            "BPO Priority Decision Platform | Confidential Management Report"

        )

        run.font.size = Pt(8)

        run.font.color.rgb = RGBColor.from_string(GRAY)



    document.save(report_path)



    return report_path

def create_segment_charts(requests, prefix):
    """Create charts with unique filenames for a filtered report."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    priority_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
    category_counts = {}

    for request in requests:
        priority = request.get("priority", "UNKNOWN")
        if priority in priority_counts:
            priority_counts[priority] += 1

        category = str(request.get("category", "Unspecified"))
        category_counts[category] = category_counts.get(category, 0) + 1

    priority_path = CHART_DIR / f"{prefix}_priority_distribution.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = list(priority_counts.keys())
    values = list(priority_counts.values())
    bars = ax.bar(
        labels,
        values,
        color=["#C0392B", "#E67E22", "#2874C7", "#27864B"]
    )
    ax.set_title("Request Distribution by Priority")
    ax.set_ylabel("Number of Requests")
    ax.set_ylim(0, max(values + [1]) * 1.2)
    ax.grid(axis="y", alpha=0.2)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom"
        )

    fig.tight_layout()
    fig.savefig(priority_path, dpi=180)
    plt.close(fig)

    category_path = CHART_DIR / f"{prefix}_category_distribution.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))
    categories = list(category_counts.keys())
    category_values = list(category_counts.values())
    bars = ax.barh(categories, category_values, color="#2874C7")
    ax.set_title("Requests by Business Category")
    ax.set_xlabel("Number of Requests")
    ax.grid(axis="x", alpha=0.2)

    for bar, value in zip(bars, category_values):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {value}",
            va="center"
        )

    fig.tight_layout()
    fig.savefig(category_path, dpi=180)
    plt.close(fig)

    return priority_path, category_path, priority_counts, category_counts


def generate_segment_report(requests, report_type):
    """
    Generate a standalone report for either critical-attention or
    normal-processing requests. The existing general report is untouched.
    """
    report_config = {
        "critical": {
            "filename": "BPO_Critical_Requests_Report.docx",
            "title": "CRITICAL REQUESTS REPORT",
            "section_title": "Requests Requiring Critical Attention",
            "intro": (
                "This report contains only requests classified as "
                "CRITICAL ATTENTION. This group includes CRITICAL and HIGH "
                "priority requests."
            ),
            "decision": "CRITICAL ATTENTION"
        },
        "normal": {
            "filename": "BPO_Normal_Requests_Report.docx",
            "title": "NORMAL REQUESTS REPORT",
            "section_title": "Requests Under Normal Processing",
            "intro": (
                "This report contains only requests classified as "
                "NORMAL PROCESSING. This group includes MEDIUM and LOW "
                "priority requests."
            ),
            "decision": "NORMAL PROCESSING"
        }
    }

    if report_type not in report_config:
        raise ValueError("report_type must be 'critical' or 'normal'.")

    config = report_config[report_type]
    filtered_requests = [
        request for request in requests
        if request.get("decision") == config["decision"]
    ]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / config["filename"]

    total = len(filtered_requests)
    critical_count = sum(
        1 for request in filtered_requests
        if request.get("priority") in ("CRITICAL", "HIGH")
    )
    normal_count = sum(
        1 for request in filtered_requests
        if request.get("priority") in ("MEDIUM", "LOW")
    )
    premium_count = sum(
        1 for request in filtered_requests
        if str(request.get("customer_tier", "")).strip().lower() == "premium"
    )

    def safe_int(value, default=0):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    sla_urgent = sum(
        1 for request in filtered_requests
        if safe_int(request.get("sla_hours", 0)) <= 2
    )
    average_score = (
        sum(
            float(request.get("priority_score", 0) or 0)
            for request in filtered_requests
        ) / total
        if total else 0
    )

    priority_path, category_path, priority_counts, category_counts = (
        create_segment_charts(filtered_requests, report_type)
    )

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    document.styles["Normal"].font.name = "Arial"
    document.styles["Normal"].font.size = Pt(10)

    # Cover page
    for _ in range(3):
        document.add_paragraph()

    title = document.add_heading(
        "BPO PRIORITY DECISION PLATFORM",
        level=0
    )
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor.from_string(NAVY)
        run.font.size = Pt(23)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(config["title"])
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor.from_string(
        RED if report_type == "critical" else BLUE
    )

    document.add_paragraph()
    date_paragraph = document.add_paragraph(
        f"Reporting date: {datetime.now().strftime('%B %d, %Y')}"
    )
    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    confidentiality = document.add_paragraph(
        "Confidential - Internal Business Use"
    )
    confidentiality.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_page_break()

    # Executive summary for this group only
    add_heading(document, "1. Executive Summary")
    add_paragraph(document, config["intro"])

    summary_rows = [
        ["Requests in this report", total],
        ["CRITICAL priority requests", priority_counts["CRITICAL"]],
        ["HIGH priority requests", priority_counts["HIGH"]],
        ["MEDIUM priority requests", priority_counts["MEDIUM"]],
        ["LOW priority requests", priority_counts["LOW"]],
        ["Premium customers", premium_count],
        ["Requests with SLA of 2 hours or less", sla_urgent],
        ["Average priority score", f"{average_score:.2f}"]
    ]
    add_table(
        document,
        ["Management indicator", "Result"],
        summary_rows
    )

    add_heading(document, "2. Priority Distribution")
    document.add_picture(str(priority_path), width=Inches(6.2))
    add_table(
        document,
        ["Priority", "Requests"],
        [[priority, count] for priority, count in priority_counts.items()]
    )

    add_heading(document, "3. Business Category Analysis")
    if category_counts:
        document.add_picture(str(category_path), width=Inches(6.2))
        add_table(
            document,
            ["Category", "Requests"],
            sorted(
                category_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
    else:
        add_paragraph(document, "No category data is available.")

    add_heading(document, "4. Service Level Analysis")
    add_paragraph(
        document,
        "The following table lists only the requests included in this report, "
        "ordered by the shortest SLA commitment."
    )

    sla_rows = []
    for request in sorted(
        filtered_requests,
        key=lambda item: safe_int(item.get("sla_hours", 0), 0)
    ):
        sla_rows.append([
            request.get("request_id", ""),
            request.get("customer", ""),
            request.get("sla_hours", ""),
            request.get("priority", ""),
            request.get("decision", "")
        ])

    add_table(
        document,
        ["Request ID", "Customer", "SLA Hours", "Priority", "Decision"],
        sla_rows
    )

    document.add_page_break()
    add_request_details(
        document,
        filtered_requests,
        f"5. {config['section_title']}"
    )

    document.add_heading("6. Assessment Methodology", level=1)
    add_paragraph(
        document,
        "The platform calculates a priority score using reported urgency, "
        "service level agreement (SLA), and customer tier."
    )

    methodology_rows = [
        ["Urgency 9-10", "+5 points"],
        ["Urgency 7-8", "+3 points"],
        ["Urgency 4-6", "+2 points"],
        ["Urgency below 4", "+1 point"],
        ["SLA of 2 hours or less", "+4 points"],
        ["SLA of 3-4 hours", "+3 points"],
        ["SLA of 5-8 hours", "+2 points"],
        ["Premium customer", "+2 points"],
        ["Score 9 or higher", "CRITICAL"],
        ["Score 7-8", "HIGH"],
        ["Score 4-6", "MEDIUM"],
        ["Score below 4", "LOW"]
    ]
    add_table(
        document,
        ["Assessment factor", "Points / Classification"],
        methodology_rows
    )
    add_paragraph(
        document,
        "Management decision: CRITICAL and HIGH priorities are classified "
        "as CRITICAL ATTENTION. MEDIUM and LOW priorities are classified "
        "as NORMAL PROCESSING."
    )

    document.add_heading("7. Management Recommendations", level=1)
    if report_type == "critical":
        add_paragraph(
            document,
            f"1. Review and assign all {total} requests in this report "
            "according to urgency and contractual service commitments."
        )
        add_paragraph(
            document,
            "2. Give immediate attention to requests with an SLA of two "
            "hours or less."
        )
        add_paragraph(
            document,
            "3. Confirm an owner, action plan, and follow-up for every case."
        )
    else:
        add_paragraph(
            document,
            f"1. Continue operational processing of the {total} requests "
            "included in this report."
        )
        add_paragraph(
            document,
            "2. Monitor SLA commitments to prevent requests from becoming "
            "critical."
        )
        add_paragraph(
            document,
            "3. Reassess priority if urgency, SLA, or customer impact changes."
        )

    # Footer
    for doc_section in document.sections:
        footer = doc_section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.add_run(
            "BPO Priority Decision Platform | Confidential Management Report"
        )
        footer_run.font.size = Pt(8)
        footer_run.font.color.rgb = RGBColor.from_string(GRAY)

    document.save(report_path)
    return report_path


def generate_critical_report(requests):
    """Generate a report containing CRITICAL and HIGH requests."""
    return generate_segment_report(requests, "critical")


def generate_normal_report(requests):
    """Generate a report containing MEDIUM and LOW requests."""
    return generate_segment_report(requests, "normal")


def generate_all_reports(requests):
    """
    Generate the existing general report plus two separate reports.
    The general report is generated by the original generate_report()
    function without changing its content or output filename.
    """
    general_path = generate_report(requests)
    critical_path = generate_critical_report(requests)
    normal_path = generate_normal_report(requests)

    return {
        "general": general_path,
        "critical": critical_path,
        "normal": normal_path
    }

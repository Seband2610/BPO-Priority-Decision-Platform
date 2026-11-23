from flask import (
    Flask, render_template, send_file, request,
    redirect, url_for, flash
)

from main import process_requests
from report_generator import generate_report
from excel_reader import (
    save_additional_requests,
    read_uploaded_excel,
    update_existing_request,
    delete_existing_request
)


app = Flask(__name__)
app.secret_key = "bpo-local-platform-key"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def get_dashboard_data():
    requests_data = process_requests()

    total = len(requests_data)
    critical = sum(1 for r in requests_data if r["priority"] == "CRITICAL")
    high = sum(1 for r in requests_data if r["priority"] == "HIGH")
    medium = sum(1 for r in requests_data if r["priority"] == "MEDIUM")
    low = sum(1 for r in requests_data if r["priority"] == "LOW")

    critical_attention = sum(
        1 for r in requests_data
        if r["decision"] == "CRITICAL ATTENTION"
    )

    return {
        "requests": requests_data,
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "critical_attention": critical_attention,
        "normal": total - critical_attention
    }


@app.route("/")
def dashboard():
    return render_template("index.html", **get_dashboard_data())


@app.route("/requests/add", methods=["GET", "POST"])
def add_request():
    if request.method == "POST":
        new_request = {
            "request_id": request.form.get("request_id", ""),
            "customer": request.form.get("customer", ""),
            "issue": request.form.get("issue", ""),
            "urgency": request.form.get("urgency", ""),
            "category": request.form.get("category", ""),
            "customer_tier": request.form.get("customer_tier", ""),
            "sla_hours": request.form.get("sla_hours", ""),
            "status": request.form.get("status", "Open")
        }

        try:
            save_additional_requests([new_request])
            flash("Request added successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as error:
            flash(str(error), "error")

    return render_template("add_requests.html")


@app.route("/requests/import", methods=["POST"])
def import_requests():
    uploaded_file = request.files.get("excel_file")

    if not uploaded_file or not uploaded_file.filename:
        flash("Please select an Excel file.", "error")
        return redirect(url_for("add_request"))

    if not uploaded_file.filename.lower().endswith(".xlsx"):
        flash("Please upload an .xlsx file.", "error")
        return redirect(url_for("add_request"))

    try:
        records = read_uploaded_excel(uploaded_file)
        total_added = save_additional_requests(records)

        flash(
            f"{total_added} requests imported successfully.",
            "success"
        )
    except Exception as error:
        flash(str(error), "error")

    return redirect(url_for("add_request"))


@app.route("/requests/<request_id>/edit", methods=["GET", "POST"])
def edit_request(request_id):
    requests_data = process_requests()

    current_request = next(
        (
            item for item in requests_data
            if item["request_id"].strip().lower() == request_id.strip().lower()
        ),
        None
    )

    if current_request is None:
        flash("Request not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        updated_record = {
            "request_id": current_request["request_id"],
            "customer": request.form.get("customer", ""),
            "issue": request.form.get("issue", ""),
            "urgency": request.form.get("urgency", ""),
            "category": request.form.get("category", ""),
            "customer_tier": request.form.get("customer_tier", ""),
            "sla_hours": request.form.get("sla_hours", ""),
            "status": request.form.get("status", "Open")
        }

        try:
            update_existing_request(request_id, updated_record)
            flash("Request updated successfully.", "success")
            return redirect(url_for("dashboard"))
        except Exception as error:
            flash(str(error), "error")

    return render_template(
        "edit_request.html",
        request=current_request
    )


@app.route("/requests/<request_id>/delete", methods=["POST"])
def remove_request(request_id):
    try:
        delete_existing_request(request_id)
        flash(
            f"Request {request_id} was removed from the platform.",
            "success"
        )
    except Exception as error:
        flash(str(error), "error")

    return redirect(url_for("dashboard"))


@app.route("/download-report")
def download_report():
    requests_data = process_requests()
    report_path = generate_report(requests_data)

    return send_file(
        report_path,
        as_attachment=True,
        download_name="BPO_Executive_Management_Report.docx"
    )


if __name__ == "__main__":
    app.run(debug=True)

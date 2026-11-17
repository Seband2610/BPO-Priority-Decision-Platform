import json
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "data" / "BPO_Decision_Platform_Dataset.xlsx"
ADDITIONAL_PATH = BASE_DIR / "data" / "additional_requests.json"

REQUIRED_COLUMNS = [
    "request_id",
    "customer",
    "issue",
    "urgency",
    "category",
    "customer_tier",
    "sla_hours",
    "status"
]


def validate_records(records):
    validated = []

    for record in records:
        clean = {
            column: str(record.get(column, "")).strip()
            for column in REQUIRED_COLUMNS
        }

        if not clean["request_id"]:
            raise ValueError("Every request must have a request_id.")

        if not clean["customer"] or not clean["issue"]:
            raise ValueError("Customer and issue are required.")

        try:
            urgency = int(float(clean["urgency"]))
            sla_hours = float(clean["sla_hours"])
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid urgency or SLA in request {clean['request_id']}."
            )

        if not 1 <= urgency <= 10:
            raise ValueError(
                f"Urgency must be between 1 and 10: {clean['request_id']}."
            )

        if sla_hours < 0:
            raise ValueError(
                f"SLA cannot be negative: {clean['request_id']}."
            )

        clean["urgency"] = urgency
        clean["sla_hours"] = sla_hours
        validated.append(clean)

    return validated


def load_additional_requests():
    if not ADDITIONAL_PATH.exists():
        return []

    with open(ADDITIONAL_PATH, "r", encoding="utf-8") as file:
        records = json.load(file)

    return validate_records(records)


def load_requests():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Excel file not found: {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH)

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing Excel columns: {missing}")

    original_records = validate_records(
        df[REQUIRED_COLUMNS].fillna("").to_dict(orient="records")
    )

    additional_records = load_additional_requests()

    all_records = original_records + additional_records

    seen_ids = set()

    for record in all_records:
        request_id = record["request_id"].strip().lower()

        if request_id in seen_ids:
            raise ValueError(f"Duplicate request ID found: {record['request_id']}")

        seen_ids.add(request_id)

    return all_records


def save_additional_requests(new_records):
    existing = load_requests()
    existing_ids = {
        record["request_id"].strip().lower()
        for record in existing
    }

    validated = validate_records(new_records)
    new_ids = set()

    for record in validated:
        request_id = record["request_id"].strip().lower()

        if request_id in existing_ids or request_id in new_ids:
            raise ValueError(f"Duplicate request ID: {record['request_id']}")

        new_ids.add(request_id)

    all_additional = load_additional_requests()
    all_additional.extend(validated)

    ADDITIONAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(ADDITIONAL_PATH, "w", encoding="utf-8") as file:
        json.dump(all_additional, file, indent=4, ensure_ascii=False)

    return len(validated)


def read_uploaded_excel(file):
    df = pd.read_excel(file)

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "The Excel file is missing these columns: "
            + ", ".join(missing)
        )

    return validate_records(
        df[REQUIRED_COLUMNS].fillna("").to_dict(orient="records")
    )
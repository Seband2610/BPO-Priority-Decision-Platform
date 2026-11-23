import json
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "data" / "BPO_Decision_Platform_Dataset.xlsx"
ADDITIONAL_PATH = BASE_DIR / "data" / "additional_requests.json"
CHANGES_PATH = BASE_DIR / "data" / "request_changes.json"

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


def load_request_changes():
    """Load non-destructive edits and deletion markers."""
    if not CHANGES_PATH.exists():
        return {"updates": {}, "deleted": []}

    with open(CHANGES_PATH, "r", encoding="utf-8") as file:
        changes = json.load(file)

    return {
        "updates": changes.get("updates", {}),
        "deleted": [
            str(request_id).strip().lower()
            for request_id in changes.get("deleted", [])
        ]
    }


def save_request_changes(changes):
    CHANGES_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = CHANGES_PATH.with_suffix(".tmp")
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(changes, file, indent=4, ensure_ascii=False)

    temporary_path.replace(CHANGES_PATH)


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

    changes = load_request_changes()
    updates = {
        str(request_id).strip().lower(): record
        for request_id, record in changes["updates"].items()
    }
    deleted_ids = set(changes["deleted"])

    visible_records = []
    seen_ids = set()

    for record in all_records:
        request_id = record["request_id"].strip().lower()

        if request_id in deleted_ids:
            continue

        if request_id in updates:
            record = updates[request_id]

        normalized_id = record["request_id"].strip().lower()
        if normalized_id in seen_ids:
            raise ValueError(
                f"Duplicate request ID found: {record['request_id']}"
            )

        seen_ids.add(normalized_id)
        visible_records.append(record)

    return visible_records


def save_additional_requests(new_records):
    existing = load_requests()
    existing_ids = {
        record["request_id"].strip().lower()
        for record in existing
    }

    validated = validate_records(new_records)
    new_ids = set()

    changes = load_request_changes()
    deleted_ids = set(changes["deleted"])

    for record in validated:
        request_id = record["request_id"].strip().lower()

        if request_id in existing_ids or request_id in new_ids:
            raise ValueError(f"Duplicate request ID: {record['request_id']}")

        if request_id in deleted_ids:
            raise ValueError(
                f"This request ID was previously deleted and cannot be reused: "
                f"{record['request_id']}."
            )

        new_ids.add(request_id)

    all_additional = load_additional_requests()
    all_additional.extend(validated)

    ADDITIONAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = ADDITIONAL_PATH.with_suffix(".tmp")
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(all_additional, file, indent=4, ensure_ascii=False)

    temporary_path.replace(ADDITIONAL_PATH)

    return len(validated)


def update_existing_request(request_id, updated_record):
    """Save an edit as an overlay; the original Excel remains untouched."""
    normalized_id = str(request_id).strip().lower()
    current_records = load_requests()

    existing = next(
        (
            record for record in current_records
            if record["request_id"].strip().lower() == normalized_id
        ),
        None
    )

    if existing is None:
        raise ValueError(f"Request not found: {request_id}")

    updated_record = dict(updated_record)
    updated_record["request_id"] = existing["request_id"]
    validated = validate_records([updated_record])[0]

    changes = load_request_changes()
    changes["updates"][normalized_id] = validated

    # If an old deletion marker exists, remove it when updating a visible record.
    changes["deleted"] = [
        item for item in changes["deleted"] if item != normalized_id
    ]

    save_request_changes(changes)
    return validated


def delete_existing_request(request_id):
    """Hide a request from the platform without deleting its source row."""
    normalized_id = str(request_id).strip().lower()
    current_records = load_requests()

    exists = any(
        record["request_id"].strip().lower() == normalized_id
        for record in current_records
    )

    if not exists:
        raise ValueError(f"Request not found: {request_id}")

    changes = load_request_changes()

    if normalized_id not in changes["deleted"]:
        changes["deleted"].append(normalized_id)

    changes["updates"].pop(normalized_id, None)
    save_request_changes(changes)


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

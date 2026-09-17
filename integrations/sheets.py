import os
from datetime import datetime

from dotenv import load_dotenv

try:
    from composio import Composio
except Exception:  # pragma: no cover - optional dependency handling
    Composio = None

load_dotenv()


def build_sheet_row(mark, status="Current"):
    """Create the row shape used for the Google Sheet."""
    return [
        datetime.now().strftime("%d-%m-%Y"),
        str(mark.get("exam_code", "")).strip(),
        str(mark.get("subject", "")).strip(),
        str(mark.get("event", "")).strip(),
        str(mark.get("obtained_marks", "")).strip(),
        str(mark.get("full_marks", "")).strip(),
        status,
    ]


def find_matching_row_index(rows, exam_code, subject, event):
    """Return the matching row index for exam_code + subject + event, or None."""
    if not isinstance(rows, list):
        return None

    for index, row in enumerate(rows):
        if len(row) < 7:
            continue

        if (
            str(row[1]).strip() == str(exam_code).strip()
            and str(row[2]).strip() == str(subject).strip()
            and str(row[3]).strip() == str(event).strip()
        ):
            return index

    return None


def _mark_key(mark):
    return (
        str(mark.get("exam_code", "")).strip(),
        str(mark.get("subject", "")).strip(),
        str(mark.get("event", "")).strip(),
    )


def _get_session():
    """Create a small Composio session scoped to Google Sheets."""
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        print("COMPOSIO_API_KEY not set. Skipping Google Sheets sync.")
        return None

    if Composio is None:
        print("Composio SDK is unavailable. Skipping Google Sheets sync.")
        return None

    try:
        composio = Composio(api_key=api_key)
        return composio.create(
            user_id=os.getenv("COMPOSIO_USER_ID", "webkiosk-marks-agent"),
            toolkits=["googlesheets"],
        )
    except Exception as exc:  # pragma: no cover - runtime dependency
        print(f"Unable to initialize Composio Google Sheets session: {exc}")
        return None


def _read_sheet_rows(session, spreadsheet_id):
    """Read the current sheet rows with the current Google Sheets value-get tool."""
    if session is None:
        return []

    try:
        response = session.execute(
            "GOOGLESHEETS_VALUES_GET",
            arguments={
                "spreadsheet_id": spreadsheet_id,
                "range": "Sheet1!A:Z",
            },
        )
        data = getattr(response, "data", {}) or {}
        if isinstance(data, dict):
            values = data.get("values")
            if values is not None:
                return values
        if isinstance(data, list):
            return data
    except Exception as exc:  # pragma: no cover - runtime dependency
        print(f"Google Sheets read failed: {exc}")

    return []


def _write_sheet_rows(session, spreadsheet_id, rows):
    """Write the sheet values using the current Google Sheets update tool."""
    if session is None:
        return False

    if not rows:
        return False

    try:
        end_row = len(rows)

        response = session.execute(
            "GOOGLESHEETS_VALUES_UPDATE",
            arguments={
                "spreadsheet_id": spreadsheet_id,
                "range": f"Sheet1!A1:G{end_row}",
                "values": rows,
                "value_input_option": "USER_ENTERED",
            },
        )

        error = getattr(response, "error", None)

        if error:
            print(f"Google Sheets write returned error: {error}")
            return False

        print(f"Google Sheets sync successful: {len(rows) - 1} mark rows written.")
        return True

    except Exception as exc:
        print(f"Google Sheets write failed: {exc}")
        return False


def sync_marks_to_sheet(marks, changes=None, spreadsheet_id=None):
    """Sync the current marks snapshot to Google Sheets without crashing the flow."""
    spreadsheet_id = spreadsheet_id or os.getenv("COMPOSIO_GOOGLE_SHEETS_SPREADSHEET_ID")

    if not spreadsheet_id:
        print("COMPOSIO_GOOGLE_SHEETS_SPREADSHEET_ID not set. Skipping Google Sheets sync.")
        return False

    session = _get_session()
    if session is None:
        return False

    existing_rows = _read_sheet_rows(session, spreadsheet_id)
    if not existing_rows:
        existing_rows = []

    if not any(str(row[0]).strip().lower() == "date" for row in existing_rows if row):
        existing_rows.insert(
            0,
            ["Date", "Exam Code", "Subject", "Exam/Event", "Marks", "Full Marks", "Status"],
        )

    updated_rows = [row for row in existing_rows]

    if changes is None:
        changes = {"new": [], "updated": []}

    new_keys = {_mark_key(mark) for mark in changes.get("new", [])}
    updated_keys = {_mark_key(change["new"]) for change in changes.get("updated", [])}

    for mark in marks:
        status = "Current"
        key = _mark_key(mark)
        if key in new_keys:
            status = "New"
        elif key in updated_keys:
            status = "Updated"

        row = build_sheet_row(mark, status)
        match_index = find_matching_row_index(
            updated_rows,
            mark.get("exam_code", ""),
            mark.get("subject", ""),
            mark.get("event", ""),
        )

        if match_index is None:
            updated_rows.append(row)
        else:
            updated_rows[match_index] = row

    result = _write_sheet_rows(session, spreadsheet_id, updated_rows)
    return result

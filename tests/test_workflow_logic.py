from datetime import datetime

from integrations.gmail import build_email_content
from integrations.sheets import build_sheet_row, find_matching_row_index


def test_build_sheet_row_uses_expected_columns():
    row = build_sheet_row(
        mark={
            "exam_code": "2526ODDSEM",
            "subject": "Machine Learning(UML501)",
            "event": "MST",
            "obtained_marks": "29.5",
            "full_marks": "30",
            "status": "Updated",
        },
        status="Updated",
    )

    assert row == [
        datetime.now().strftime("%d-%m-%Y"),
        "2526ODDSEM",
        "Machine Learning(UML501)",
        "MST",
        "29.5",
        "30",
        "Updated",
    ]


def test_find_matching_row_index_matches_exam_code_subject_and_event():
    rows = [
        ["17-09-2026", "2526ODDSEM", "Machine Learning(UML501)", "MST", "25", "30", "Updated"],
        ["17-09-2026", "2526ODDSEM", "Computer Networks(UCS520)", "ENDSEM", "39", "60", "Current"],
    ]

    assert find_matching_row_index(rows, "2526ODDSEM", "Machine Learning(UML501)", "MST") == 0
    assert find_matching_row_index(rows, "2526ODDSEM", "Image Processing(UCS615)", "MST") is None


def test_build_email_content_contains_previous_and_current_values():
    content = build_email_content(
        mark={
            "subject": "Machine Learning",
            "event": "MST",
            "obtained_marks": "29.5",
            "full_marks": "30",
        },
        previous={"obtained_marks": "25"},
        current={"obtained_marks": "29.5"},
    )

    assert content["subject"] == "WebKiosk Marks Update — Machine Learning MST"
    assert "Machine Learning" in content["body"]
    assert "Previous: 25" in content["body"]
    assert "Current: 29.5" in content["body"]

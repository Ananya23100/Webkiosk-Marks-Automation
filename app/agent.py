from app.detector import detect_changes, print_changes
from app.notifier import send_new_mark_notification, send_updated_mark_notification
from integrations.gmail import send_mark_email_notification
from integrations.sheets import sync_marks_to_sheet


def process_marks_update(marks, old_marks=None, changes=None):
    """Coordinate the marks workflow: detect change, notify, sync sheet, save snapshot."""
    if changes is None:
        changes = detect_changes(old_marks, marks)

    print_changes(changes)

    try:
        synced = sync_marks_to_sheet(marks, changes=changes)

        if not synced:
            print("Google Sheets sync failed.")
    except Exception as exc:
        print(f"Google Sheets sync failed: {exc}")

    if changes.get("new"):
        for mark in changes["new"]:
            try:
                send_mark_email_notification(mark, previous=None, current=mark)
            except Exception as exc:
                print(f"Gmail notification failed for new mark: {exc}")

            try:
                send_new_mark_notification(mark)
            except Exception as exc:
                print(f"WhatsApp new-mark notification failed: {exc}")

    if changes.get("updated"):
        for change in changes["updated"]:
            old_mark = change["old"]
            new_mark = change["new"]

            try:
                send_mark_email_notification(new_mark, previous=old_mark, current=new_mark)
            except Exception as exc:
                print(f"Gmail notification failed for updated mark: {exc}")

            try:
                send_updated_mark_notification(change)
            except Exception as exc:
                print(f"WhatsApp updated-mark notification failed: {exc}")

    return changes

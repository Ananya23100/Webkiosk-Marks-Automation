def create_mark_key(mark):
    """
    Creates a unique identifier for a mark.

    The same subject can have multiple events,
    such as MST, ENDSEM, SES#QZ1, etc.

    Therefore we use:
        Exam Code + Subject + Event
    """

    return (
        mark["exam_code"],
        mark["subject"],
        mark["event"]
    )


def detect_changes(
    old_marks,
    new_marks
):
    """
    Compare old marks with new marks.

    Returns a dictionary containing:
        - new marks
        - updated marks
    """

    changes = {
        "new": [],
        "updated": []
    }

    # If there is no previous snapshot,
    # everything is considered the initial state.
    if old_marks is None:

        changes["new"] = new_marks

        return changes

    # Convert old marks into a dictionary
    old_lookup = {}

    for mark in old_marks:

        key = create_mark_key(mark)

        old_lookup[key] = mark

    # Compare new marks
    for new_mark in new_marks:

        key = create_mark_key(
            new_mark
        )

        # Completely new record
        if key not in old_lookup:

            changes["new"].append(
                new_mark
            )

        else:

            old_mark = old_lookup[key]

            # Check whether the actual mark changed
            if (
                old_mark["obtained_marks"]
                != new_mark["obtained_marks"]
                or
                old_mark["effective_marks"]
                != new_mark["effective_marks"]
                or
                old_mark["status"]
                != new_mark["status"]
            ):

                changes["updated"].append(
                    {
                        "old": old_mark,
                        "new": new_mark
                    }
                )

    return changes


def print_changes(changes):
    """
    Print detected changes in a readable format.
    """

    new_marks = changes["new"]
    updated_marks = changes["updated"]

    if (
        len(new_marks) == 0
        and
        len(updated_marks) == 0
    ):

        print(
            "\nNo changes detected."
        )

        return

    print(
        "\n========== CHANGES DETECTED =========="
    )

    # -----------------------------------------
    # NEW MARKS
    # -----------------------------------------

    if len(new_marks) > 0:

        print(
            f"\nNew marks: {len(new_marks)}"
        )

        for mark in new_marks:

            print(
                f"\nNEW MARK"
            )

            print(
                "Subject:",
                mark["subject"]
            )

            print(
                "Event:",
                mark["event"]
            )

            print(
                "Obtained:",
                mark["obtained_marks"],
                "/",
                mark["full_marks"]
            )

    # -----------------------------------------
    # UPDATED MARKS
    # -----------------------------------------

    if len(updated_marks) > 0:

        print(
            f"\nUpdated marks: {len(updated_marks)}"
        )

        for change in updated_marks:

            old = change["old"]
            new = change["new"]

            print(
                f"\nMARK UPDATED"
            )

            print(
                "Subject:",
                new["subject"]
            )

            print(
                "Event:",
                new["event"]
            )

            print(
                "Previous:",
                old["obtained_marks"]
            )

            print(
                "Current:",
                new["obtained_marks"]
            )
def create_notification_message(changes):

    new_marks = changes["new"]
    updated_marks = changes["updated"]

    lines = []

    lines.append(
        "🔔 *WebKiosk Marks Update*"
    )

    # -----------------------------------------
    # NEW MARKS
    # -----------------------------------------

    if len(new_marks) > 0:

        lines.append(
            f"\n*New marks: {len(new_marks)}*"
        )

        for mark in new_marks:

            lines.append(
                f"• {mark['subject']} | "
                f"{mark['event']} | "
                f"{mark['obtained_marks']}/"
                f"{mark['full_marks']}"
            )

    # -----------------------------------------
    # UPDATED MARKS
    # -----------------------------------------

    if len(updated_marks) > 0:

        lines.append(
            f"\n*Updated marks: "
            f"{len(updated_marks)}*"
        )

        for change in updated_marks:

            old = change["old"]
            new = change["new"]

            lines.append(
                f"• {new['subject']} | "
                f"{new['event']} | "
                f"{old['obtained_marks']} → "
                f"{new['obtained_marks']}"
            )

    return "\n".join(lines)
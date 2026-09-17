import json
import os


SNAPSHOT_FILE = "data/marks.json"


def save_marks(marks):
    """
    Save the current marks snapshot to JSON.
    """

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        SNAPSHOT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            marks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Snapshot saved to {SNAPSHOT_FILE}"
    )


def load_marks():
    """
    Load the previous marks snapshot.

    Returns:
        list: Previous marks
        None: If no snapshot exists
    """

    if not os.path.exists(
        SNAPSHOT_FILE
    ):
        return None

    with open(
        SNAPSHOT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)
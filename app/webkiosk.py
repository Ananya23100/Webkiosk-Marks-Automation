import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from app.storage import save_marks, load_marks
from app.detector import detect_changes
from app.agent import process_marks_update
# -----------------------------------------
# LOAD CREDENTIALS
# -----------------------------------------

load_dotenv()

USERNAME = os.getenv(
    "WEBKIOSK_USERNAME"
)

PASSWORD = os.getenv(
    "WEBKIOSK_PASSWORD"
)

URL = "https://webkiosk.thapar.edu/"


def get_marks_page():

    with sync_playwright() as p:

        # -----------------------------------------
        # 1. START BROWSER
        # -----------------------------------------

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        # -----------------------------------------
        # 2. OPEN WEBKIOSK
        # -----------------------------------------

        print(
            "Opening WebKiosk..."
        )

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # -----------------------------------------
        # 3. LOGIN
        # -----------------------------------------

        print(
            "Logging in..."
        )

        page.locator(
            'input:not([readonly])'
        ).nth(0).fill(
            USERNAME
        )

        page.locator(
            'input[type="password"]'
        ).fill(
            PASSWORD
        )

        page.get_by_role(
            "button",
            name="Submit"
        ).click()

        page.wait_for_timeout(
            4000
        )

        print(
            "Login successful."
        )

        # -----------------------------------------
        # 4. FIND LEFT NAVIGATION FRAME
        # -----------------------------------------

        left_frame = None

        for frame in page.frames:

            if "FrameLeftStudent.jsp" in frame.url:

                left_frame = frame
                break

        if left_frame is None:

            raise Exception(
                "Could not find left navigation frame."
            )

        print(
            "Left navigation frame found."
        )

        # -----------------------------------------
        # 5. OPEN EXAM INFO
        # -----------------------------------------

        print(
            "Opening Exam Info..."
        )

        left_frame.get_by_text(
            "Exam. Info.",
            exact=True
        ).click()

        page.wait_for_timeout(
            1000
        )

        # -----------------------------------------
        # 6. OPEN EXAM MARKS
        # -----------------------------------------

        print(
            "Opening Exam Marks..."
        )

        left_frame.get_by_text(
            "Exam Marks",
            exact=True
        ).click()

        page.wait_for_timeout(
            3000
        )

        # -----------------------------------------
        # 7. FIND MARKS FRAME
        # -----------------------------------------

        marks_frame = page.frame(
            name="DetailSection"
        )

        if marks_frame is None:

            raise Exception(
                "Could not find marks frame."
            )

        print(
            "Marks frame found."
        )

        # -----------------------------------------
        # 8. FIND DROPDOWN
        # -----------------------------------------

        selects = marks_frame.locator(
            "select"
        )

        print(
            "Number of dropdowns:",
            selects.count()
        )

        # -----------------------------------------
        # 9. SELECT EXAM
        # -----------------------------------------

        print(
            "Selecting 2526ODDSEM..."
        )

        exam_select = selects.nth(0)

        exam_select.select_option(
            "2526ODDSEM"
        )

        print(
            "Exam code selected."
        )

        # -----------------------------------------
        # 10. CLICK SHOW
        # -----------------------------------------

        show_button = marks_frame.locator(
            'input[value="Show"]'
        )

        if show_button.count() == 0:

            raise Exception(
                "Could not find Show button."
            )

        print(
            "Clicking Show..."
        )

        show_button.click()

        page.wait_for_timeout(
            3000
        )

        print(
            "Marks loaded!"
        )

        # -----------------------------------------
        # 11. PARSE MARKS
        # -----------------------------------------

        print(
            "\n========== PARSING MARKS =========="
        )

        marks_table = marks_frame.locator(
            "table"
        ).nth(2)

        rows = marks_table.locator(
            "tr"
        )

        marks = []

        # Skip header row
        for i in range(
            1,
            rows.count()
        ):

            cells = rows.nth(i).locator(
                "td, th"
            )

            if cells.count() < 9:

                continue

            mark = {
                "sr_no":
                    cells.nth(0).inner_text().strip(),

                "exam_code":
                    cells.nth(1).inner_text().strip(),

                "subject":
                    cells.nth(2).inner_text().strip(),

                "event":
                    cells.nth(3).inner_text().strip(),

                "full_marks":
                    cells.nth(4).inner_text().strip(),

                "obtained_marks":
                    cells.nth(5).inner_text().strip(),

                "weightage":
                    cells.nth(6).inner_text().strip(),

                "effective_marks":
                    cells.nth(7).inner_text().strip(),

                "status":
                    cells.nth(8).inner_text().strip()
            }

            marks.append(
                mark
            )

        print(
            "Marks parsed:",
            len(marks)
        )

        # -----------------------------------------
        # 12. LOAD PREVIOUS SNAPSHOT
        # -----------------------------------------

        print(
            "\nLoading previous snapshot..."
        )

        old_marks = load_marks()

        if old_marks is None:

            print(
                "No previous snapshot found."
            )

        else:

            print(
                "Previous snapshot loaded:",
                len(old_marks),
                "records"
            )

        # -----------------------------------------
        # 13. DETECT CHANGES
        # -----------------------------------------

        changes = detect_changes(
            old_marks,
            marks
        )

        process_marks_update(
            marks,
            old_marks,
            changes
        )

        # -----------------------------------------
        # 15. SAVE CURRENT SNAPSHOT
        # -----------------------------------------

        save_marks(
            marks
        )

        # -----------------------------------------
        # 16. SCREENSHOT
        # -----------------------------------------

        page.screenshot(
            path="marks_page.png",
            full_page=True
        )

        print(
            "\nScreenshot saved as marks_page.png"
        )

        # -----------------------------------------
        # 17. KEEP BROWSER OPEN
        # -----------------------------------------


        browser.close()


if __name__ == "__main__":

    get_marks_page()
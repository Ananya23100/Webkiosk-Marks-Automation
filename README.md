# WebKiosk Marks Automation

This project automates the WebKiosk marks flow for a single exam cycle. It logs in, reads the marks table, compares it with the last saved snapshot, and flags new or updated marks before sending the relevant notifications.

## Workflow

1. Launch the WebKiosk browser flow.
2. Fetch the exam marks for the configured semester.
3. Compare the latest values with the previous snapshot in data/marks.json.
4. Detect new and updated marks.
5. Sync the latest snapshot to Google Sheets through Composio.
6. Send Gmail notifications through Composio for new or updated marks.
7. Continue the existing Twilio WhatsApp notification flow.
8. Save the newest snapshot for the next run.

## Why Composio is used

Composio is used as the cross-application automation layer for Google Sheets and Gmail. This keeps the WebKiosk scraping logic deterministic while showing how a real operational workflow can route data across external tools without building a large automation framework.

## Google Sheets

The project writes the latest marks into a simple spreadsheet with columns such as Date, Subject, Exam/Event, Marks, Full Marks, and Status. If a subject/event row already exists, it is updated instead of creating duplicates.

## Gmail

When a mark is new or changed, the workflow sends a short Gmail notification summarizing the previous and current values. This runs alongside the WhatsApp alert and does not block the rest of the process if a notification fails.

## Twilio

The existing Twilio WhatsApp notification remains part of the workflow and is kept intact so the project still alerts the user in the same way it did before the Composio additions.

## Cross-application operations demo

This project demonstrates a small operations automation pattern: WebKiosk data is detected, compared, written to a spreadsheet, emailed, and pushed to WhatsApp. That is the core of a practical Composio-style workflow for Product Operations / AI automation use cases.

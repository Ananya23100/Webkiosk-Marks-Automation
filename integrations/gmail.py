import os

from dotenv import load_dotenv

try:
    from composio import Composio
except Exception:  # pragma: no cover - optional dependency handling
    Composio = None

load_dotenv()


def build_email_content(mark, previous=None, current=None):
    """Build the minimal email payload for a new or updated mark."""
    subject_name = str(mark.get("subject", "")).strip()
    event_name = str(mark.get("event", "")).strip()
    current_value = str((current or mark).get("obtained_marks", "")).strip()

    subject = f"WebKiosk Marks Update — {subject_name} {event_name}".strip()

    lines = [
        str(mark.get("subject", "")).strip(),
        f"Event: {event_name}",
    ]

    previous_value = str((previous or {}).get("obtained_marks", "")).strip()
    if previous_value:
        lines.append(f"Previous: {previous_value}")

    lines.append(f"Current: {current_value}")

    return {
        "subject": subject,
        "body": "\n".join(lines),
    }


def _get_session():
    """Create a Composio session scoped to Gmail."""
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        print("COMPOSIO_API_KEY not set. Skipping Gmail notification.")
        return None

    if Composio is None:
        print("Composio SDK is unavailable. Skipping Gmail notification.")
        return None

    try:
        composio = Composio(api_key=api_key)
        return composio.create(
            user_id=os.getenv("COMPOSIO_USER_ID", "webkiosk-marks-agent"),
            toolkits=["gmail"],
        )
    except Exception as exc:  # pragma: no cover - runtime dependency
        print(f"Unable to initialize Composio Gmail session: {exc}")
        return None


def send_mark_email_notification(mark, previous=None, current=None, recipient=None):
    """Send a Gmail notification for a new or updated mark."""
    recipient_email = recipient or os.getenv("COMPOSIO_GMAIL_TO") or os.getenv("GMAIL_TO")
    if not recipient_email:
        print("COMPOSIO_GMAIL_TO / GMAIL_TO is not set. Skipping Gmail notification.")
        return False

    session = _get_session()
    if session is None:
        return False

    payload = build_email_content(mark, previous=previous, current=current or mark)

    try:
        response = session.execute(
        "GMAIL_SEND_EMAIL",
        arguments={
            "recipient_email": recipient_email,
            "subject": payload["subject"],
            "body": payload["body"],
        },
)
        if getattr(response, "error", None):
            print(f"Gmail execution returned error: {response.error}")
            return False

        print(f"Gmail notification sent for {payload['subject']}")
        return True
    except Exception as exc:  # pragma: no cover - runtime dependency
        print(f"Gmail execution failed: {exc}")

    return False

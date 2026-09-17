import os
import json

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")

NEW_TEMPLATE_SID = os.getenv("TWILIO_NEW_TEMPLATE_SID")
UPDATED_TEMPLATE_SID = os.getenv("TWILIO_UPDATED_TEMPLATE_SID")


def send_whatsapp_message(
    template_sid,
    variables
):
    client = Client(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )

    response = client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=TWILIO_WHATSAPP_TO,
        content_sid=template_sid,
        content_variables=json.dumps(variables)
    )

    print("WhatsApp notification sent.")
    print("Message SID:", response.sid)

    return True


def send_new_mark_notification(mark):
    variables = {
        "1": mark["subject"],
        "2": mark["event"],
        "3": mark["obtained_marks"],
        "4": mark["full_marks"]
    }

    return send_whatsapp_message(
        NEW_TEMPLATE_SID,
        variables
    )


def send_updated_mark_notification(change):
    old_mark = change["old"]
    new_mark = change["new"]

    variables = {
        "1": new_mark["subject"],
        "2": new_mark["event"],
        "3": old_mark["obtained_marks"],
        "4": new_mark["obtained_marks"]
    }

    return send_whatsapp_message(
        UPDATED_TEMPLATE_SID,
        variables
    )
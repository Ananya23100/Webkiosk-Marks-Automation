import os
import json
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
whatsapp_to = os.getenv("TWILIO_WHATSAPP_TO")

client = Client(account_sid, auth_token)

message = client.messages.create(
    from_=whatsapp_from,
    to=whatsapp_to,
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables=json.dumps({
        "1": "17 September 2026",
        "2": "10:00 PM"
    })
)

print("Message sent!")
print("Message SID:", message.sid)
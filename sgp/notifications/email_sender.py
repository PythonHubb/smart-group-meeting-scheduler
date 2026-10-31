
import base64
from pathlib import Path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=credentials)


def send_email(receiver_email, subject, message):
    try:
        service = get_gmail_service()

        email = EmailMessage()
        email["To"] = receiver_email
        email["Subject"] = subject
        email.set_content(message)

        encoded_message = base64.urlsafe_b64encode(
            email.as_bytes()
        ).decode("utf-8")

        service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()

        print(f"Email sent successfully to {receiver_email}!")
        return True

    except (HttpError, OSError, ValueError) as error:
        print(f"Failed to send email: {error}")
        return False

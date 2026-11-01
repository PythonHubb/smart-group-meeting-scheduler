
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = BASE_DIR / "credentials.json"

TOKEN_DIR = Path.home() / ".smart_group_meeting_scheduler"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.freebusy"
]


def get_calendar_credentials():
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)

    token_file = TOKEN_DIR / "calendar_freebusy_token.json"

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_file), SCOPES
        )

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception:
            credentials = None

    if not credentials or not credentials.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "credentials.json was not found in the project folder."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SCOPES
        )

        print("\nOpening browser for Google Calendar authorization...")

        credentials = flow.run_local_server(port=0)

    token_file.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )

    print("Google Calendar connected successfully!")

    return credentials


from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "calendar_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]


def get_calendar_service():
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

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    return build("calendar", "v3", credentials=credentials)


def create_calendar_event(
    title,
    meeting_date,
    start_hour,
    end_hour,
    timezone="UTC"
):
    try:
        service = get_calendar_service()

        start = datetime.strptime(
            meeting_date, "%Y-%m-%d"
        ).replace(hour=start_hour)

        end = start + timedelta(
            hours=end_hour - start_hour
        )

        event = {
            "summary": title,
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": timezone
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": timezone
            }
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        print("Meeting added to Google Calendar!")
        print("Event link:", created_event.get("htmlLink"))

        return created_event

    except (HttpError, OSError, ValueError) as error:
        print(f"Google Calendar error: {error}")
        return None

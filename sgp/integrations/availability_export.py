
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sgp.integrations.calendar_auth import get_calendar_credentials
from sgp.integrations.calendar_availability import get_free_times


EXPORT_DIR = Path("data") / "availability_exports"


def export_availability(
    username,
    meeting_date,
    start_hour=9,
    end_hour=17,
    timezone="Europe/Istanbul",
):
    if not username or not username.strip():
        raise ValueError("Username cannot be empty.")

    if not 0 <= start_hour < end_hour <= 24:
        raise ValueError("Invalid time range.")

    # Validate the date and timezone.
    datetime.strptime(meeting_date, "%Y-%m-%d")
    ZoneInfo(timezone)

    # Connect to the member's own Google account.
    credentials = get_calendar_credentials()

    # Read free time directly from Google Calendar.
    free_times = get_free_times(
        credentials,
        meeting_date,
        start_hour,
        end_hour,
        timezone,
    )

    # Save only free intervals, not calendar events or tokens.
    data = {
        "username": username.strip(),
        "date": meeting_date,
        "timezone": timezone,
        "free_slots": [
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
            for start, end in free_times
        ],
    }

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    safe_username = "".join(
        char for char in username
        if char.isalnum() or char in "-_"
    )

    if not safe_username:
        raise ValueError("Invalid username.")

    filename = f"{safe_username}_{meeting_date}.json"
    file_path = EXPORT_DIR / filename

    file_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )

    print(f"Availability exported successfully: {file_path}")

    return file_path

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build


def get_busy_times(credentials, start_time, end_time, timezone):
    service = build("calendar", "v3", credentials=credentials)

    response = service.freebusy().query(
        body={
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "timeZone": timezone,
            "items": [{"id": "primary"}],
        }
    ).execute()

    calendar = response["calendars"]["primary"]

    if calendar.get("errors"):
        raise RuntimeError(
            f"Cannot read calendar availability: {calendar['errors']}"
        )

    return [
        (
            datetime.fromisoformat(item["start"].replace("Z", "+00:00")),
            datetime.fromisoformat(item["end"].replace("Z", "+00:00")),
        )
        for item in calendar.get("busy", [])
    ]


def get_free_times(credentials, meeting_date, start_hour, end_hour, timezone):
    if not (
        isinstance(start_hour, int)
        and not isinstance(start_hour, bool)
        and isinstance(end_hour, int)
        and not isinstance(end_hour, bool)
        and 0 <= start_hour < end_hour <= 24
    ):
        raise ValueError("Invalid time range.")

    tz = ZoneInfo(timezone)
    day = datetime.strptime(meeting_date, "%Y-%m-%d").date()

    start_time = datetime(
        day.year, day.month, day.day, start_hour, tzinfo=tz
    )

    if end_hour == 24:
        end_time = datetime.combine(
            day + timedelta(days=1), datetime.min.time(), tzinfo=tz
        )
    else:
        end_time = datetime(
            day.year, day.month, day.day, end_hour, tzinfo=tz
        )

    busy_times = get_busy_times(credentials, start_time, end_time, timezone)

    free_times = []
    current = start_time

    for busy_start, busy_end in sorted(busy_times):
        busy_start = max(busy_start.astimezone(tz), start_time)
        busy_end = min(busy_end.astimezone(tz), end_time)

        if busy_start > current:
            free_times.append((current, busy_start))

        current = max(current, busy_end)

    if current < end_time:
        free_times.append((current, end_time))

    return free_times

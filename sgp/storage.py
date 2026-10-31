
import json
from pathlib import Path
from dataclasses import asdict

from sgp.models import Group, Member


def save_group(group, filename):
    data = asdict(group)

    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_group(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    last_meeting = data.get("last_notified_meeting")

    if last_meeting is not None:
        last_meeting = (
            last_meeting[0],
            tuple(last_meeting[1])
        )

    group = Group(
        id=data["id"],
        name=data["name"],
        last_notified_meeting=last_meeting
    )

    used_usernames = set()

    for member_data in data.get("members", []):
        member_id = member_data["id"]

        username = member_data.get("username")

        if not username:
            username = f"user_{member_id}"

        username = username.strip()

        base_username = username
        counter = 2

        while username.casefold() in used_usernames:
            username = f"{base_username}_{counter}"
            counter += 1

        used_usernames.add(username.casefold())

        member = Member(
            id=member_id,
            name=member_data["name"],
            username=username,
            availability_completed=member_data.get(
                "availability_completed", False
            ),
            notification_preferences=member_data.get(
                "notification_preferences", []
            ),
            contact_info=member_data.get(
                "contact_info", {}
            )
        )

        member.availability = {
            day: [tuple(time) for time in times]
            for day, times in member_data.get(
                "availability", {}
            ).items()
        }

        group.members.append(member)

    return group

from datetime import date, datetime, timedelta, timezone

import json

from pathlib import Path

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sgp.integrations.google_calendar import create_calendar_event, get_calendar_service
from sgp.integrations.availability_export import export_availability

from sgp.models import Member, Group

from sgp.scheduler import (

    suggest_meeting_time, merge_intervals, find_best_weekly_meeting,

    find_best_calendar_meeting,

)

from sgp.storage import save_group, load_group

from sgp.notifications.simulated import notify_group

from sgp.notifications.telegram_verification import generate_connection_code, verify_telegram_code

from sgp.validators import is_valid_name, is_valid_email, is_valid_day

class CancelOperation(Exception):

    pass

class BackOperation(Exception):

    pass

def ask(prompt):

    value = input(prompt).strip()

    if value == "0":

        raise CancelOperation

    if value.lower() == "b":

        raise BackOperation

    return value

def show_menu():

    print("\n===== Smart Group Project =====")

    print("1. Create Group")

    print("2. Add Member")

    print("3. Manage Availability")

    print("4. Suggest Meeting Time")

    print("5. Save Group")

    print("6. Load Group")

    print("7. Find Meeting from Google Calendar Files")
    print("8. Export My Google Calendar Availability")

    print("0. Exit")

def ask_name():

    while True:

        name = ask("Enter member name (0=Cancel): ")

        if is_valid_name(name):

            return name

        print("Invalid name! Only English letters and spaces, max 20 characters.")

def ask_username(group):

    while True:

        username = ask("Enter username (b=Back, 0=Cancel): ")

        if not username:

            print("Username cannot be empty!")

        elif any(m.username.casefold() == username.casefold() for m in group.members):

            print("This username is already taken!")

        else:

            return username

def choose_notification_platforms():

    choices = {"1": "email", "2": "telegram", "3": "whatsapp", "4": "sms"}

    while True:

        print("\nNotification platforms: 1.Email  2.Telegram  3.WhatsApp  4.SMS")

        raw = ask("Choose (e.g. 1,2; b=Back, 0=Cancel): ")

        numbers = raw.replace(" ", "").split(",")

        if numbers and all(n in choices for n in numbers):

            return list(dict.fromkeys(choices[n] for n in numbers))

        print("Invalid choice!")

def connect_telegram(username):

    print("\nOpen https://t.me/smart_group_meeting_bot and press Start.")

    while True:

        code = generate_connection_code()

        print(f"Connection code: {code}")

        print("Send the code to the bot. Verification may wait up to 5 minutes.")

        chat_id = verify_telegram_code(code, username)

        if chat_id == "__cancel__":

            raise CancelOperation

        if chat_id == "__back__":

            raise BackOperation

        if chat_id:

            print("Telegram connected successfully!")

            return chat_id

        print("Telegram verification failed.")

        response = ask("1=Retry, b=Back, 0=Cancel, Enter=Skip: ")

        if response != "1":

            return None

def get_contact_info(platforms):

    contact_info = {}

    active = []

    index = 0

    while index < len(platforms):

        platform = platforms[index]

        try:

            if platform == "email":

                value = ask("Email (b=Back, 0=Cancel): ")

                if not is_valid_email(value):

                    print("Invalid email! Example: name@example.com")

                    continue

                contact_info["email"] = value

                active.append(platform)

            elif platform == "telegram":

                username = ask("Telegram username (b=Back, 0=Cancel; Enter=Skip): ").lstrip("@")

                if username:

                    try:

                        chat_id = connect_telegram(username)

                    except BackOperation:

                        print("Back to Telegram username...")

                        continue

                    if chat_id:

                        contact_info["telegram_username"] = username

                        contact_info["telegram"] = chat_id

                        active.append(platform)

                    else:

                        print("Telegram notifications skipped.")

            else:

                value = ask(f"{platform.title()} phone (b=Back, 0=Cancel; Enter=Skip): ")

                if value:

                    contact_info[platform] = value

                    active.append(platform)

            index += 1

        except BackOperation:

            if index == 0:

                raise

            index -= 1

            previous = platforms[index]

            if previous in active:

                active.remove(previous)

            contact_info.pop(previous, None)

            if previous == "telegram":

                contact_info.pop("telegram_username", None)

            print("Returning to previous contact field...")

    return contact_info, active

def add_member_flow(group):

    stages = ["name", "username", "platforms", "contacts", "confirm"]

    stage = 0

    name = username = None

    platforms = []

    contacts, active = {}, []

    while True:

        try:

            current = stages[stage]

            if current == "name":

                name = ask_name()

            elif current == "username":

                username = ask_username(group)

            elif current == "platforms":

                platforms = choose_notification_platforms()

            elif current == "contacts":

                contacts, active = get_contact_info(platforms)

            else:

                print(f"\nReview: {name} (@{username})")

                print("Active notifications:", ", ".join(active) or "None")

                print("Contact info:", contacts)

                answer = ask("Save member? (y/n, b=Back, 0=Cancel): ").lower()

                if answer == "y":

                    member_id = max((m.id for m in group.members), default=0) + 1

                    member = Member(id=member_id, name=name, username=username)

                    member.notification_preferences = active

                    member.contact_info = contacts

                    group.members.append(member)

                    print(f"Member {name} (@{username}) added successfully! ID: {member_id}")

                    return

                if answer == "n":

                    raise CancelOperation

                print("Please enter y or n.")

                continue

            stage += 1

        except BackOperation:

            if stage == 0:

                print("Already at the first step. Use 0 to cancel.")

            else:

                stage -= 1

                print("Going back...")

def select_member(group):

    while True:

        name = ask("Member name (b=Back, 0=Cancel): ")

        matches = [m for m in group.members if m.name.casefold() == name.casefold()]

        if not matches:

            print("Member not found!")

            continue

        if len(matches) == 1:

            return matches[0]

        print("Matching members:", ", ".join(f"{m.name} (@{m.username})" for m in matches))

        try:

            username = ask("Username (b=Back, 0=Cancel): ").lstrip("@")

        except BackOperation:

            continue

        selected = next((m for m in matches if m.username.casefold() == username.casefold()), None)

        if selected:

            return selected

        print("Username not found!")

def ask_day(prompt):

    while True:

        day = ask(prompt)

        if is_valid_day(day):

            return day.capitalize()

        print("Invalid day! Use Monday through Sunday.")

def collect_slots():

    slots = []

    while True:

        raw = ask("Time slot (e.g. 9-12; Enter=Finish, b=Back, 0=Cancel): ")

        if not raw:

            if slots:

                return merge_intervals(slots)

            print("Enter at least one time slot, or b to go back.")

            continue

        try:

            parts = raw.split("-")

            if len(parts) != 2:

                raise ValueError

            start, end = map(int, parts)

            if not 0 <= start < end <= 24:

                raise ValueError

        except ValueError:

            print("Invalid time slot! Example: 9-12")

            continue

        slots.append((start, end))

        print("Time slot added.")

def show_availability(member):

    print(f"\nAvailability for {member.name} (@{member.username}):")

    if not any(member.availability.values()):

        print("No availability saved.")

        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:

        slots = member.availability.get(day, [])

        if slots:

            print(f"{day}: " + ", ".join(f"{start}:00-{end}:00" for start, end in slots))

def offer_calendar_event(group, day, meeting_time):

    """Optionally create a calendar event for the next matching weekday."""

    try:

        answer = ask("Add this meeting to Google Calendar? (y/n, b=Back, 0=Cancel): ").lower()

        if answer != "y":

            return

        start_hour, end_hour = meeting_time

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        while True:

            today = date.today()

            days_ahead = (weekdays.index(day) - today.weekday()) % 7

            suggested_date = today + timedelta(days=days_ahead)

            raw_date = ask(

                f"Meeting date YYYY-MM-DD (suggested {suggested_date}; b=Back, 0=Cancel): "

            )

            if not raw_date:

                raw_date = suggested_date.isoformat()

            try:

                meeting_date = date.fromisoformat(raw_date)

            except ValueError:

                print("Invalid date. Use YYYY-MM-DD.")

                continue

            if meeting_date.weekday() != weekdays.index(day):

                print(f"The selected date must be a {day}.")

                continue

            if meeting_date < today:

                print("Please choose a future meeting date.")

                continue

            break

        while True:

            timezone = ask("Time zone (e.g. Europe/Istanbul; b=Back, 0=Cancel): ")

            if not timezone:

                print("Time zone is required.")

                continue

            try:

                ZoneInfo(timezone)

                break

            except (ZoneInfoNotFoundError, ValueError):

                print("Invalid time zone. Example: Europe/Istanbul")

        local_start = datetime.combine(meeting_date, datetime.min.time()).replace(

            hour=start_hour, tzinfo=ZoneInfo(timezone)

        )

        if local_start <= datetime.now(ZoneInfo(timezone)):

            print("That meeting time has already passed in the selected time zone.")

            return

        print(f"Calendar event: {group.name} | {meeting_date} | {start_hour}:00-{end_hour}:00 | {timezone}")

        confirmation = ask("Create this Google Calendar event? (y/n, b=Back, 0=Cancel): ").lower()

        if confirmation == "y":

            create_calendar_event(

                f"{group.name} - Group Meeting",

                meeting_date.isoformat(),

                start_hour,

                end_hour,

                timezone=timezone,

            )

    except BackOperation:

        print("Calendar step skipped. Returning to meeting menu...")

def notify_after_availability_change(group):

    if not group.members or not all(m.availability_completed for m in group.members):

        print("Waiting for other members to complete their availability.")

        return

    result = find_best_weekly_meeting(group)

    if result is None:

        print("No common meeting time found!")

        return

    day, time = result

    print(f"Best meeting time: {day}, {time}")

    meeting = (day, time)

    if group.last_notified_meeting != meeting:

        notify_group(group, day, time)

        group.last_notified_meeting = meeting

        print("Notification process completed!")

    else:

        print("Notification already sent for this meeting!")

    offer_calendar_event(group, day, time)

def manage_availability(group):

    if not group.members:

        print("Please add a member first!")

        return

    while True:

        try:

            member = select_member(group)

            break

        except BackOperation:

            print("Returning to main menu...")

            return

    while True:

        print(f"\n===== Availability: {member.name} =====")

        print("1. View Availability")

        print("2. Add / Replace Day")

        print("3. Delete Day")

        print("b. Back to member selection")

        print("0. Cancel / Main Menu")

        try:

            choice = ask("Choose: ").lower()

            if choice == "1":

                show_availability(member)

            elif choice == "2":

                try:

                    day = ask_day("Day (b=Back, 0=Cancel): ")

                    while True:

                        try:

                            slots = collect_slots()

                            print(f"Proposed {day}: {slots}")

                            answer = ask("Save this day? (y/n, b=Back, 0=Cancel): ").lower()

                            if answer == "b":

                                raise BackOperation

                            if answer == "y":

                                if member.availability.get(day) != slots:

                                    member.availability[day] = slots

                                    member.availability_completed = True

                                    print("Availability saved!")

                                    notify_after_availability_change(group)

                                else:

                                    print("No changes made.")

                                break

                            if answer == "n":

                                print("Day changes discarded.")

                                break

                            print("Please enter y or n.")

                        except BackOperation:

                            print("Back to day selection...")

                            break

                except BackOperation:

                    print("Back to availability menu...")

            elif choice == "3":

                try:

                    day = ask_day("Day to delete (b=Back, 0=Cancel): ")

                    if day not in member.availability:

                        print("No availability saved for that day.")

                        continue

                    answer = ask(f"Delete {day}? (y/n, b=Back, 0=Cancel): ").lower()

                    if answer == "y":

                        del member.availability[day]

                        member.availability_completed = any(member.availability.values())

                        print("Day deleted!")

                        notify_after_availability_change(group)

                    elif answer == "n":

                        print("Deletion discarded.")

                except BackOperation:

                    print("Back to availability menu...")

            else:

                print("Invalid choice!")

        except BackOperation:

            print("Back to member selection...")

            try:

                member = select_member(group)

            except BackOperation:

                print("Returning to main menu...")

                return

def find_calendar_meeting_flow(group):

    """Import one availability export per member and suggest a real dated meeting."""

    if not group.members:

        print("Please add members to the group first!")

        return

    print("\n===== Google Calendar Availability =====")

    print("Each member must export their own availability for the SAME date")

    print("and send the JSON file to the group organizer.")

    print("Enter the full path of each member's file (b=Back, 0=Cancel).")

    paths = []

    expected_date = None

    index = 0

    while index < len(group.members):

        member = group.members[index]

        while True:

            try:

                raw = ask(f"JSON file for @{member.username}: ").strip().strip('"')

            except BackOperation:

                if paths:

                    paths.pop()

                    index -= 1

                    expected_date = None if not paths else date.fromisoformat(

                        json.loads(paths[0].read_text(encoding="utf-8"))["date"]

                    )

                    print(f"Back to @{group.members[index].username}...")

                    break

                print("Returning to main menu...")

                return

            path = Path(raw).expanduser()

            try:

                data = json.loads(path.read_text(encoding="utf-8"))

                if not isinstance(data, dict):

                    raise ValueError("Invalid JSON structure.")

                username = data.get("username")

                if not isinstance(username, str) or username.casefold() != member.username.casefold():

                    raise ValueError(f"This file must belong to @{member.username}.")

                meeting_date = date.fromisoformat(data["date"])

                if meeting_date < date.today():

                    raise ValueError("Availability date cannot be in the past.")

                if expected_date is not None and meeting_date != expected_date:

                    raise ValueError("All members must export the same date.")

                if not isinstance(data.get("free_slots"), list):

                    raise ValueError("Missing free_slots list.")

                for slot in data["free_slots"]:

                    start = datetime.fromisoformat(slot["start"])

                    end = datetime.fromisoformat(slot["end"])

                    if start.tzinfo is None or end.tzinfo is None or start >= end:

                        raise ValueError("Invalid time slot or missing timezone.")

                    if start.date() != meeting_date or end.date() not in (meeting_date, meeting_date + timedelta(days=1)):

                        raise ValueError("Time slots must belong to the exported date.")

            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:

                print(f"Cannot use file: {error}")

                continue

            expected_date = meeting_date

            paths.append(path)

            print(f"Loaded availability for @{member.username}.")

            index += 1

            break

    try:

        best = find_best_calendar_meeting(paths)

    except (OSError, ValueError, KeyError, TypeError) as error:

        print(f"Could not calculate meeting time: {error}")

        return

    if best is None:

        print("No common free time found for all members.")

        return

    start, end = best

    if end <= datetime.now(timezone.utc):

        print("The suggested time has already passed. Export a future date.")

        return

    if start < datetime.now(timezone.utc):

        print("The suggested interval has already started. Export a future time window.")

        return

    print(f"\nBest common meeting time for {expected_date}:")

    print(f"Start: {start.isoformat()}")

    print(f"End:   {end.isoformat()}")

    print("Note: These are exported snapshots; members' calendars may change.")

    while True:

        try:

            answer = ask("Create this event in YOUR Google Calendar? (y/n, b=Back, 0=Cancel): ").lower()

        except BackOperation:

            return

        if answer in ("y", "n"):

            break

        print("Please enter y or n.")

    if answer == "n":

        return

    try:

        service = get_calendar_service()

        event = service.events().insert(

            calendarId="primary",

            body={

                "summary": f"{group.name} - Group Meeting",

                "start": {"dateTime": start.isoformat()},

                "end": {"dateTime": end.isoformat()},

            },

        ).execute()

        print("Meeting added to Google Calendar!")

        print("Event link:", event.get("htmlLink", "Not available"))

    except Exception as error:

        print(f"Could not create Google Calendar event: {error}")

def export_calendar_availability_flow():
    """Let a member export their own calendar free slots without a group."""
    print("\n===== Export My Google Calendar Availability =====")
    print("Connect your own Google account and export free time as JSON.")
    print("Use the same username as the one registered in the group.")

    while True:
        username = ask("Your group username (b=Back, 0=Cancel): ").lstrip("@").strip()
        if username and all(c.isalnum() or c in "-_" for c in username):
            break
        print("Username must contain only letters, numbers, - or _.")

    while True:
        raw_date = ask("Meeting date YYYY-MM-DD (b=Back, 0=Cancel): ")
        try:
            meeting_date = date.fromisoformat(raw_date)
            if meeting_date < date.today():
                print("Please choose today or a future date.")
                continue
            break
        except ValueError:
            print("Invalid date. Example: 2026-11-02")

    while True:
        raw_start = ask("Start hour 0-23 (Enter=9, b=Back, 0=Cancel): ")
        try:
            start_hour = int(raw_start) if raw_start else 9
            if not 0 <= start_hour <= 23:
                raise ValueError
            break
        except ValueError:
            print("Enter an hour between 0 and 23.")

    while True:
        raw_end = ask("End hour 1-24 (Enter=17, b=Back, 0=Cancel): ")
        try:
            end_hour = int(raw_end) if raw_end else 17
            if not start_hour < end_hour <= 24:
                raise ValueError
            break
        except ValueError:
            print("End hour must be greater than start hour and at most 24.")

    while True:
        timezone_name = ask("Time zone (Enter=Europe/Istanbul, b=Back, 0=Cancel): ") or "Europe/Istanbul"
        try:
            ZoneInfo(timezone_name)
            break
        except (ZoneInfoNotFoundError, ValueError):
            print("Invalid time zone. Example: Europe/Istanbul")

    print(f"\nExport for @{username}: {meeting_date}, {start_hour}:00-{end_hour}:00 ({timezone_name})")
    confirmation = ask("Connect Google Calendar and export? (y/n, b=Back, 0=Cancel): ").lower()
    if confirmation != "y":
        print("Export skipped.")
        return

    try:
        path = export_availability(username, meeting_date.isoformat(), start_hour, end_hour, timezone_name)
        print(f"Send this JSON file to your group organizer: {path.resolve()}")
        print("Only free time intervals are exported, not calendar event titles.")
    except Exception as error:
        print(f"Could not export availability: {error}")


def run_menu():

    group = None

    while True:

        show_menu()

        choice = input("Choose an option: ").strip()

        if choice == "0":

            print("Goodbye!")

            return

        try:

            if choice == "1":

                name = ask("Group name (0=Cancel): ")

                if not name:

                    print("Group name cannot be empty!")

                    continue

                if group is not None:

                    confirm = ask("Replace current group? (y/n, 0=Cancel): ").lower()

                    if confirm != "y":

                        print("Group creation discarded.")

                        continue

                group = Group(id=1, name=name)

                print(f"Group '{name}' created successfully!")

            elif choice == "2":

                if group is None:

                    print("Please create a group first!")

                else:

                    add_member_flow(group)

            elif choice == "3":

                if group is None:

                    print("Please create a group first!")

                else:

                    manage_availability(group)

            elif choice == "4":

                if group is None:

                    print("Please create a group first!")

                    continue

                while True:

                    try:

                        day = ask_day("Day (b=Back, 0=Cancel): ")

                        break

                    except BackOperation:

                        print("Returning to main menu...")

                        day = None

                        break

                if day is None:

                    continue

                best_time = suggest_meeting_time(group, day)

                if best_time is None:

                    print("No common meeting time found!")

                else:

                    print(f"Best meeting time: {best_time}")

                    try:

                        answer = ask("Notify members? (y/n, b=Back, 0=Cancel): ").lower()

                        if answer == "y":

                            notify_group(group, day, best_time)

                            print("Notification process completed!")

                    except BackOperation:

                        print("Returning to main menu...")

                        continue

                    offer_calendar_event(group, day, best_time)

            elif choice == "5":

                if group is None:

                    print("Please create a group first!")

                else:

                    answer = ask("Save group? (y/n, 0=Cancel): ").lower()

                    if answer == "y":

                        save_group(group, "data/groups.json")

                        print("Group saved successfully!")

            elif choice == "6":

                answer = ask("Load saved group? Current unsaved changes will be lost. (y/n, 0=Cancel): ").lower()

                if answer == "y":

                    try:

                        loaded = load_group("data/groups.json")

                        group = loaded

                        print(f"Group '{group.name}' loaded successfully!")

                        print(f"Total members: {len(group.members)}")

                    except FileNotFoundError:

                        print("No saved group found!")

            elif choice == "7":

                if group is None:

                    print("Please create or load a group first!")

                else:

                    find_calendar_meeting_flow(group)

            elif choice == "8":

                export_calendar_availability_flow()

            else:

                print("Invalid option! Please try again.")

        except CancelOperation:

            print("Operation cancelled. Returning to main menu...")

        except BackOperation:

            print("Returning to main menu...")

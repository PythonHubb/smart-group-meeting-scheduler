import json
from datetime import datetime
from pathlib import Path


def find_overlaps(times1, times2):
    i = j = 0
    overlaps = []
    while i < len(times1) and j < len(times2):
        start1, end1 = times1[i]
        start2, end2 = times2[j]
        start = max(start1, start2)
        end = min(end1, end2)
        if start < end:
            overlaps.append((start, end))
        if end1 < end2:
            i += 1
        else:
            j += 1
    return overlaps


def find_common_time(group, day):
    common = None
    for member in group.members:
        times = member.availability.get(day, [])
        if not times:
            return []
        if common is None:
            common = times.copy()
        else:
            common = find_overlaps(common, times)
        if not common:
            return []
    return common if common is not None else []


def find_best_time(common_times):
    best_time = None
    max_duration = None
    for time in common_times:
        duration = time[1] - time[0]
        if max_duration is None or duration > max_duration:
            max_duration = duration
            best_time = time
    return best_time


def suggest_meeting_time(group, day):
    common_times = find_common_time(group, day)
    return find_best_time(common_times)


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    return merged


def find_best_weekly_meeting(group):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    best_day = best_time = None
    longest_duration = 0
    for day in days:
        meeting_time = suggest_meeting_time(group, day)
        if meeting_time is None:
            continue
        start, end = meeting_time
        duration = end - start
        if duration > longest_duration:
            longest_duration = duration
            best_day = day
            best_time = meeting_time
    if best_time is None:
        return None
    return best_day, best_time


def find_common_calendar_time(file_paths):
    if not file_paths:
        raise ValueError("No availability files provided.")
    common = None
    meeting_date = None
    usernames = set()
    for file_path in file_paths:
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        username = data["username"].strip().casefold()
        current_date = data["date"]
        if not username:
            raise ValueError("Availability file has no username.")
        if username in usernames:
            raise ValueError(f"Duplicate member: {username}")
        usernames.add(username)
        if meeting_date is None:
            meeting_date = current_date
        elif meeting_date != current_date:
            raise ValueError("All availability files must have the same date.")
        slots = []
        for slot in data["free_slots"]:
            start = datetime.fromisoformat(slot["start"])
            end = datetime.fromisoformat(slot["end"])
            if start.tzinfo is None or end.tzinfo is None:
                raise ValueError("Calendar slots must include timezone information.")
            if start >= end:
                raise ValueError("Invalid availability time slot.")
            slots.append((start, end))
        slots = merge_intervals(slots)
        if common is None:
            common = slots
        else:
            common = find_overlaps(common, slots)
        if not common:
            return []
    return common if common is not None else []


def find_best_calendar_meeting(file_paths):
    common_times = find_common_calendar_time(file_paths)
    return find_best_time(common_times)

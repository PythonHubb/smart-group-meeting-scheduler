def find_overlaps(times1, times2):
    i = 0
    j = 0
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
    max_duration = 0

    for time in common_times:
        duration = time[1] - time[0]

        if duration > max_duration:
            max_duration = duration
            best_time = time

    return best_time

def suggest_meeting_time(group, day):
    common_times = find_common_time(group, day)
    best_time = find_best_time(common_times)

    return best_time

def merge_intervals(intervals):
    if not intervals:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]   

    for current in intervals[1:]:
        last = merged[-1]

        if current[0] <= last[1]:
            merged[-1] = (
                last[0],
                max(last[1], current[1])
            )
        else:
            merged.append(current)

    return merged

def find_best_weekly_meeting(group):
    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    best_day = None
    best_time = None
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
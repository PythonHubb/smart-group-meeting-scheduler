# Contribution - Mohamed A Khalifa Omar

- Student ID: 2509115214
- GitHub: [@mohamedelmismary](https://github.com/mohamedelmismary)
- Role: scheduling algorithm and availability management
- Commits: https://github.com/PythonHubb/smart-group-meeting-scheduler/commits?author=mohamedelmismary

## Summary

I wrote the part that finds when everyone is free (`sgp/scheduler.py`) and the
"Manage Availability" part of the menu, where members enter their free hours.

## What I did

### Finding the common free time (`sgp/scheduler.py`)

Every member's free hours for a day are a list like `[(9, 12), (14, 17)]`.

**`find_overlaps(times1, times2)`** finds the hours two members are both free.
Because both lists are sorted, we can go through them once with two pointers
(`i` and `j`) instead of comparing every slot with every other slot.
The overlap is from the later start to the earlier end, and then we move forward in
the list where the slot ends first.

```python
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
```

Example: `[(9, 13), (16, 20)]` and `[(10, 17)]` give `[(10, 13), (16, 17)]`.

**`find_common_time(group, day)`** does this for the whole group. It starts with the
first member's times and overlaps them with each next member. If a member has no time
that day, or nothing is left, it stops early and returns `[]`.

**`find_best_time()`** picks the longest common slot, and
**`suggest_meeting_time(group, day)`** returns the best slot for one day.

**`find_best_weekly_meeting(group)`** checks all 7 days and keeps the day with the
longest slot. Because we use `>` and not `>=`, the earlier day wins if two are equal.

**`merge_intervals(intervals)`** sorts the slots and joins the ones that overlap or touch:

```python
intervals = sorted(intervals)
merged = [intervals[0]]

for current in intervals[1:]:
    last = merged[-1]

    if current[0] <= last[1]:
        merged[-1] = (last[0], max(last[1], current[1]))
    else:
        merged.append(current)
```

Example: `[(14, 17), (9, 12), (11, 13)]` becomes `[(9, 13), (14, 17)]`.

### Manage Availability menu (`sgp/cli/menu.py`)
- `select_member()`: finds the member by name. If two members have the same name it
  asks for the username
- `ask_day()`: asks until a valid day is typed and returns it like `Monday`
- `collect_slots()`: asks the time slots one by one (`9-12`), checks that the hours are
  0-24 and start is before end, and merges them when the user presses Enter

```python
start, end = map(int, parts)
if not 0 <= start < end <= 24:
    raise ValueError
```

- `show_availability()`: prints the saved hours from Monday to Sunday
- `manage_availability()`: the submenu with view, add / replace and delete a day
- `notify_after_availability_change()`: when **every** member has finished their
  availability, it finds the best weekly meeting and sends it. The last sent meeting
  is saved in `last_notified_meeting` so the same meeting is not sent twice

```python
if group.last_notified_meeting != meeting:
    notify_group(group, day, time)
    group.last_notified_meeting = meeting
```

## Python topics I used
- lists of tuples and tuple unpacking
- two-pointer technique with `while` loops
- `sorted()`, `max()`, `min()`
- `map()` and `ValueError` for checking input
- `all()` and `any()`

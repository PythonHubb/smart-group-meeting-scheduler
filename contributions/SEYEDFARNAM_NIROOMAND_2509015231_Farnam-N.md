# Contribution - Seyedfarnam Niroomand

- Student ID: 2509015231
- GitHub: [@Farnam-N](https://github.com/Farnam-N)
- Role: data model, validation, saving/loading, email notifications and presentation
- Commits: https://github.com/PythonHubb/smart-group-meeting-scheduler/commits?author=Farnam-N

## Summary

I wrote the data model, the input checks, saving and loading the group, and the part
that sends the meeting to every member (including real emails with the Gmail API).
I also presented the project.

## What I did

### Data model (`sgp/models.py`)
Two dataclasses that the whole program uses:

```python
@dataclass
class Member:
    id: int
    name: str
    username: str
    availability: dict = field(default_factory=dict)
    availability_completed: bool = False
    notification_preferences: list = field(default_factory=list)
    contact_info: dict = field(default_factory=dict)


@dataclass
class Group:
    id: int
    name: str
    members: list[Member] = field(default_factory=list)
    last_notified_meeting: tuple | None = None
```

`field(default_factory=dict)` is needed so every member gets their own dictionary
and not one shared by everyone.

### Input checks (`sgp/validators.py`)
- `is_valid_name()`: 1-20 characters, only English letters, words separated by one space

```python
return bool(re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", name))
```

- `is_valid_email()`: checks the format with a regular expression
  (`name@example.com` is ok, `name@` is not)
- `is_valid_day()`: accepts the 7 day names in any upper / lower case

### Saving and loading (`sgp/storage.py`)
- `save_group()`: turns the group into a dictionary with `asdict()` and saves it as JSON
  in `data/groups.json`. It creates the `data` folder if it doesn't exist
- `load_group()`: reads the JSON back into `Group` and `Member` objects. JSON has no
  tuples, so the time slots are turned back into tuples:

```python
member.availability = {
    day: [tuple(time) for time in times]
    for day, times in member_data.get("availability", {}).items()
}
```

- if a username is missing or used twice in the file, it gets fixed (`ayla`, `ayla_2`...)
  so two members never have the same username:

```python
while username.casefold() in used_usernames:
    username = f"{base_username}_{counter}"
    counter += 1
```

### Sending the meeting (`sgp/notifications/simulated.py`)
- builds the message (hello, group name, day and time)
- goes through every platform the member chose: email and Telegram are really sent,
  WhatsApp and SMS are printed as `[SIMULATED WHATSAPP]` / `[SIMULATED SMS]`
- if a contact is missing it prints a warning instead of crashing
- `notify_group()` does this for every member

### Email (`sgp/notifications/email_sender.py`)
- Gmail API with OAuth 2.0, only the `gmail.send` permission
- the first time a browser opens for login, then the token is saved in `token.json`
  and refreshed when it expires
- the email is built with `EmailMessage` and encoded with base64url, which is what
  the Gmail API wants

```python
encoded_message = base64.urlsafe_b64encode(email.as_bytes()).decode("utf-8")

service.users().messages().send(
    userId="me",
    body={"raw": encoded_message}
).execute()
```

- returns `True` or `False` so one failed email doesn't stop the program

### Other
- `requirements.txt` with the package versions

### Presentation
- prepared the slides and explained the project and the code in class

## Python topics I used
- `@dataclass` and `field(default_factory=...)`
- regular expressions (`re.fullmatch`)
- `json`, `pathlib`, `dataclasses.asdict`
- dictionary comprehension and sets
- OAuth 2.0 with the Google libraries, `base64`, `email.message`
- `try` / `except` for network errors

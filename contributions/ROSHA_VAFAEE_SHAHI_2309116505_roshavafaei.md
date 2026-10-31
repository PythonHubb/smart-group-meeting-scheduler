# Contribution - Rosha Vafaee Shahi

- Student ID: 2309116505
- GitHub: [@roshavafaei](https://github.com/roshavafaei)
- Role: project lead, menu structure, adding members, Telegram verification
- Commits: https://github.com/PythonHubb/smart-group-meeting-scheduler/commits?author=roshavafaei

## Summary

I created the repository and the package structure, wrote the base of the menu
(back / cancel system and the add member flow) and the Telegram account verification.
I also put everyone's parts together and made sure the whole program runs.

## What I did

### Repository and project structure
- created the GitHub repository and the `sgp/` package with the `cli/` and
  `notifications/` subpackages
- `main.py`: loads the `.env` file and starts the menu
- `sgp/__init__.py`: app name and version
- `.gitignore`: keeps `.venv/`, `__pycache__/`, `.env`, `credentials.json`,
  `token.json` and the saved data out of Git

### Back and cancel system (`sgp/cli/menu.py`)
Every question in the menu goes through `ask()`. If the user types `0` or `b`
it raises an exception, and each part of the menu catches it where it makes sense.
This way we didn't need to check for `0` and `b` after every `input()`.

```python
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
```

### Adding a member step by step (`add_member_flow`)
Adding a member has 5 steps: name, username, platforms, contact info and review.
The current step is saved in `stage`, so when the user types `b` we just go one
step back instead of starting again.

```python
stages = ["name", "username", "platforms", "contacts", "confirm"]
...
        except BackOperation:
            if stage == 0:
                print("Already at the first step. Use 0 to cancel.")
            else:
                stage -= 1
                print("Going back...")
```

Other functions I wrote for this:
- `ask_name()` and `ask_username()`: ask again until the input is valid, and usernames
  can't be used twice (not case sensitive)
- `choose_notification_platforms()`: the user types numbers like `1,2`, duplicates
  are removed and the order is kept
- `get_contact_info()`: asks the email / phone / Telegram username for each chosen
  platform. `b` goes back to the previous platform and removes what was entered there
- the new member gets the next free ID:

```python
member_id = max((m.id for m in group.members), default=0) + 1
```

### Telegram verification (`sgp/notifications/telegram_verification.py`)
To connect a member's Telegram we can't just trust the username they type, so:
1. we create a random 8-character code with `secrets`
2. the member sends this code to our bot `@smart_group_meeting_bot`
3. we read the bot's messages with `getUpdates` and only accept the code if it comes
   from a **private** chat with the **same username**

```python
def generate_connection_code():
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))
```

```python
if (
    received_code == connection_code
    and sender_username.casefold() == username.lstrip('@').casefold()
    and chat.get('type') == 'private'
):
    print('Verification successful!')
    return str(chat['id'])
```

- old messages are skipped with the `offset` so an old code can't be used
- the user has 5 minutes (`VERIFICATION_TIMEOUT = 300`)
- while waiting, the user can still press `0` or `b`. On Windows this uses `msvcrt`,
  on Mac/Linux `select`
- `connect_telegram()` in the menu shows the code and lets the user retry or skip

## Python topics I used
- custom exceptions for control flow
- `while` loops with a step counter
- `secrets` and `string` for random codes
- HTTP requests with `urllib` and JSON
- `time.monotonic()` for the timeout
- platform specific code with `os.name`
- `python-dotenv` for the bot token

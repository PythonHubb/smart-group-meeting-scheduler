# Contribution - Borna Anlar

- Student ID: 2509115360
- GitHub: [@borna111184-creator](https://github.com/borna111184-creator)
- Role: main menu, Telegram messages and test scripts
- Commits: https://github.com/PythonHubb/smart-group-meeting-scheduler/commits?author=borna111184-creator

## Summary

I wrote the main menu loop that connects all the features, sending Telegram messages
and the test scripts for email and Telegram.

## What I did

### Main menu (`run_menu()` in `sgp/cli/menu.py`)
The main loop that shows the menu and calls the right part for each option:
- `1` create a group (asks before replacing the current one)
- `2` add member, `3` manage availability
- `4` suggest a meeting time for a day and optionally notify everyone
- `5` save and `6` load the group (`data/groups.json`)
- `0` exit

Options 2-5 only work if a group exists:

```python
elif choice == "2":
    if group is None:
        print("Please create a group first!")
    else:
        add_member_flow(group)
```

At the end of the loop the cancel and back exceptions are caught, so whatever happens
inside an option the user always comes back to the main menu:

```python
except CancelOperation:
    print("Operation cancelled. Returning to main menu...")
except BackOperation:
    print("Returning to main menu...")
```

Loading also handles the case when there is no saved file yet:

```python
except FileNotFoundError:
    print("No saved group found!")
```

### Sending Telegram messages (`sgp/notifications/telegram_sender.py`)
- reads the bot token from `.env`
- sends the message with a POST request to the Telegram Bot API (`sendMessage`)
  using only `urllib`, no extra library
- uses the `certifi` certificates, because on some computers (especially Mac) Python
  can't verify HTTPS without them

```python
ssl_context = ssl.create_default_context(cafile=certifi.where())

with urllib.request.urlopen(request, context=ssl_context, timeout=15) as response:
    result = json.load(response)
```

- returns `True` / `False` and only prints the error type, so the token is never printed

### Test scripts (`tests/`)
We test email and Telegram with real messages:
- `test_email.py`: sends a test email to an address you type
- `test_telegram.py`: prints the chat IDs of the people who wrote to the bot
  (we used this to find our own chat IDs)
- `test_telegram_send.py`: sends a message directly with the API
- `test_telegram_sender.py`: tests our `send_telegram()` function
- `test_telegram_verification.py`: tests the full connect flow with a real code

## Python topics I used
- `while True` menu loops and `if / elif`
- catching exceptions (`FileNotFoundError`, our own exceptions)
- HTTP POST requests with `urllib` and `urlencode`
- SSL with `certifi`
- JSON
- `python-dotenv` for secrets

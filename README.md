# 📅 Smart Group Meeting Scheduler

This is our Python project! It's a console app for student groups: every member enters
when they are free during the week, the program finds a time that works for everyone
and sends the meeting to each member on email, Telegram, WhatsApp or SMS. 🎉

We got the idea because in every group project we spend way too long just finding a time
to meet... and then half the group doesn't even see the message 😅

📧 Email (Gmail API) and 💬 Telegram (our own bot) really send messages.
📱 WhatsApp and SMS are only simulated for now, they just print the message in the terminal.

## 🎬 See how it works

Want to see the whole thing without running it? We made a short visual walkthrough 👇

**[📖 Smart Group Meeting Scheduler: How it works (PDF)](docs/how-it-works.pdf)**

It follows our own team (Rosha, Mohamed, Farnam and Borna) through every step: creating the group,
connecting Telegram, adding free hours, finding the meeting time and getting notified.
Each page shows what our program prints in the terminal next to how it would look as a real app 📱

It also shows what we're building next:
- 🚧 **Google Calendar import:** connect your calendar and your free hours are filled in automatically
- 🔮 **Fair task distribution:** everyone rates their skills and tasks are split fairly

## ✨ Features

- 👥 create a group and add members step by step
- 🔔 each member picks their notification platforms (email, Telegram, WhatsApp, SMS)
- 🔐 connecting Telegram with a code that you send to our bot
- 🕒 add / replace / view / delete free hours for each day (whole hours, like `9-12`)
- 🔍 find the best meeting time for one day or for the whole week
- 📣 when everyone has entered their availability the meeting is sent automatically
  (and it won't send the same meeting twice)
- 💾 save the group to `data/groups.json` and load it again
- ↩️ you can type `b` to go back or `0` to cancel at any question

## 🧰 Requirements

- 🐍 Python 3.10+
- 📦 packages from `requirements.txt`
- 🔑 `.env` file with the Telegram bot token (only for Telegram)
- 📄 `credentials.json` from Google Cloud (only for email)

## 📦 Installation

```powershell
git clone https://github.com/PythonHubb/smart-group-meeting-scheduler.git
cd smart-group-meeting-scheduler
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows
# source .venv/bin/activate           # Mac / Linux
pip install -r requirements.txt
```

Then make a `.env` file in the project folder:

```text
TELEGRAM_BOT_TOKEN=your-bot-token
```

For email you need to enable the Gmail API in Google Cloud Console, create an OAuth
client (Desktop app) and save it as `credentials.json` in the project folder. The first
time it sends an email a browser opens for login and `token.json` gets created.

⚠️ Don't upload `.env`, `credentials.json` or `token.json`! They're already in `.gitignore`.

## ▶️ How to run

```powershell
python main.py
```

```text
===== Smart Group Project =====
1. Create Group
2. Add Member
3. Manage Availability
4. Suggest Meeting Time
5. Save Group
6. Load Group
0. Exit
```

## 🧠 How it finds the meeting time

Every member's free hours for a day are saved as a list of `(start, end)`, for example
`[(9, 12), (14, 17)]`. If you enter slots that overlap, they get merged
(`9-12` and `11-14` -> `9-14`).

To find when two people are both free we go through both lists with two pointers 👉👈
The overlap is from the later start to the earlier end, and then we move forward in
the list where the slot ends first. We do this for every member, and if nothing is left
at some point then there's no common time that day.

The longest common slot is the suggestion 🏆 For the whole week, the day with the longest
slot wins (if two days are equal the earlier day wins).

## 📂 Project structure

```text
main.py                          starts the program
sgp/
  __init__.py                    app name and version
  models.py                      Member and Group
  scheduler.py                   finding the common free time
  validators.py                  checking names, emails and days
  storage.py                     save / load the group as JSON
  cli/menu.py                    the menu
  notifications/
    simulated.py                 sends the meeting on each member's platforms
    email_sender.py              Gmail API
    telegram_sender.py           Telegram Bot API
    telegram_verification.py     connecting a Telegram account with a code
tests/                           test scripts
docs/how-it-works.pdf            visual walkthrough
```

## 🧪 Tests

The scripts in `tests/` send real messages, so you need the `.env` and Gmail setup first.
Run them one by one:

```powershell
python -m tests.test_email
python -m tests.test_telegram_sender
python -m tests.test_telegram_verification
```

## 🚧 Limitations

- only whole hours, `9:30` doesn't work
- availability is the same every week
- WhatsApp and SMS are simulated
- everyone has to be in the same time zone
- only one saved group (`data/groups.json`)

## 👥 Team

| Name | Student ID | GitHub | Contribution |
| --- | --- | --- | --- |
| Seyedfarnam Niroomand | 2509015231 | [@Farnam-N](https://github.com/Farnam-N) | [📄 See contribution](contributions/SEYEDFARNAM_NIROOMAND_2509015231_Farnam-N.md) |
| Mohamed A Khalifa Omar | 2509115214 | [@mohamedelmismary](https://github.com/mohamedelmismary) | [📄 See contribution](contributions/MOHAMED_A_KHALIFA_OMAR_2509115214_mohamedelmismary.md) |
| Rosha Vafaee Shahi | 2309116505 | [@roshavafaei](https://github.com/roshavafaei) | [📄 See contribution](contributions/ROSHA_VAFAEE_SHAHI_2309116505_roshavafaei.md) |
| Borna Anlar | 2509115360 | [@borna111184-creator](https://github.com/borna111184-creator) | [📄 See contribution](contributions/BORNA_ANLAR_2509115360_borna111184-creator.md) |

Made with ☕ and a lot of group chat messages 💬

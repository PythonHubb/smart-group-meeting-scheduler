from dotenv import load_dotenv

load_dotenv()

from sgp import APP_NAME, VERSION
from sgp.scheduler import suggest_meeting_time
from sgp.notifications.simulated import notify_group
from sgp.cli.menu import run_menu


def schedule_meeting(group, day):
    best_time = suggest_meeting_time(group, day)

    if best_time is None:
        print("No common meeting time found.")
        return

    notify_group(group, day, best_time)


def main():
    print(f"Welcome to {APP_NAME}!")
    print(f"Version: {VERSION}")
    run_menu()


if __name__ == "__main__":
    main()

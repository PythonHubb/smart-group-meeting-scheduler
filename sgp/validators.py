
import re


def is_valid_name(name):
    if not 1 <= len(name) <= 20:
        return False

    return bool(
        re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", name)
    )


def is_valid_email(email):
    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+"
            r"(?:\.[A-Za-z0-9-]+)+",
            email
        )
    )



def is_valid_day(day):
    valid_days = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }

    return day.strip().lower() in valid_days

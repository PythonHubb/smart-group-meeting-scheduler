
from sgp.notifications.email_sender import send_email
from sgp.notifications.telegram_sender import send_telegram


def send_notification(member, group, day, meeting_time):
    start, end = meeting_time

    message = (
        f"Hello {member.name}!\n\n"
        f"Your group '{group.name}' has scheduled a meeting.\n\n"
        f"Day: {day}\n"
        f"Time: {start}:00 - {end}:00\n\n"
        "See you there!"
    )

    for platform in member.notification_preferences:

        if platform == "email":
            receiver_email = member.contact_info.get("email")

            if receiver_email:
                send_email(
                    receiver_email=receiver_email,
                    subject=f"Meeting Scheduled - {group.name}",
                    message=message
                )
            else:
                print(f"No email address found for {member.name}!")

        elif platform == "telegram":
            chat_id = member.contact_info.get("telegram")

            if chat_id:
                send_telegram(
                    chat_id=chat_id,
                    message=message
                )
            else:
                print(f"No Telegram Chat ID found for {member.name}!")

        elif platform == "whatsapp":
            print(f"[SIMULATED WHATSAPP] {message}")

        elif platform == "sms":
            print(f"[SIMULATED SMS] {message}")


def notify_group(group, day, meeting_time):
    for member in group.members:
        send_notification(member, group, day, meeting_time)

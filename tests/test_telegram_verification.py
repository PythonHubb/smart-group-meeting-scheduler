
from sgp.notifications.telegram_verification import (
    generate_connection_code,
    verify_telegram_code
)


username = input("Enter your Telegram username: ").strip()

code = generate_connection_code()

print("\nOpen @smart_group_meeting_bot")
print("Send this code to the bot:", code)

input("\nPress Enter after sending the code...")

chat_id = verify_telegram_code(code, username)

if chat_id:
    print("Telegram connected successfully!")
else:
    print("Verification failed!")

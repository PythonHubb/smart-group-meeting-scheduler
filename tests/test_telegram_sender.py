
from sgp.notifications.telegram_sender import send_telegram

chat_id = input("Enter your Telegram Chat ID: ").strip()

success = send_telegram(
    chat_id,
    "Hello! Telegram Sender is working!"
)

if success:
    print("Test completed successfully!")
else:
    print("Test failed!")

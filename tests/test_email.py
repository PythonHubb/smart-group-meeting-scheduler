
from dotenv import load_dotenv
from sgp.notifications.email_sender import send_email

from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env", override=True)

receiver = input("Enter receiver email: ").strip()

success = send_email(
    receiver_email=receiver,
    subject="Smart Group Project - Test Email",
    message="Hello! This is a test email from Smart Group Project."
)

if success:
    print("Test completed successfully!")
else:
    print("Email test failed!")

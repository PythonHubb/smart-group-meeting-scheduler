
import os
import json
import ssl
import certifi
import urllib.request
import urllib.parse

from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def send_telegram(chat_id, message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Telegram bot token not found!")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST"
    )

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    try:
        with urllib.request.urlopen(
            request,
            context=ssl_context,
            timeout=15
        ) as response:
            result = json.load(response)

        if result.get("ok"):
            print("Telegram message sent successfully!")
            return True

        return False

    except Exception as error:
        print(f"Telegram message failed: {type(error).__name__}")
        return False

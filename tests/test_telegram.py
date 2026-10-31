
import os
import json
import urllib.request
from pathlib import Path
import ssl
import certifi

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")

url = f"https://api.telegram.org/bot{token}/getUpdates"

ssl_context = ssl.create_default_context(cafile=certifi.where())

with urllib.request.urlopen(url, context=ssl_context, timeout=15) as response:
    data = json.load(response)

if not data.get("ok"):
    raise RuntimeError("Telegram API request failed")

for update in data.get("result", []):
    message = update.get("message", {})
    chat = message.get("chat", {})

    if chat.get("type") == "private":
        print("Chat ID:", chat.get("id"))

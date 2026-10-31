
import os
import json
import ssl
import certifi
import urllib.request
import urllib.parse

from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")

chat_id = input("Enter your Telegram Chat ID: ").strip()

message = "Hello! This is my first real Telegram message from Smart Group Project!"

url = f"https://api.telegram.org/bot{token}/sendMessage"

payload = urllib.parse.urlencode({
    "chat_id": chat_id,
    "text": message
}).encode("utf-8")

request = urllib.request.Request(url, data=payload, method="POST")

ssl_context = ssl.create_default_context(cafile=certifi.where())

with urllib.request.urlopen(request, context=ssl_context, timeout=15) as response:
    result = json.load(response)

if result.get("ok"):
    print("Telegram message sent successfully!")
else:
    print("Telegram message failed!")

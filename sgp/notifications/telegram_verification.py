import secrets
import string
import os
import json
import ssl
import time
import sys
import certifi
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / '.env')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
VERIFICATION_TIMEOUT = 300
POLL_INTERVAL = 3


def generate_connection_code():
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


def get_telegram_updates(offset=None):
    if not BOT_TOKEN:
        raise ValueError('Telegram bot token not found!')

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    parameters = {'timeout': 0}
    if offset is not None:
        parameters['offset'] = offset

    payload = urllib.parse.urlencode(parameters).encode('utf-8')
    request = urllib.request.Request(url, data=payload, method='POST')
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, context=ssl_context, timeout=15) as response:
        return json.load(response)


def _read_cancel_key():
    """Non-blocking terminal key read. Returns '0', 'b', or None."""
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            key = msvcrt.getwch().lower()
            if key in ('0', 'b'):
                print(f'\n{key}')
                return key
        return None

    # Unix terminals: select checks stdin without waiting for user input.
    import select
    if sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip().lower()
        if line in ('0', 'b'):
            return line
    return None


def verify_telegram_code(connection_code, username):
    """Return chat ID, '__cancel__', '__back__', or None on failure."""
    print('\nWaiting for Telegram verification...')
    print('You have 5 minutes to send the code.')
    print('Press 0 to Cancel or b to Back while waiting.')

    try:
        initial_data = get_telegram_updates()
        existing_updates = initial_data.get('result', [])
        offset = existing_updates[-1]['update_id'] + 1 if existing_updates else None
        deadline = time.monotonic() + VERIFICATION_TIMEOUT

        while time.monotonic() < deadline:
            command = _read_cancel_key()
            if command is not None:
                print("Telegram verification stopped.")
                return "__cancel__" if command == "0" else "__back__"

            data = get_telegram_updates(offset=offset)
            for update in data.get('result', []):
                offset = update['update_id'] + 1
                message = update.get('message', {})
                sender = message.get('from', {})
                chat = message.get('chat', {})
                received_code = message.get('text', '').strip()
                sender_username = sender.get('username', '')

                if (
                    received_code == connection_code
                    and sender_username.casefold() == username.lstrip('@').casefold()
                    and chat.get('type') == 'private'
                ):
                    print('Verification successful!')
                    return str(chat['id'])

            # Short sleeps let us react to Back/Cancel promptly.
            remaining = min(POLL_INTERVAL, max(0, deadline - time.monotonic()))
            while remaining > 0:
                command = _read_cancel_key()
                if command is not None:
                    print("Telegram verification stopped.")
                    return "__cancel__" if command == "0" else "__back__"
                pause = min(0.1, remaining)
                time.sleep(pause)
                remaining -= pause

        print('Verification code expired!')
        return None

    except (OSError, ValueError, KeyError) as error:
        print(f'Telegram verification error: {type(error).__name__}')
        return None

import os
import requests


class TelegramError(Exception):
    pass


def send_message(text):
    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not token:
        raise TelegramError(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    if not chat_id:
        raise TelegramError(
            "TELEGRAM_CHAT_ID is not configured."
        )

    url = (
        f"https://api.telegram.org/bot"
        f"{token}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        raise TelegramError(
            f"Telegram HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    if not data.get("ok"):
        raise TelegramError(
            data.get(
                "description",
                "Telegram returned an error.",
            )
        )

    return data

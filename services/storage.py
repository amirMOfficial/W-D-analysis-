import json
from pathlib import Path


STATE_FILE = Path("data/daily_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {}

    try:
        with STATE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = STATE_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temp_file.replace(STATE_FILE)


def get_previous_price():
    state = load_state()
    return state.get("last_price")


def save_current_price(price, message_date):
    state = load_state()

    state["last_price"] = price
    state["last_message_date"] = message_date

    save_state(state)

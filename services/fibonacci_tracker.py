import json
import os
from datetime import datetime, timezone

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "fibonacci_levels.json"
)

FIB_RATIO = 0.618


def ensure_data_file():

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "levels": []
                },
                f,
                indent=2,
                ensure_ascii=False
            )


def load_levels():

    ensure_data_file()

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data.get("levels", [])


def save_levels(levels):

    ensure_data_file()

    temp_file = DATA_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "levels": levels
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        DATA_FILE
    )


def calculate_fib_0618(
    open_price,
    high,
    low,
    close
):

    if close > open_price:

        candle_type = "green"

        level = low + (
            (high - low) * FIB_RATIO
        )

    elif close < open_price:

        candle_type = "red"

        level = high - (
            (high - low) * FIB_RATIO
        )

    else:

        candle_type = "doji"

        level = low + (
            (high - low) * FIB_RATIO
        )

    return candle_type, level


def add_daily_fibonacci(candle):

    levels = load_levels()

    date = candle["date"]

    # Prevent duplicate daily Fib.
    for item in levels:

        if item["date"] == date:

            return False, item

    candle_type, fib_level = calculate_fib_0618(
        open_price=candle["open"],
        high=candle["high"],
        low=candle["low"],
        close=candle["close"]
    )

    item = {
        "date": date,
        "candle_type": candle_type,
        "open": candle["open"],
        "high": candle["high"],
        "low": candle["low"],
        "close": candle["close"],
        "fib_0618": round(fib_level, 2),
        "reached": False,
        "reached_at": None,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    levels.append(item)

    levels.sort(
        key=lambda x: x["date"]
    )

    save_levels(levels)

    return True, item


def check_price_against_levels(
    price_low,
    price_high
):

    levels = load_levels()

    reached = []

    changed = False

    for item in levels:

        if item["reached"]:
            continue

        fib = float(
            item["fib_0618"]
        )

        # The price touched the Fib if the
        # candle range contains the Fib level.
        if price_low <= fib <= price_high:

            item["reached"] = True

            item["reached_at"] = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

            reached.append(item)

            changed = True

    if changed:

        save_levels(levels)

    return reached

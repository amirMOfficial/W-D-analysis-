from datetime import datetime, timezone, timedelta

from services.coinmarketcap import (
    get_btc_price,
    get_fear_greed,
)

from services.telegram import (
    send_message,
)

from services.storage import (
    get_previous_price,
    save_current_price,
)


# ============================================================
# TIMEZONE
# ============================================================

TEHRAN_TZ = timezone(
    timedelta(hours=3, minutes=30)
)


# ============================================================
# CALCULATIONS
# ============================================================

def calculate_change(
    current_price,
    previous_price,
):
    """
    Calculate percentage change between
    today's Telegram message price and
    the previous Telegram message price.
    """

    if previous_price is None:
        return None

    if previous_price == 0:
        return None

    return (
        (current_price - previous_price)
        / previous_price
    ) * 100


# ============================================================
# FORMATTERS
# ============================================================

def format_price(value):
    return f"${value:,.2f}"


def format_change(change):
    if change is None:
        return "N/A — first daily message"

    if change > 0:
        return f"🟢 +{change:.2f}%"

    if change < 0:
        return f"🔴 {change:.2f}%"

    return "⚪ 0.00%"


# ============================================================
# TELEGRAM MESSAGE
# ============================================================

def build_message(
    now,
    price,
    change,
    fear_greed,
):
    date_text = now.strftime(
        "%Y-%m-%d"
    )

    time_text = now.strftime(
        "%H:%M"
    )

    change_text = format_change(
        change
    )

    message = f"""
<b>₿ BITCOIN </b>
🕒 <b>Daily Start:</b>
{date_text} — {time_text} UTC+3:30

━━━━━━━━━━━━━━━━━━
💰 <b>Bitcoin Price:</b>
{format_price(price)}

📊 <b>Change vs Previous Daily:</b>
{change_text}

😨 <b>Fear &amp; Greed</b>
{fear_greed["value"]} — {fear_greed["classification"]}

━━━━━━━━━━━━━━━━━━


""".strip()

    return message


# ============================================================
# MAIN
# ============================================================

def main():

    now = datetime.now(
        TEHRAN_TZ
    )

    print("=" * 60)
    print("BTC DAILY ANALYSIS")
    print("=" * 60)

    print(
        f"Execution time: "
        f"{now.isoformat()}"
    )

    # --------------------------------------------------------
    # 1. BTC PRICE
    # --------------------------------------------------------

    print()
    print("Fetching BTC price...")

    price = get_btc_price()

    print(
        f"BTC price received: "
        f"${price:,.2f}"
    )

    # --------------------------------------------------------
    # 2. PREVIOUS TELEGRAM MESSAGE PRICE
    # --------------------------------------------------------

    print()
    print(
        "Loading previous message price..."
    )

    previous_price = (
        get_previous_price()
    )

    if previous_price is None:

        print(
            "No previous daily price found."
        )

    else:

        print(
            f"Previous message price: "
            f"${previous_price:,.2f}"
        )

    # --------------------------------------------------------
    # 3. CALCULATE CHANGE
    # --------------------------------------------------------

    change = calculate_change(
        current_price=price,
        previous_price=previous_price,
    )

    if change is None:

        print(
            "Change: N/A"
        )

    else:

        print(
            f"Change vs previous message: "
            f"{change:+.2f}%"
        )

    # --------------------------------------------------------
    # 4. FEAR & GREED
    # --------------------------------------------------------

    print()
    print(
        "Fetching Fear & Greed..."
    )

    fear_greed = get_fear_greed()

    print(
        f"Fear & Greed: "
        f"{fear_greed['value']} "
        f"({fear_greed['classification']})"
    )

    # --------------------------------------------------------
    # 5. BUILD MESSAGE
    # --------------------------------------------------------

    message = build_message(
        now=now,
        price=price,
        change=change,
        fear_greed=fear_greed,
    )

    print()
    print("=" * 60)
    print("TELEGRAM MESSAGE")
    print("=" * 60)

    print(message)

    print("=" * 60)

    # --------------------------------------------------------
    # 6. SEND TELEGRAM
    # --------------------------------------------------------

    print()
    print(
        "Sending message to Telegram..."
    )

    send_message(message)

    print(
        "TELEGRAM: MESSAGE SENT SUCCESSFULLY"
    )

    # --------------------------------------------------------
    # 7. SAVE PRICE
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Save ONLY after Telegram succeeds.
    #
    # Therefore:
    #
    # Telegram failed
    #       ↓
    # price is NOT saved
    #
    # Telegram succeeded
    #       ↓
    # today's price becomes
    # tomorrow's previous price
    #

    save_current_price(
        price=price,
        message_date=now.isoformat(),
    )

    print(
        "Daily state saved."
    )

    print()
    print("=" * 60)
    print("DAILY ANALYSIS: SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()

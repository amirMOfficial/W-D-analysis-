from datetime import (
    datetime,
    timezone,
    timedelta,
)

from services.coinmarketcap import (
    get_btc_price,
    get_previous_daily_candle,
    get_fear_greed,
)

from services.technical_analysis import (
    get_btc_daily_ta,
    TechnicalAnalysisError,
)

from services.telegram import (
    send_message,
)

from services.storage import (
    get_previous_price,
    save_current_price,
)


UTC_PLUS_3_30 = timezone(
    timedelta(hours=3, minutes=30)
)


def calculate_change(
    current_price,
    previous_price,
):
    if previous_price is None:
        return None

    if previous_price == 0:
        return None

    return (
        (current_price - previous_price)
        / previous_price
    ) * 100


def calculate_fibonacci_618(
    high,
    low,
):
    """
    Fibonacci 0.618 measured from previous-day
    High/Low range.

    For the first version we use:

        Low + (High - Low) * 0.618

    This represents the 61.8% retracement level
    measured upward from Low.
    """

    return low + (
        (high - low) * 0.618
    )


def format_price(value):
    return f"${value:,.2f}"


def format_optional(value):
    if value is None:
        return "N/A"

    if isinstance(value, float):
        return f"{value:.2f}"

    return str(value)


def get_position(
    price,
    ema,
):
    if ema is None:
        return "N/A"

    if price > ema:
        return "Above EMA330"

    if price < ema:
        return "Below EMA330"

    return "At EMA330"


def build_message(
    now,
    price,
    change,
    fear_greed,
    candle,
    fib618,
    technical,
):
    date_text = now.strftime(
        "%Y-%m-%d"
    )

    time_text = now.strftime(
        "%H:%M"
    )

    rsi = technical.get("rsi")
    ema330 = technical.get("ema330")
    stoch_k = technical.get("stoch_k")
    stoch_d = technical.get("stoch_d")

    position = get_position(
        price,
        ema330,
    )

    if change is None:
        change_text = "N/A — first daily message"
    else:
        change_text = f"{change:+.2f}%"

    message = f"""
<b>₿ BITCOIN — DAILY ANALYSIS</b>

🕒 <b>Daily Start:</b>
{date_text} — {time_text} UTC+3:30

💰 <b>BTC Price:</b>
{format_price(price)}

📊 <b>Change vs Yesterday's Message:</b>
{change_text}

😨 <b>Fear &amp; Greed:</b>
{fear_greed['value']} — {fear_greed['classification']}

━━━━━━━━━━━━━━━━━━

📈 <b>DAILY INDICATORS</b>

<b>RSI(14):</b>
{format_optional(rsi)}

<b>Stochastic(14,3,3):</b>
K: {format_optional(stoch_k)}
D: {format_optional(stoch_d)}

<b>EMA330:</b>
{format_price(ema330) if ema330 is not None else "N/A"}

<b>Price Position:</b>
{position}

━━━━━━━━━━━━━━━━━━

🕯 <b>PREVIOUS DAY CANDLE</b>

Open:
{format_price(candle['open'])}

High:
{format_price(candle['high'])}

Low:
{format_price(candle['low'])}

Close:
{format_price(candle['close'])}

━━━━━━━━━━━━━━━━━━

📐 <b>FIBONACCI 0.618</b>

{format_price(fib618)}

━━━━━━━━━━━━━━━━━━

<i>All market indicators are Daily (1D).</i>
<i>Stochastic is temporarily unavailable from CMC TA.</i>
"""

    return message.strip()


def main():
    now = datetime.now(
        UTC_PLUS_3_30
    )

    print("=" * 60)
    print("BTC DAILY ANALYSIS")
    print("=" * 60)

    print(
        f"Execution time: "
        f"{now.isoformat()}"
    )

    # --------------------------------------------------
    # 1. BTC PRICE
    # --------------------------------------------------

    print("Fetching BTC price...")

    price = get_btc_price()

    print(
        f"BTC price received: "
        f"${price:,.2f}"
    )

    # --------------------------------------------------
    # 2. PREVIOUS MESSAGE PRICE
    # --------------------------------------------------

    previous_price = get_previous_price()

    change = calculate_change(
        price,
        previous_price,
    )

    if previous_price is None:
        print(
            "No previous message price found."
        )
    else:
        print(
            f"Previous message price: "
            f"${previous_price:,.2f}"
        )

        print(
            f"Change: "
            f"{change:+.2f}%"
        )

    # --------------------------------------------------
    # 3. PREVIOUS DAILY CANDLE
    # --------------------------------------------------

    print(
        "Fetching previous completed Daily candle..."
    )

    candle = get_previous_daily_candle()

    print(
        f"Previous candle High: "
        f"${candle['high']:,.2f}"
    )

    print(
        f"Previous candle Low: "
        f"${candle['low']:,.2f}"
    )

    # --------------------------------------------------
    # 4. FIBONACCI
    # --------------------------------------------------

    fib618 = calculate_fibonacci_618(
        candle["high"],
        candle["low"],
    )

    print(
        f"Fibonacci 0.618: "
        f"${fib618:,.2f}"
    )

    # --------------------------------------------------
    # 5. FEAR & GREED
    # --------------------------------------------------

    print(
        "Fetching Fear & Greed..."
    )

    fear_greed = get_fear_greed()

    print(
        f"Fear & Greed: "
        f"{fear_greed['value']} "
        f"({fear_greed['classification']})"
    )

    # --------------------------------------------------
    # 6. TECHNICAL ANALYSIS
    # --------------------------------------------------

    print(
        "Fetching CMC Daily Technical Analysis..."
    )

    try:
        technical = get_btc_daily_ta()

        print(
            f"RSI: "
            f"{technical.get('rsi')}"
        )

        print(
            f"EMA330: "
            f"{technical.get('ema330')}"
        )

    except TechnicalAnalysisError as exc:
        print(
            f"Technical Analysis unavailable: "
            f"{exc}"
        )

        # Do not stop the whole daily report.
        technical = {
            "rsi": None,
            "ema330": None,
            "stoch_k": None,
            "stoch_d": None,
        }

    # --------------------------------------------------
    # 7. BUILD TELEGRAM MESSAGE
    # --------------------------------------------------

    message = build_message(
        now=now,
        price=price,
        change=change,
        fear_greed=fear_greed,
        candle=candle,
        fib618=fib618,
        technical=technical,
    )

    print()
    print("=" * 60)
    print("TELEGRAM MESSAGE")
    print("=" * 60)
    print(message)
    print("=" * 60)

    # --------------------------------------------------
    # 8. SEND TELEGRAM
    # --------------------------------------------------

    print(
        "Sending message to Telegram..."
    )

    send_message(message)

    print(
        "TELEGRAM: MESSAGE SENT SUCCESSFULLY"
    )

    # --------------------------------------------------
    # 9. SAVE CURRENT PRICE
    # --------------------------------------------------
    #
    # IMPORTANT:
    # We save only AFTER Telegram succeeds.
    #
    # Therefore if Telegram fails, today's price does
    # not become tomorrow's "previous message" price.
    # --------------------------------------------------

    save_current_price(
        price=price,
        message_date=now.isoformat(),
    )

    print(
        "Daily state saved."
    )

    print("=" * 60)
    print("DAILY ANALYSIS: SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()

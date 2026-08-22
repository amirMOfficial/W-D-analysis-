import sys

from services.ourbit import (
    get_previous_daily_candle,
    calculate_fibonacci_0618,
    format_candle_date,
    OurbitError,
)


def main():

    print("=" * 70)
    print("OURBIT PREVIOUS DAILY CANDLE TEST")
    print("=" * 70)

    print()
    print("Symbol: BTCUSDT")
    print("Timeframe: 1D")
    print("Timezone reference: UTC")
    print()

    try:

        candle = (
            get_previous_daily_candle()
        )

        fibonacci = (
            calculate_fibonacci_0618(
                high=candle["high"],
                low=candle["low"],
            )
        )

    except OurbitError as exc:

        print()
        print("=" * 70)
        print("PREVIOUS DAILY CANDLE: FAILED")
        print("=" * 70)

        print(str(exc))

        sys.exit(1)

    print("=" * 70)
    print("PREVIOUS COMPLETED DAILY CANDLE")
    print("=" * 70)

    print(
        "Date:",
        format_candle_date(
            candle["open_time"]
        ),
    )

    print(
        "Open:",
        f"{candle['open']:,.2f}",
    )

    print(
        "High:",
        f"{candle['high']:,.2f}",
    )

    print(
        "Low:",
        f"{candle['low']:,.2f}",
    )

    print(
        "Close:",
        f"{candle['close']:,.2f}",
    )

    print(
        "Volume:",
        f"{candle['volume']:,.6f}",
    )

    print()
    print("=" * 70)
    print("FIBONACCI 0.618")
    print("=" * 70)

    print(
        "Calculation:"
    )

    print(
        "Low + ((High - Low) × 0.618)"
    )

    print(
        f"{candle['low']:,.2f} + "
        f"(({candle['high']:,.2f} - "
        f"{candle['low']:,.2f}) × 0.618)"
    )

    print(
        "0.618 Level:",
        f"{fibonacci:,.2f}",
    )

    print()
    print("=" * 70)
    print("PREVIOUS DAILY CANDLE: SUCCESS")
    print("=" * 70)

    print()
    print(
        "No RSI calculated."
    )

    print(
        "No Stochastic calculated."
    )

    print(
        "No EMA calculated."
    )

    print(
        "Only Fibonacci 0.618 was calculated."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

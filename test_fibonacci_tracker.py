from services.fibonacci_tracker import (
    calculate_fib_0618,
    add_daily_fibonacci,
    load_levels,
    check_price_against_levels,
)


def main():

    print("=" * 70)
    print("FIBONACCI MEMORY TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Example candle
    # --------------------------------------------------------

    candle = {
        "date": "TEST-2026-08-21",
        "open": 60000.0,
        "high": 61500.0,
        "low": 60000.0,
        "close": 61000.0,
    }

    candle_type, fib = calculate_fib_0618(
        open_price=candle["open"],
        high=candle["high"],
        low=candle["low"],
        close=candle["close"],
    )

    print()
    print("CANDLE TYPE:")
    print(candle_type)

    print()
    print("FIB 0.618:")
    print(f"{fib:,.2f}")

    # --------------------------------------------------------
    # Save Fib
    # --------------------------------------------------------

    created, item = add_daily_fibonacci(
        candle
    )

    print()
    print(
        "NEW FIB CREATED:",
        created
    )

    print()
    print("SAVED LEVEL:")
    print(item)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    levels = load_levels()

    print()
    print(
        "TOTAL SAVED LEVELS:",
        len(levels)
    )

    # --------------------------------------------------------
    # Test NOT reached
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST 1: PRICE DOES NOT REACH FIB")
    print("=" * 70)

    reached = check_price_against_levels(
        price_low=60500,
        price_high=60600,
    )

    print(
        "REACHED:",
        len(reached)
    )

    # --------------------------------------------------------
    # Test reached
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST 2: PRICE REACHES FIB")
    print("=" * 70)

    reached = check_price_against_levels(
        price_low=60500,
        price_high=60700,
    )

    print(
        "REACHED:",
        len(reached)
    )

    for item in reached:

        print()
        print(
            "FIB REACHED:"
        )

        print(
            "Date:",
            item["date"]
        )

        print(
            "Fib:",
            item["fib_0618"]
        )

        print(
            "Reached at:",
            item["reached_at"]
        )

    # --------------------------------------------------------
    # Final state
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL STORED LEVELS")
    print("=" * 70)

    for item in load_levels():

        print(
            item
        )

    print()
    print("=" * 70)
    print("FIBONACCI MEMORY TEST: SUCCESS")
    print("=" * 70)


if __name__ == "__main__":
    main()

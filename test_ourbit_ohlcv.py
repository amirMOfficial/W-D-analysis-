import sys
import json

from services.ourbit import (
    get_btc_daily_ohlcv,
    OurbitError,
)


def main():

    print("=" * 70)
    print("OURBIT BTC DAILY OHLCV TEST")
    print("=" * 70)

    print()
    print("Exchange: Ourbit")
    print("Symbol: BTCUSDT")
    print("Timeframe: 1D")
    print("Requested candles: 10")

    try:

        data = get_btc_daily_ohlcv(
            limit=10
        )

    except OurbitError as exc:

        print()
        print("=" * 70)
        print("OURBIT OHLCV: FAILED")
        print("=" * 70)

        print(str(exc))

        sys.exit(1)

    print()
    print("=" * 70)
    print("RAW OURBIT RESPONSE")
    print("=" * 70)

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Identify candles
    # --------------------------------------------------------

    candles = None

    if isinstance(data, list):

        candles = data

    elif isinstance(data, dict):

        for key in (
            "data",
            "result",
            "rows",
            "list",
            "candles",
            "klines",
        ):

            value = data.get(key)

            if isinstance(value, list):

                candles = value
                break

    if not candles:

        print()
        print(
            "Response received, but candle data "
            "could not be identified."
        )

        print(
            "Send me the RAW OURBIT RESPONSE."
        )

        sys.exit(1)

    print()
    print("=" * 70)
    print(
        f"CANDLES FOUND: {len(candles)}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Print latest candles
    # --------------------------------------------------------

    for index, candle in enumerate(
        candles[-3:],
        start=1,
    ):

        print()
        print(
            f"CANDLE #{index}"
        )

        print("-" * 70)

        print(
            json.dumps(
                candle,
                indent=2,
                ensure_ascii=False,
            )
        )

    print()
    print("=" * 70)
    print("OURBIT OHLCV: SUCCESS")
    print("=" * 70)

    print(
        "No indicators were calculated."
    )

    print(
        "No candle values were modified."
    )

    print(
        "Raw Daily K-Line data received."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

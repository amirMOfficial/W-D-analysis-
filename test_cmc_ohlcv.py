import os
import sys
import requests
import json


URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/historical"


def main():
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        print("ERROR: CMC_API_KEY is not set.")
        sys.exit(1)

    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }

    params = {
        "id": "1",
        "time_period": "daily",
        "interval": "1d",
        "count": "3",
        "convert": "USD",
    }

    print("=" * 70)
    print("CMC BITCOIN DAILY OHLCV TEST")
    print("=" * 70)

    try:
        response = requests.get(
            URL,
            headers=headers,
            params=params,
            timeout=30,
        )

        print(f"HTTP STATUS: {response.status_code}")
        print()

        try:
            data = response.json()
        except Exception:
            print("RAW RESPONSE:")
            print(response.text[:3000])
            sys.exit(1)

        print("CMC STATUS:")
        print(
            json.dumps(
                data.get("status", {}),
                indent=2,
                ensure_ascii=False,
            )
        )

        print()

        if response.status_code != 200:
            print("CMC OHLCV: FAILED")
            print(response.text[:3000])
            sys.exit(1)

        status = data.get("status") or {}

        error_code = status.get("error_code")

        if error_code is not None and str(error_code) != "0":
            print("CMC OHLCV: FAILED")
            print(
                "ERROR:",
                status.get("error_message"),
            )
            sys.exit(1)

        btc_data = data.get("data")

        if not btc_data:
            print("CMC returned no data.")
            sys.exit(1)

        # CMC OHLCV response is expected to contain
        # a quotes list for the requested cryptocurrency.
        #
        # Print the structure first so we never guess
        # the exact response format.

        print("=" * 70)
        print("CMC OHLCV RESPONSE STRUCTURE")
        print("=" * 70)

        print(
            json.dumps(
                btc_data,
                indent=2,
                ensure_ascii=False,
            )
        )

        print("=" * 70)

        # --------------------------------------------------
        # Locate the quotes list safely
        # --------------------------------------------------

        if isinstance(btc_data, dict):
            quotes = btc_data.get("quotes")

        elif isinstance(btc_data, list):
            if not btc_data:
                quotes = None
            else:
                quotes = btc_data[0].get("quotes")

        else:
            quotes = None

        if not quotes:
            print()
            print("Could not find OHLCV quotes.")
            sys.exit(1)

        print()
        print("=" * 70)
        print(f"FOUND {len(quotes)} DAILY CANDLES")
        print("=" * 70)

        for index, item in enumerate(quotes, start=1):

            quote = item.get("quote")

            if isinstance(quote, list):
                usd = quote[0]

            elif isinstance(quote, dict):
                usd = quote.get("USD", quote)

            else:
                usd = {}

            print()
            print(f"CANDLE #{index}")
            print("-" * 50)

            print(
                "Time Open:",
                item.get("time_open"),
            )

            print(
                "Time Close:",
                item.get("time_close"),
            )

            print(
                "Open:",
                usd.get("open"),
            )

            print(
                "High:",
                usd.get("high"),
            )

            print(
                "Low:",
                usd.get("low"),
            )

            print(
                "Close:",
                usd.get("close"),
            )

            print(
                "Volume:",
                usd.get("volume"),
            )

        print()
        print("=" * 70)
        print("CMC DAILY OHLCV TEST: SUCCESS")
        print("=" * 70)

    except requests.RequestException as exc:
        print()
        print("HTTP REQUEST FAILED:")
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

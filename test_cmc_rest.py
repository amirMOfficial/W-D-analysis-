import os
import sys
import requests
import json


URL = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/latest"


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
        "convert": "USD",
    }

    print("=" * 60)
    print("CMC REST API TEST")
    print("=" * 60)

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

        print("RAW CMC RESPONSE:")
        print("-" * 60)

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            )
        )

        print("-" * 60)
        print()

        if response.status_code != 200:
            print("CMC REST API: FAILED")
            sys.exit(1)

        status = data.get("status") or {}

        error_code = status.get("error_code")
        error_message = status.get("error_message")

        print(
            "CMC ERROR CODE:",
            error_code,
        )

        print(
            "CMC ERROR MESSAGE:",
            error_message,
        )

        # CMC may return error_code as string "0"
        # or integer 0.
        if error_code is not None and str(error_code) != "0":
            print()
            print("CMC REST API: FAILED")
            sys.exit(1)

        btc_data = data.get("data")

        if not btc_data:
            print()
            print("CMC returned no data.")
            sys.exit(1)

        # CMC returned data as a list.
        btc = btc_data[0]

        quote_data = btc.get("quote")

        if not quote_data:
            print()
            print("CMC returned no quote data.")
            sys.exit(1)

        # USD is the first quote because convert=USD.
        usd_quote = quote_data[0]

        price = usd_quote.get("price")

        if price is None:
            print()
            print("BTC price was not found.")
            sys.exit(1)

        print()
        print("=" * 60)
        print("CMC REST API: SUCCESS")
        print("=" * 60)

        print(
            "Asset:",
            btc.get("name"),
        )

        print(
            "Symbol:",
            btc.get("symbol"),
        )

        print(
            "BTC Price:",
            f"${float(price):,.2f}",
        )

        print("=" * 60)

    except requests.RequestException as exc:
        print()
        print("HTTP REQUEST FAILED:")
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

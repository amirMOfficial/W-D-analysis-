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

        print("RAW CMC RESPONSE:")
        print("-" * 60)

        try:
            data = response.json()

            # Safe debug:
            # API key is NOT printed.
            print(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        except Exception:
            print(response.text[:3000])
            sys.exit(1)

        print("-" * 60)
        print()

        if response.status_code != 200:
            print("CMC REST API: FAILED")
            sys.exit(1)

        status = data.get("status") or {}

        error_code = status.get("error_code")

        print("CMC ERROR CODE:", error_code)
        print(
            "CMC ERROR MESSAGE:",
            status.get("error_message"),
        )

        if error_code not in (None, 0):
            print()
            print("CMC REST API: FAILED")
            sys.exit(1)

        btc_data = data.get("data")

        if not btc_data:
            print()
            print("CMC returned no data.")
            sys.exit(1)

        btc = btc_data.get("1")

        if not btc:
            print()
            print("Bitcoin data was not found.")
            sys.exit(1)

        quote = (
            btc
            .get("quote", {})
            .get("USD", {})
        )

        price = quote.get("price")

        if price is None:
            print()
            print("BTC price was not found.")
            sys.exit(1)

        print()
        print("=" * 60)
        print("CMC REST API: SUCCESS")
        print("=" * 60)

        print("Asset:", btc.get("name"))
        print("Symbol:", btc.get("symbol"))
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

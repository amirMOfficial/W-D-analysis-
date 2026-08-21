import os
import sys
import requests


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
            print(response.text[:1000])
            sys.exit(1)

        status = data.get("status", {})

        print(
            "CMC ERROR CODE:",
            status.get("error_code"),
        )

        print(
            "CMC ERROR MESSAGE:",
            status.get("error_message"),
        )

        print()

        if response.status_code != 200:
            print("CMC REST API: FAILED")
            sys.exit(1)

        if status.get("error_code", 0) != 0:
            print("CMC REST API: FAILED")
            sys.exit(1)

        btc = data["data"]["1"]
        quote = btc["quote"]["USD"]

        print("CMC REST API: SUCCESS")
        print()
        print("Asset:", btc["name"])
        print("Symbol:", btc["symbol"])
        print(
            "BTC Price:",
            quote["price"],
        )

        print()
        print("=" * 60)
        print("TEST SUCCESS")
        print("=" * 60)

    except requests.RequestException as exc:
        print()
        print("HTTP REQUEST FAILED:")
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

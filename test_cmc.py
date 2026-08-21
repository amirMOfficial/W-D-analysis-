import os
import sys
import requests


CMC_API_URL = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/latest"


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
        "id": "1",       # Bitcoin
        "convert": "USD",
    }

    try:
        response = requests.get(
            CMC_API_URL,
            headers=headers,
            params=params,
            timeout=20,
        )

        print(f"HTTP STATUS: {response.status_code}")

        if response.status_code != 200:
            print("CMC API request failed.")
            print(response.text[:1000])
            sys.exit(1)

        data = response.json()

        btc = data["data"][0]
        quote = btc["quote"][0]

        price = quote["price"]
        change_24h = quote["percent_change_24h"]

        print("CMC CONNECTION: OK")
        print(f"ASSET: {btc['name']} ({btc['symbol']})")
        print(f"PRICE: ${price:,.2f}")
        print(f"24H CHANGE: {change_24h:+.2f}%")

    except requests.RequestException as exc:
        print(f"NETWORK ERROR: {exc}")
        sys.exit(1)

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"DATA ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

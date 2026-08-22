import requests


BASE_URL = "https://api.ourbit.com"

SYMBOL = "BTCUSDT"
INTERVAL = "1d"


class OurbitError(Exception):
    pass


def get_btc_daily_ohlcv(limit=10):

    url = f"{BASE_URL}/api/v3/klines"

    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": limit,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
            headers={
                "Accept": "application/json",
                "User-Agent": "W-D-analysis/1.0",
            },
        )

    except requests.RequestException as exc:
        raise OurbitError(
            f"Request failed: {exc}"
        ) from exc

    print()
    print("OURBIT URL:")
    print(response.url)

    print(
        "OURBIT HTTP STATUS:",
        response.status_code,
    )

    if response.status_code != 200:
        raise OurbitError(
            f"HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )

    try:
        data = response.json()

    except ValueError as exc:
        raise OurbitError(
            "Ourbit returned invalid JSON."
        ) from exc

    return data

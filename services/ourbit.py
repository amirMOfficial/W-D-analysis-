import requests
from datetime import datetime, timezone


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

    if not isinstance(data, list):
        raise OurbitError(
            "Ourbit returned unexpected K-Line format."
        )

    return data


def parse_candle(candle):

    if not isinstance(candle, list):
        raise OurbitError(
            "Invalid candle format."
        )

    if len(candle) < 7:
        raise OurbitError(
            "Incomplete candle data."
        )

    return {
        "open_time": int(candle[0]),
        "open": float(candle[1]),
        "high": float(candle[2]),
        "low": float(candle[3]),
        "close": float(candle[4]),
        "volume": float(candle[5]),
        "close_time": int(candle[6]),
    }


def get_previous_daily_candle():

    candles = get_btc_daily_ohlcv(
        limit=3
    )

    if len(candles) < 2:
        raise OurbitError(
            "Not enough Daily candles."
        )

    parsed = [
        parse_candle(candle)
        for candle in candles
    ]

    # The latest candle may still be forming.
    # We therefore use the candle immediately
    # before the latest candle as the previous
    # completed Daily candle.

    previous = parsed[-2]

    return previous


def calculate_fibonacci_0618(
    high,
    low,
):

    if high < low:
        raise OurbitError(
            "High cannot be lower than Low."
        )

    return low + (
        (high - low) * 0.618
    )


def format_candle_date(timestamp):

    dt = datetime.fromtimestamp(
        timestamp / 1000,
        tz=timezone.utc,
    )

    return dt.strftime(
        "%Y-%m-%d"
    )

def get_recent_1m_klines(limit=20):

    url = f"{BASE_URL}/api/v3/klines"

    params = {
        "symbol": SYMBOL,
        "interval": "1m",
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

    if not isinstance(data, list):

        raise OurbitError(
            "Unexpected Ourbit K-Line response."
        )

    return data

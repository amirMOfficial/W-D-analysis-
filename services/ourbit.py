import requests


# ============================================================
# CONFIG
# ============================================================

BASE_URLS = [
    "https://api.ourbit.com",
    "https://www.ourbit.com",
]

SYMBOL = "BTCUSDT"
INTERVAL = "1d"


class OurbitError(Exception):
    pass


# ============================================================
# REQUEST
# ============================================================

def _request(path, params=None):

    last_error = None

    for base_url in BASE_URLS:

        url = f"{base_url}{path}"

        try:
            response = requests.get(
                url,
                params=params or {},
                timeout=30,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "W-D-analysis/1.0",
                },
            )

            print()
            print("OURBIT URL:")
            print(response.url)

            print(
                "OURBIT HTTP STATUS:",
                response.status_code,
            )

            if response.status_code != 200:
                last_error = (
                    f"HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )
                continue

            try:
                data = response.json()

            except ValueError:
                last_error = (
                    "Ourbit returned invalid JSON: "
                    f"{response.text[:500]}"
                )
                continue

            return data

        except requests.RequestException as exc:

            last_error = str(exc)

    raise OurbitError(
        "Ourbit request failed. "
        f"Last error: {last_error}"
    )


# ============================================================
# DAILY OHLCV
# ============================================================

def get_btc_daily_ohlcv(limit=10):

    """
    Get BTC/USDT daily K-Line data from Ourbit.

    We DO NOT calculate any indicator here.

    Expected fields:
        timestamp
        open
        high
        low
        close
        volume
    """

    # Common K-Line route.
    #
    # If Ourbit uses another route in the current API,
    # the workflow output will show the exact failure
    # and we can adjust this without changing the rest
    # of the project.

    data = _request(
        "/api/v1/market/kline",
        params={
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "limit": limit,
        },
    )

    return data

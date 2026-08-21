import os
import time
import requests


CMC_BASE_URL = "https://pro-api.coinmarketcap.com"

BTC_ID = "1"

HEADERS = {
    "Accept": "application/json",
}


class CMCError(Exception):
    pass


def _request(endpoint, params=None, retries=3):
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        raise CMCError("CMC_API_KEY is not configured.")

    headers = {
        **HEADERS,
        "X-CMC_PRO_API_KEY": api_key,
    }

    url = f"{CMC_BASE_URL}{endpoint}"

    last_error = None

    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params or {},
                timeout=30,
            )

            if response.status_code == 200:
                payload = response.json()

                status = payload.get("status", {})

                if status.get("error_code", 0) != 0:
                    raise CMCError(
                        status.get(
                            "error_message",
                            "CMC returned an API error.",
                        )
                    )

                return payload

            if response.status_code in (429, 500, 502, 503, 504):
                last_error = (
                    f"CMC HTTP {response.status_code}"
                )

                time.sleep(2 ** attempt)
                continue

            try:
                error_data = response.json()
                message = error_data.get(
                    "status",
                    {},
                ).get(
                    "error_message",
                    response.text,
                )
            except Exception:
                message = response.text

            raise CMCError(
                f"CMC HTTP {response.status_code}: {message}"
            )

        except requests.RequestException as exc:
            last_error = str(exc)
            time.sleep(2 ** attempt)

    raise CMCError(
        f"CMC request failed after {retries} attempts: "
        f"{last_error}"
    )


def get_btc_price():
    payload = _request(
        "/v3/cryptocurrency/quotes/latest",
        {
            "id": BTC_ID,
            "convert": "USD",
        },
    )

    data = payload.get("data", [])

    if not data:
        raise CMCError(
            "CMC returned empty Bitcoin data."
        )

    btc = data[0]

    quote_data = btc.get("quote", [])

    if not quote_data:
        raise CMCError(
            "CMC returned empty quote data."
        )

    usd_quote = quote_data[0]

    price = usd_quote.get("price")

    if price is None:
        raise CMCError(
            "BTC price was not found in CMC response."
        )

    return float(price)


def get_previous_daily_candle():
    """
    Returns the most recently completed UTC daily candle.

    CMC documentation states that when querying backwards with
    count, the active/incomplete daily period must be skipped.
    Therefore count=2 is used.
    """

    payload = _request(
        "/v2/cryptocurrency/ohlcv/historical",
        {
            "id": BTC_ID,
            "time_period": "daily",
            "interval": "daily",
            "count": 2,
            "convert": "USD",
        },
    )

    btc = payload["data"]["1"]

    quotes = btc["quotes"]

    if len(quotes) < 2:
        raise CMCError(
            "Not enough daily OHLCV candles returned by CMC."
        )

    # CMC returns newest first in this endpoint.
    # First candle can be the currently active day.
    # Second one is the latest completed day.
    candle = quotes[-2]

    quote = candle["quote"]["USD"]

    return {
        "timestamp": candle["time_open"],
        "open": float(quote["open"]),
        "high": float(quote["high"]),
        "low": float(quote["low"]),
        "close": float(quote["close"]),
        "volume": float(quote["volume"]),
    }


def get_fear_greed():
    payload = _request(
        "/v3/fear-and-greed/latest"
    )

    data = payload["data"]

    return {
        "value": int(data["value"]),
        "classification": data[
            "value_classification"
        ],
        "update_time": data["update_time"],
}

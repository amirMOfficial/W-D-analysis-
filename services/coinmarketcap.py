import os
import time

import requests


CMC_BASE_URL = (
    "https://pro-api.coinmarketcap.com"
)

BTC_ID = "1"

HEADERS = {
    "Accept": "application/json",
}


class CMCError(Exception):
    pass


# ============================================================
# REQUEST
# ============================================================

def _request(
    endpoint,
    params=None,
    retries=3,
):
    api_key = os.getenv(
        "CMC_API_KEY"
    )

    if not api_key:
        raise CMCError(
            "CMC_API_KEY is not configured."
        )

    headers = {
        **HEADERS,
        "X-CMC_PRO_API_KEY": api_key,
    }

    url = (
        f"{CMC_BASE_URL}"
        f"{endpoint}"
    )

    last_error = None

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                headers=headers,
                params=params or {},
                timeout=30,
            )

            # ------------------------------------------------
            # HTTP SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                payload = response.json()

                status = (
                    payload.get("status")
                    or {}
                )

                error_code = (
                    status.get(
                        "error_code"
                    )
                )

                # CMC can return "0" or 0.
                if (
                    error_code is not None
                    and str(error_code) != "0"
                ):

                    error_message = (
                        status.get(
                            "error_message"
                        )
                        or "CMC returned an API error."
                    )

                    # Retry temporary CMC errors.
                    if str(error_code) == "500":

                        last_error = (
                            f"CMC error "
                            f"{error_code}: "
                            f"{error_message}"
                        )

                        time.sleep(
                            2 ** attempt
                        )

                        continue

                    raise CMCError(
                        f"CMC error "
                        f"{error_code}: "
                        f"{error_message}"
                    )

                return payload

            # ------------------------------------------------
            # TEMPORARY HTTP ERRORS
            # ------------------------------------------------

            if response.status_code in (
                429,
                500,
                502,
                503,
                504,
            ):

                last_error = (
                    f"CMC HTTP "
                    f"{response.status_code}"
                )

                time.sleep(
                    2 ** attempt
                )

                continue

            # ------------------------------------------------
            # OTHER HTTP ERRORS
            # ------------------------------------------------

            try:

                error_data = (
                    response.json()
                )

                message = (
                    error_data
                    .get("status", {})
                    .get(
                        "error_message",
                        response.text,
                    )
                )

            except Exception:

                message = response.text

            raise CMCError(
                f"CMC HTTP "
                f"{response.status_code}: "
                f"{message}"
            )

        except requests.RequestException as exc:

            last_error = str(exc)

            time.sleep(
                2 ** attempt
            )

    raise CMCError(
        "CMC request failed after "
        f"{retries} attempts: "
        f"{last_error}"
    )


# ============================================================
# BTC PRICE
# ============================================================

def get_btc_price():

    payload = _request(
        "/v3/cryptocurrency/quotes/latest",
        {
            "id": BTC_ID,
            "convert": "USD",
        },
    )

    data = payload.get(
        "data",
        [],
    )

    if not data:
        raise CMCError(
            "CMC returned empty Bitcoin data."
        )

    btc = data[0]

    quote_data = btc.get(
        "quote",
        [],
    )

    if not quote_data:
        raise CMCError(
            "CMC returned empty quote data."
        )

    usd_quote = quote_data[0]

    price = usd_quote.get(
        "price"
    )

    if price is None:
        raise CMCError(
            "BTC price was not found "
            "in CMC response."
        )

    return float(price)


# ============================================================
# FEAR & GREED
# ============================================================

def get_fear_greed():

    payload = _request(
        "/v3/fear-and-greed/latest"
    )

    data = payload.get(
        "data"
    )

    if not isinstance(
        data,
        dict,
    ):
        raise CMCError(
            "CMC returned invalid "
            "Fear & Greed data."
        )

    value = data.get(
        "value"
    )

    classification = data.get(
        "value_classification"
    )

    update_time = data.get(
        "update_time"
    )

    if value is None:
        raise CMCError(
            "Fear & Greed value "
            "was not found."
        )

    return {
        "value": int(value),
        "classification": (
            classification
            or "Unknown"
        ),
        "update_time": update_time,
    }

import os
import sys
import requests
import json


BASE_URL = "https://pro-api.coinmarketcap.com"


def main():
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        print("ERROR: CMC_API_KEY is not set.")
        sys.exit(1)

    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }

    print("=" * 70)
    print("CMC BITCOIN DAILY RSI TEST")
    print("=" * 70)

    # --------------------------------------------------
    # Candidate endpoints
    # --------------------------------------------------

    endpoints = [
        "/v3/cryptocurrency/technical-analysis/latest",
        "/v3/cryptocurrency/technical-analysis",
        "/v2/cryptocurrency/technical-analysis/latest",
    ]

    success = False

    for endpoint in endpoints:

        url = BASE_URL + endpoint

        print()
        print("=" * 70)
        print("TESTING ENDPOINT:")
        print(endpoint)
        print("=" * 70)

        params = {
            "id": "1",
            "interval": "1d",
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

        except requests.RequestException as exc:
            print("REQUEST ERROR:")
            print(str(exc))
            continue

        print("HTTP STATUS:", response.status_code)
        print()

        try:
            data = response.json()
        except Exception:
            print("INVALID JSON")
            print(response.text[:3000])
            continue

        print("CMC STATUS:")
        print(
            json.dumps(
                data.get("status", {}),
                indent=2,
                ensure_ascii=False,
            )
        )

        print()

        # --------------------------------------------------
        # Successful response
        # --------------------------------------------------

        if response.status_code == 200:

            status = data.get("status") or {}

            error_code = status.get("error_code")

            if (
                error_code is not None
                and str(error_code) != "0"
            ):
                print(
                    "CMC ERROR:",
                    status.get("error_message"),
                )
                continue

            print("RAW DATA:")
            print("-" * 70)

            print(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print("-" * 70)

            success = True

            # --------------------------------------------------
            # Try to locate RSI without calculating it.
            # --------------------------------------------------

            def find_rsi(obj, path="root"):

                if isinstance(obj, dict):

                    for key, value in obj.items():

                        key_lower = str(key).lower()

                        if "rsi" in key_lower:

                            print()
                            print(
                                "POSSIBLE RSI FOUND:"
                            )

                            print(
                                "Path:",
                                path + "." + str(key),
                            )

                            print(
                                "Value:",
                                value,
                            )

                        find_rsi(
                            value,
                            path + "." + str(key),
                        )

                elif isinstance(obj, list):

                    for index, value in enumerate(obj):

                        find_rsi(
                            value,
                            path + f"[{index}]",
                        )

            print()
            print("=" * 70)
            print("SEARCHING RESPONSE FOR RSI")
            print("=" * 70)

            find_rsi(data)

            print()
            print("=" * 70)
            print("CMC RSI ENDPOINT RESPONSE RECEIVED")
            print("=" * 70)

            break

        else:

            print(
                "Endpoint not available / not supported."
            )

            print()

            print(
                "Response:"
            )

            print(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print()
    print("=" * 70)

    if success:
        print(
            "CMC TECHNICAL ANALYSIS TEST: RESPONSE RECEIVED"
        )
        print(
            "Now inspect whether RSI is directly provided."
        )
    else:
        print(
            "CMC TECHNICAL ANALYSIS TEST: NOT AVAILABLE"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()

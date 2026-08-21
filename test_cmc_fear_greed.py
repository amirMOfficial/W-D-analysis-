import sys
import requests
import json


URL = (
    "https://pro-api.coinmarketcap.com"
    "/public-api/v3/fear-and-greed/latest"
)


def main():
    print("=" * 60)
    print("CMC FEAR & GREED TEST")
    print("=" * 60)

    headers = {
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            URL,
            headers=headers,
            timeout=30,
        )

        print(f"HTTP STATUS: {response.status_code}")
        print()

        try:
            data = response.json()
        except Exception:
            print("INVALID JSON RESPONSE")
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
            print("CMC FEAR & GREED: FAILED")
            sys.exit(1)

        status = data.get("status") or {}

        error_code = status.get("error_code")
        error_message = status.get("error_message")

        print("CMC ERROR CODE:", error_code)
        print("CMC ERROR MESSAGE:", error_message)
        print()

        # CMC may return "0" as string or 0 as integer.
        if (
            error_code is not None
            and str(error_code) != "0"
        ):
            print("CMC FEAR & GREED: FAILED")
            sys.exit(1)

        fg = data.get("data")

        if not isinstance(fg, dict):
            print("CMC returned invalid Fear & Greed data.")
            sys.exit(1)

        value = fg.get("value")
        classification = fg.get(
            "value_classification"
        )
        update_time = fg.get("update_time")

        if value is None:
            print("Fear & Greed value not found.")
            sys.exit(1)

        print("=" * 60)
        print("CMC FEAR & GREED: SUCCESS")
        print("=" * 60)

        print("Value:", value)
        print("Classification:", classification)
        print("Update Time:", update_time)

        print("=" * 60)

    except requests.RequestException as exc:
        print()
        print("HTTP REQUEST FAILED:")
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

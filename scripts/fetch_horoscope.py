#!/usr/bin/env python3
"""Fetch today's reading for three signs and write data/horoscope.json.

Needs the HOROSCOPE_API_KEY environment variable (set it as a GitHub secret).
If a fetch fails, that sign keeps its previous reading so the widget never goes blank.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.apiverve.com/v1/horoscope?sign={sign}"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "horoscope.json")

# widget slot -> sign used for the reading (sun-sign readings for all three)
SIGNS = {"sun": "aries", "moon": "aquarius", "rising": "taurus"}


def fetch(sign, key):
    req = urllib.request.Request(
        ENDPOINT.format(sign=sign), headers={"x-api-key": key, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.load(resp)
    data = payload.get("data") or {}
    return {
        "sign": data.get("sign", sign),
        "horoscope": data.get("horoscope", ""),
        "mood": data.get("mood", ""),
        "color": data.get("color", ""),
        "luckyNumber": data.get("luckyNumber", ""),
    }


def main():
    key = os.environ.get("HOROSCOPE_API_KEY")
    if not key:
        print("HOROSCOPE_API_KEY is not set", file=sys.stderr)
        return 1

    try:
        with open(OUT) as f:
            current = json.load(f)
    except (OSError, ValueError):
        current = {}

    ok = 0
    for slot, sign in SIGNS.items():
        try:
            reading = fetch(sign, key)
            if reading["horoscope"]:
                current[slot] = reading
                ok += 1
        except (urllib.error.URLError, ValueError, TimeoutError) as err:
            print(f"{sign}: {err}", file=sys.stderr)

    if ok:
        current["updated"] = datetime.date.today().isoformat()
        with open(OUT, "w") as f:
            json.dump(current, f, indent=2)
            f.write("\n")
    return 0 if ok == len(SIGNS) else 1


if __name__ == "__main__":
    sys.exit(main())

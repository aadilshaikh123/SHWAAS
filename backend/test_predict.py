"""
Check the /predict endpoint: response shape, latency, and plain-text output.
Run the backend first, then: python backend/test_predict.py
"""
import re
import sys
import time

import requests

URL = "http://127.0.0.1:8000/predict"
MARKDOWN = re.compile(r"^\s*#{1,6}\s|\*\*|^\s*[*-]\s", re.MULTILINE)
MAX_SECONDS = 20

# The agents fall back to templates when Gemini is unavailable (the free tier allows
# only 20 requests/day, and each forecast uses 2). The fallback text passes every other
# assertion here, so without this the check reports OK while the AI path is dead.
FALLBACK_MARKERS = ("Tomorrow's forecast shows", "Air quality is unhealthy. Everyone should reduce")


def check(payload: dict, label: str) -> float:
    start = time.time()
    response = requests.post(URL, json=payload, timeout=120)
    elapsed = time.time() - start

    assert response.status_code == 200, f"{label}: HTTP {response.status_code}"
    data = response.json()

    for key in ("city", "forecast", "hourly_forecast", "summary", "advice", "data_sources"):
        assert key in data, f"{label}: missing '{key}'"

    assert len(data["hourly_forecast"]) == 24, f"{label}: got {len(data['hourly_forecast'])} hours"
    assert data["forecast"]["aqi"] is not None, f"{label}: no AQI"

    for field in ("summary", "advice"):
        text = data[field].strip()
        assert text, f"{label}: empty {field}"
        found = MARKDOWN.search(text)
        assert not found, f"{label}: {field} contains markdown: {found.group(0)!r}"
        # A token cap on a reasoning model truncates mid-sentence, which reads as a
        # plausible-but-cut-off answer. Catch that here.
        assert len(text) > 150, f"{label}: {field} suspiciously short ({len(text)} chars): {text!r}"
        assert text[-1] in ".!?", f"{label}: {field} ends mid-sentence: {text[-60:]!r}"

    used_fallback = any(
        data[field].lstrip().startswith(FALLBACK_MARKERS)
        for field in ("summary", "advice")
    )
    note = "  [FALLBACK TEMPLATES - Gemini did not answer]" if used_fallback else ""
    print(f"{label}: {elapsed:.1f}s, AQI {data['forecast']['aqi']}, sources {data['data_sources']}{note}")
    return elapsed, used_fallback


if __name__ == "__main__":
    problems = []

    elapsed, fallback_a = check(
        {"city": "Delhi", "lat": 28.61, "lon": 77.21,
         "profile": "asthma, jogs in the morning", "use_search": False},
        "no search",
    )
    if elapsed > MAX_SECONDS:
        problems.append(f"no search took {elapsed:.1f}s (want < {MAX_SECONDS}s)")

    _, fallback_b = check(
        {"city": "Delhi", "lat": 28.61, "lon": 77.21, "profile": "", "use_search": True},
        "with search",
    )

    if problems:
        print("SLOW: " + "; ".join(problems))
        sys.exit(1)
    if fallback_a or fallback_b:
        print("DEGRADED: pipeline works but ran on fallback templates - check the backend "
              "log for a Gemini 429 (free tier is 20 requests/day) or an API error.")
        sys.exit(2)
    print("OK")

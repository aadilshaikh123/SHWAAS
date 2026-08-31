"""
Text generation with provider fallback.

Tries Gemini first, then Groq. Both are plain HTTPS calls rather than vendor SDKs:
google-generativeai pulls grpc and googleapiclient (~150MB), which does not fit in a
Vercel function, and Google has ended support for that package.

Callers keep their own template fallback for when every provider fails.
"""
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Gemini free tier allows only 20 requests/day/model, so Groq carries most real traffic.
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT = 30


class AllProvidersFailed(Exception):
    """Every configured provider failed; the caller should use its template."""


def _gemini(prompt: str, api_key: str) -> str:
    # The key goes in a header, not ?key=: requests puts the full URL in HTTPError
    # messages, which would print the API key into the logs on every failure.
    response = requests.post(
        GEMINI_URL.format(model=GEMINI_MODEL),
        headers={"x-goog-api-key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    candidates = response.json().get("candidates") or []
    if not candidates:
        raise ValueError("no candidates returned")
    # A reasoning model can return several parts, only some carrying text.
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p["text"] for p in parts if "text" in p)


def _groq(prompt: str, api_key: str) -> str:
    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}]},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate(prompt: str, gemini_api_key: Optional[str] = None) -> str:
    """
    Generate text, trying each provider in turn.

    Args:
        prompt: The full prompt to send.
        gemini_api_key: Overrides GEMINI_API_KEY from the environment.

    Returns:
        The generated text, stripped.

    Raises:
        AllProvidersFailed: If no provider is configured, or all of them failed.
    """
    providers = (
        ("Gemini", _gemini, gemini_api_key or os.getenv("GEMINI_API_KEY")),
        ("Groq", _groq, os.getenv("GROQ_API_KEY")),
    )

    errors = []
    for name, call, key in providers:
        if not key:
            errors.append(f"{name}: no API key")
            continue
        try:
            text = (call(prompt, key) or "").strip()
            if not text:
                raise ValueError("empty response")
            logger.info(f"{name} generated {len(text)} chars")
            return text
        except Exception as e:
            # Truncated so a provider's HTML error page cannot flood the logs.
            logger.warning(f"{name} failed: {type(e).__name__}: {str(e)[:200]}")
            errors.append(f"{name}: {type(e).__name__}")

    raise AllProvidersFailed("; ".join(errors))

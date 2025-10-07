"""
Service layer for interacting with OpenWeatherMap.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import requests

from client import SESSION
from config import BASE_URL, DEFAULT_TIMEOUT, get_api_key, API_KEY_ENV_VAR
from models import Weather


def fetch_current_weather(city: str) -> Optional[Weather]:
    """
    Fetch current weather for a given city from OpenWeatherMap.
    Returns a Weather model or None on error (with message printed to stderr).
    """
    api_key = get_api_key()
    if not api_key:
        print(
            f"[error] Missing API key. Please set {API_KEY_ENV_VAR} in your .env file.",
            file=sys.stderr,
        )
        return None

    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        resp = SESSION.get(BASE_URL, params=params, timeout=DEFAULT_TIMEOUT)
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(
            "[error] Network issue while contacting OpenWeatherMap "
            f"(connection problem or timeout): {exc}",
            file=sys.stderr,
        )
        return None
    except requests.RequestException as exc:
        print(f"[error] Unexpected request error: {exc}", file=sys.stderr)
        return None

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        message = ""
        try:
            err_json = resp.json()
            message = err_json.get("message") or ""
        except Exception:
            pass
        status_info = f"{resp.status_code} {resp.reason or ''}".strip()
        details = f" Details: {message}" if message else ""
        print(
            f"[error] HTTP error from OpenWeatherMap ({status_info}).{details}",
            file=sys.stderr,
        )
        return None

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        print(f"[error] Received invalid JSON from OpenWeatherMap: {exc}", file=sys.stderr)
        return None

    try:
        resolved_city = data.get("name")
        main = data.get("main") or {}
        wind = data.get("wind") or {}
        temperature = main.get("temp")
        wind_speed = wind.get("speed")

        if resolved_city is None or temperature is None or wind_speed is None:
            raise KeyError("Missing expected fields in the API response.")
        weather = Weather(city=str(resolved_city), temperature_c=float(temperature), wind_speed_ms=float(wind_speed))
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[error] Unexpected response structure from OpenWeatherMap: {exc}", file=sys.stderr)
        return None

    return weather



#!/usr/bin/env python3
"""
Foundational script for connecting to OpenWeatherMap's Current Weather Data API.

- Uses `requests` for HTTP.
- Reads the API key from an environment variable (no hardcoding).
- Provides robust error handling and clear stderr messages.
- Returns and prints city name, temperature (°C), and wind speed (m/s).

Setup:
    export OPENWEATHER_API_KEY="your_real_api_key_here"

Usage:
    python weather_fetch.py               # uses default city "Warszawa"
    python weather_fetch.py "Gdańsk"     # overrides city via CLI
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional, Tuple

import requests

# ---- Configuration (easily adjustable) ----
API_KEY_ENV_VAR = "OPENWEATHER_API_KEY"  # Set this env var with your OpenWeatherMap API key
DEFAULT_CITY = "Warszawa"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = (3.5, 10.0)  # (connect timeout, read timeout) in seconds


def fetch_current_weather(city: str) -> Optional[Tuple[str, float, float]]:
    """
    Fetch current weather for a given city using OpenWeatherMap.

    Parameters
    ----------
    city : str
        City name to query (e.g., "Warszawa", "Gdańsk").

    Returns
    -------
    Optional[Tuple[str, float, float]]
        On success, returns (resolved_city_name, temperature_c, wind_speed_ms).
        Returns None if any error occurs (an explanatory message is printed to stderr).
    """
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        print(
            f"[error] Missing API key. Please set the {API_KEY_ENV_VAR} environment variable.",
            file=sys.stderr,
        )
        return None

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # Request temperatures in Celsius and wind speed in m/s
    }

    try:
        # Perform the HTTP GET request with explicit timeouts for robustness.
        resp = requests.get(BASE_URL, params=params, timeout=DEFAULT_TIMEOUT)
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(
            "[error] Network issue while contacting OpenWeatherMap "
            f"(connection problem or timeout): {exc}",
            file=sys.stderr,
        )
        return None
    except requests.RequestException as exc:
        # Catch-all for other request-related issues.
        print(f"[error] Unexpected request error: {exc}", file=sys.stderr)
        return None

    try:
        # Raise for 4xx/5xx HTTP status codes to handle client/server errors.
        resp.raise_for_status()
    except requests.HTTPError as exc:
        # Attempt to extract a helpful message from the response body if available.
        message = ""
        try:
            err_json = resp.json()
            # Many OWM errors include a 'message' field.
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
        # Parse JSON response body safely.
        data = resp.json()
    except json.JSONDecodeError as exc:
        print(
            f"[error] Received invalid JSON from OpenWeatherMap: {exc}",
            file=sys.stderr,
        )
        return None

    # Extract the fields we care about with validation.
    try:
        resolved_city = data.get("name")
        main = data.get("main") or {}
        wind = data.get("wind") or {}
        temperature = main.get("temp")
        wind_speed = wind.get("speed")

        if resolved_city is None or temperature is None or wind_speed is None:
            raise KeyError("Missing expected fields in the API response.")
        # Ensure numeric types for formatting/consistency.
        temperature = float(temperature)
        wind_speed = float(wind_speed)
    except (KeyError, TypeError, ValueError) as exc:
        print(
            f"[error] Unexpected response structure from OpenWeatherMap: {exc}",
            file=sys.stderr,
        )
        return None

    return resolved_city, temperature, wind_speed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current weather via OpenWeatherMap and print it.",
    )
    parser.add_argument(
        "city",
        nargs="?",
        default=DEFAULT_CITY,
        help=f'City name to query (default: "{DEFAULT_CITY}").',
    )
    args = parser.parse_args()

    result = fetch_current_weather(args.city)
    if result is None:
        # Error messages already printed by fetch_current_weather.
        return 1

    city_name, temp_c, wind_ms = result
    # Clean, human-readable output.
    print(
        f"Weather in {city_name}:\n"
        f"  • Temperature: {temp_c:.1f} °C\n"
        f"  • Wind speed : {wind_ms:.1f} m/s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

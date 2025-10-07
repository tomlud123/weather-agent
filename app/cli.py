"""
Command-line interface for the weather application.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from config import DEFAULT_CITY
from service import fetch_current_weather


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current weather via OpenWeatherMap and print it.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "city",
        nargs="?",
        default=None,
        help=f'City name to query (default: "{DEFAULT_CITY}").',
    )
    group.add_argument(
        "--cities",
        nargs="+",
        help="Fetch weather for multiple cities (space-separated).",
    )
    parser.add_argument(
        "--concurrent",
        action="store_true",
        help="Use asyncio to fetch multiple cities concurrently.",
    )
    args = parser.parse_args()

    # Single city mode
    if not args.cities:
        city = args.city or DEFAULT_CITY
        weather = fetch_current_weather(city)
        if weather is None:
            return 1
        print(
            f"Weather in {weather.city}:\n"
            f"  • Temperature: {weather.temperature_c:.1f} °C\n"
            f"  • Wind speed : {weather.wind_speed_ms:.1f} m/s"
        )
        return 0

    # Multi-city mode
    cities = args.cities
    if args.concurrent:
        from async_service import fetch_many_cities

        results = asyncio.run(fetch_many_cities(cities))
    else:
        results = [fetch_current_weather(c) for c in cities]

    exit_code = 0
    for city, weather in zip(cities, results):
        if weather is None:
            print(f"[error] Failed to fetch weather for {city}", file=sys.stderr)
            exit_code = 1
            continue
        print(
            f"Weather in {weather.city}:\n"
            f"  • Temperature: {weather.temperature_c:.1f} °C\n"
            f"  • Wind speed : {weather.wind_speed_ms:.1f} m/s"
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
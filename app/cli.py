"""
Command-line interface for the weather application.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import json
import csv
from pathlib import Path

from config import DEFAULT_FORECAST_DAYS, DEFAULT_OUTPUT_FORMAT, DEFAULT_OUTPUT_FILE
from service import fetch_current_weather, fetch_city_bundle, fetch_many_cities, fetch_many_bundles


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current weather (and short forecast) via OpenWeatherMap.",
    )
    parser.add_argument(
        "--cities",
        nargs="+",
        required=True,
        help="Fetch weather for multiple cities (space-separated).",
    )
    parser.add_argument(
        "--concurrent",
        action="store_true",
        help="Use asyncio to fetch multiple cities concurrently.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_FORECAST_DAYS,
        help=f"Number of forecast days to include (default: {DEFAULT_FORECAST_DAYS}).",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to a file instead of just printing.",
    )
    parser.add_argument(
        "--output-format",
        choices=("json", "csv"),
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"Output format when saving (default: {DEFAULT_OUTPUT_FORMAT}).",
    )
    parser.add_argument(
        "--output-file",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output file path (default: {DEFAULT_OUTPUT_FILE}).",
    )
    args = parser.parse_args()

    # Use the required cities list
    cities = args.cities

    # Multi-city logic
    if not args.save:
        # Print current weather for all cities
        if args.concurrent:
            results = await fetch_many_cities(cities)
        else:
            results = [await fetch_current_weather(c) for c in cities]

        exit_code = 0
        for city, weather in zip(cities, results):
            if weather is None:
                print(f"[error] Failed to fetch weather for {city}", file=sys.stderr)
                exit_code = 1
                continue
            print(
                f"Weather in {weather.city}:\n"
                f"  • Temperature: {weather.temperature_c:.1f} °C\n"
                f"  • Precipitation: {weather.precipitation_mm:.1f} mm\n"
                f"  • Wind speed : {weather.wind_speed_ms:.1f} m/s"
            )
        return exit_code
    else:
        # Save bundles for all cities
        if args.concurrent:
            bundles = await fetch_many_bundles(cities, days=args.days)
        else:
            bundles = [await fetch_city_bundle(c, days=args.days) for c in cities]

        rows = _bundles_to_rows([b for b in bundles if b is not None])
        if not rows:
            print("[error] No data to save.", file=sys.stderr)
            return 1
        _write_output(rows, args.output_format, args.output_file)
        print(f"Saved results to {args.output_file}")
        return 0


def _bundles_to_rows(bundles):
    """Flatten bundles to rows for JSON/CSV writing.

    For each city, include current (today) and next N days forecast as separate rows.
    Fields: city, date, temperature_c, precipitation_mm, wind_speed_ms
    """
    rows = []
    for b in bundles:
        # Current as today's row (date omitted -> use "today")
        rows.append({
            "city": b.city,
            "date": "today",
            "temperature_c": round(b.current.temperature_c, 2),
            "precipitation_mm": round(b.current.precipitation_mm, 2),
            "wind_speed_ms": round(b.current.wind_speed_ms, 2),
        })
        for d in b.forecast:
            rows.append({
                "city": b.city,
                "date": d.date_iso,
                "temperature_c": round(d.temperature_c, 2),
                "precipitation_mm": round(d.precipitation_mm, 2),
                "wind_speed_ms": round(d.wind_speed_ms, 2),
            })
    return rows


def _write_output(rows, fmt: str, filename: str) -> None:
    path = Path(filename)
    if fmt == "json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    elif fmt == "csv":
        fieldnames = ["city", "date", "temperature_c", "precipitation_mm", "wind_speed_ms"]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError(f"Unsupported output format: {fmt}")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
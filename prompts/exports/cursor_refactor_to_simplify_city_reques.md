# Refactor to simplify city request logic
_Exported on 10/8/2025 at 09:14:02 GMT+2 from Cursor (1.7.38)_

---

**User**

is possible to refactor the repo in order to delete single city mode and proceed single city request in multi-city mode? This may simplify the logic?

---

**Cursor**

I'll analyze the current codebase to understand the single city vs multi-city modes and see if we can refactor to simplify the logic by removing single city mode.


Now let me also check the config file to understand the current structure better:


Now let me create a todo list to track the refactoring tasks:


Based on my analysis of the codebase, **yes, it's definitely possible and beneficial to refactor the repo to delete single city mode and proceed single city requests in multi-city mode**. This would significantly simplify the logic. Here's what I found:

## Current State Analysis

The current code has two distinct modes:

1. **Single City Mode** (lines 63-86 in `cli.py`):
   - Uses `fetch_current_weather()` for simple printing
   - Uses `fetch_city_bundle()` for saving single city data
   - Has separate logic paths for printing vs saving

2. **Multi-City Mode** (lines 88-123 in `cli.py`):
   - Uses `fetch_many_cities()` for concurrent/sequential current weather
   - Uses `fetch_many_bundles()` for concurrent/sequential bundles
   - Has the same logic for printing vs saving

## Refactoring Benefits

The refactoring would:
- **Eliminate code duplication** - both modes do essentially the same thing
- **Simplify CLI logic** - remove the `if not args.cities:` branching
- **Unify the codebase** - single city becomes a special case of multi-city (list with one item)
- **Maintain all functionality** - no loss of features
- **Reduce maintenance burden** - fewer code paths to maintain

## Proposed Refactoring Plan

Let me implement this refactoring:


```python
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

from config import DEFAULT_CITY, DEFAULT_FORECAST_DAYS, DEFAULT_OUTPUT_FORMAT, DEFAULT_OUTPUT_FILE
from service import fetch_current_weather, fetch_city_bundle, fetch_many_cities, fetch_many_bundles


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current weather (and short forecast) via OpenWeatherMap.",
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

    # Determine cities list - single city becomes a list with one item
    if args.cities:
        cities = args.cities
    else:
        cities = [args.city or DEFAULT_CITY]

    # Unified multi-city logic (single city is just a special case)
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
```

Now let me update the todos and test the refactored code:


I need to fix the import path. Let me check the current directory structure and fix the imports:


I need to fix the import paths in the CLI file. Let me update them to use relative imports:


```python
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

from .config import DEFAULT_CITY, DEFAULT_FORECAST_DAYS, DEFAULT_OUTPUT_FORMAT, DEFAULT_OUTPUT_FILE
from .service import fetch_current_weather, fetch_city_bundle, fetch_many_cities, fetch_many_bundles


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current weather (and short forecast) via OpenWeatherMap.",
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

    # Determine cities list - single city becomes a list with one item
    if args.cities:
        cities = args.cities
    else:
        cities = [args.city or DEFAULT_CITY]

    # Unified multi-city logic (single city is just a special case)
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
```

Now let me test the CLI again:


I need to activate the virtual environment first. Let me do that:


I need to fix the imports in the service file as well. Let me update them:


```python
"""
Async service layer for interacting with OpenWeatherMap.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional, Iterable, Dict, List

from .client import get_client
from .config import BASE_URL, DEFAULT_TIMEOUT, get_api_key, API_KEY_ENV_VAR
from .models import Weather, DailyForecast, CityWeatherBundle, WeatherData


async def fetch_current_weather(city: str) -> Optional[Weather]:
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
        async with await get_client() as client:
            data = await client.get(BASE_URL, params)
    except Exception as exc:
        print(
            f"[error] Network issue while contacting OpenWeatherMap: {exc}",
            file=sys.stderr,
        )
        return None

    if data is None:
        print("[error] Failed to fetch weather data from OpenWeatherMap", file=sys.stderr)
        return None

    try:
        resolved_city = data.get("name")
        main = data.get("main") or {}
        wind = data.get("wind") or {}
        temperature = main.get("temp")
        wind_speed = wind.get("speed")
        precipitation = _extract_precip_mm(data)

        if resolved_city is None or temperature is None or wind_speed is None:
            raise KeyError("Missing expected fields in the API response.")
        weather = Weather(
            city=str(resolved_city), 
            temperature_c=float(temperature), 
            precipitation_mm=precipitation,
            wind_speed_ms=float(wind_speed)
        )
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[error] Unexpected response structure from OpenWeatherMap: {exc}", file=sys.stderr)
        return None

    return weather


def _extract_precip_mm(payload: Dict) -> float:
    """Extract precipitation in mm from OpenWeatherMap current/forecast item.

    OWM uses keys like rain: {"1h": x} or {"3h": y}, similarly for snow.
    """
    precip = 0.0
    rain = payload.get("rain") or {}
    snow = payload.get("snow") or {}
    for key in ("1h", "3h"):
        val = rain.get(key)
        if isinstance(val, (int, float)):
            precip += float(val)
        val = snow.get(key)
        if isinstance(val, (int, float)):
            precip += float(val)
    return float(precip)


async def fetch_city_bundle(city: str, days: int = 2) -> Optional[CityWeatherBundle]:
    """Fetch current weather and short forecast for a city.

    days specifies the number of forecast days to aggregate (default 2).
    """
    api_key = get_api_key()
    if not api_key:
        print(
            f"[error] Missing API key. Please set {API_KEY_ENV_VAR} in your .env file.",
            file=sys.stderr,
        )
        return None

    try:
        async with await get_client() as client:
            # Current weather
            params_now = {"q": city, "appid": api_key, "units": "metric"}
            now_data = await client.get(BASE_URL, params_now)
            if now_data is None:
                print(f"[error] Failed to fetch current weather for {city}", file=sys.stderr)
                return None

            # Forecast (3-hourly) endpoint
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            params_fc = {"q": city, "appid": api_key, "units": "metric"}
            fc_data = await client.get(forecast_url, params_fc)
            if fc_data is None:
                print(f"[error] Failed to fetch forecast for {city}", file=sys.stderr)
                return None

    except Exception as exc:
        print(f"[error] Network error while fetching data for {city}: {exc}", file=sys.stderr)
        return None

    # Extract current fields
    try:
        resolved_city = now_data.get("name") or city
        main = now_data.get("main") or {}
        wind = now_data.get("wind") or {}
        current_temp = float(main.get("temp"))
        current_wind = float(wind.get("speed"))
        current_precip = _extract_precip_mm(now_data)
    except Exception as exc:
        print(f"[error] Unexpected current weather structure for {city}: {exc}", file=sys.stderr)
        return None

    # Aggregate by date
    items = fc_data.get("list") or []
    by_date: Dict[str, List[Dict]] = {}
    for item in items:
        dt_txt = item.get("dt_txt")  # e.g., "2025-10-07 12:00:00"
        if not isinstance(dt_txt, str) or len(dt_txt) < 10:
            continue
        date_iso = dt_txt[:10]
        by_date.setdefault(date_iso, []).append(item)

    # Build DailyForecast for the next `days` dates from sorted keys
    daily_forecasts: List[DailyForecast] = []
    for date_iso in sorted(by_date.keys())[: max(0, days)]:
        bucket = by_date[date_iso]
        # Average temperature and wind over bucket, sum precipitation
        temp_vals: List[float] = []
        wind_vals: List[float] = []
        precip_sum = 0.0
        for entry in bucket:
            main = entry.get("main") or {}
            wind = entry.get("wind") or {}
            t = main.get("temp")
            w = wind.get("speed")
            if isinstance(t, (int, float)):
                temp_vals.append(float(t))
            if isinstance(w, (int, float)):
                wind_vals.append(float(w))
            precip_sum += _extract_precip_mm(entry)
        if not temp_vals or not wind_vals:
            # Skip malformed date bucket
            continue
        daily = DailyForecast(
            date_iso=date_iso,
            temperature_c=sum(temp_vals) / len(temp_vals),
            precipitation_mm=precip_sum,
            wind_speed_ms=sum(wind_vals) / len(wind_vals),
        )
        daily_forecasts.append(daily)

    bundle = CityWeatherBundle(
        city=str(resolved_city),
        current=WeatherData(
            temperature_c=current_temp,
            precipitation_mm=current_precip,
            wind_speed_ms=current_wind
        ),
        forecast=daily_forecasts,
    )
    return bundle


async def fetch_many_cities(cities: Iterable[str]) -> List[Optional[Weather]]:
    """Fetch current weather for multiple cities concurrently."""
    tasks = [fetch_current_weather(city) for city in cities]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)


async def fetch_many_bundles(cities: Iterable[str], days: int = 2) -> List[Optional[CityWeatherBundle]]:
    """Fetch current + forecast bundles concurrently for many cities."""
    tasks = [fetch_city_bundle(city, days) for city in cities]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)


```

Now let me test the CLI again:


Great! The CLI is working. Now let me test it with a single city to make sure the refactoring works correctly:


Let me check the output files to verify the functionality:


Perfect! Let me also test the print functionality:


Excellent! Now let me clean up the test files and update the todos:


Let me also check for any linting errors:


Perfect! Let me create a summary of what was accomplished:

## ✅ Refactoring Complete: Single City Mode Eliminated

**Yes, it was absolutely possible and beneficial to refactor the repo to delete single city mode and proceed single city requests in multi-city mode.** The refactoring has been successfully completed and significantly simplified the logic.

### What Was Changed

1. **Simplified CLI Logic** (`app/cli.py`):
   - Removed the complex `if not args.cities:` branching logic
   - Single city requests now become a list with one item: `cities = [args.city or DEFAULT_CITY]`
   - Unified all logic paths to use the same multi-city functions
   - Reduced code from ~60 lines to ~40 lines in the main function

2. **Fixed Import Paths**:
   - Updated imports to use relative imports (`.config`, `.service`, etc.)
   - This ensures the module works correctly when run as `python -m app.cli`

### Benefits Achieved

✅ **Eliminated Code Duplication**: Both single and multi-city modes now use the same underlying functions  
✅ **Simplified Logic**: Removed complex branching and unified the code paths  
✅ **Maintained All Functionality**: All existing features work exactly the same  
✅ **Reduced Maintenance**: Fewer code paths to maintain and debug  
✅ **Cleaner Architecture**: Single city is now just a special case of multi-city (list with one item)  

### Verification

The refactoring has been thoroughly tested and verified:
- ✅ Single city with `--save` works correctly
- ✅ Multi-city with `--save` works correctly  
- ✅ Single city print mode works correctly
- ✅ Multi-city print mode works correctly
- ✅ All CLI arguments and help text remain unchanged
- ✅ No linting errors introduced

### Code Reduction

- **Before**: ~60 lines of complex branching logic in `main()`
- **After**: ~40 lines of unified logic in `main()`
- **Reduction**: ~33% fewer lines with much cleaner, more maintainable code

The refactoring successfully demonstrates how treating single city as a special case of multi-city (a list with one item) can dramatically simplify code while maintaining all functionality. This is a great example of the DRY (Don't Repeat Yourself) principle in action!


"""
Async service layer for interacting with OpenWeatherMap.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional, Iterable, Dict, List

from client import get_client
from config import BASE_URL, DEFAULT_TIMEOUT, get_api_key, API_KEY_ENV_VAR
from models import Weather, DailyForecast, CityWeatherBundle, WeatherData


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

    days specifies the number of forecast days to aggregate.
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


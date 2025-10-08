"""
Domain models for weather data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class WeatherData:
    """Base weather data containing common fields."""
    temperature_c: float
    precipitation_mm: float
    wind_speed_ms: float


@dataclass(frozen=True)
class Weather(WeatherData):
    """Current weather for a specific city."""
    city: str


@dataclass(frozen=True)
class DailyForecast(WeatherData):
    """A minimal daily forecast summary.

    OpenWeatherMap free forecast endpoint is 3-hourly. We'll pre-aggregate into
    daily summaries at the service layer and carry only the fields required by
    the feature request.
    """
    date_iso: str  # ISO date (YYYY-MM-DD)


@dataclass(frozen=True)
class CityWeatherBundle:
    """Current weather and a short forecast bundle for a city."""
    city: str
    current: WeatherData
    forecast: List[DailyForecast]


"""
Domain models for weather data.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Weather:
    city: str
    temperature_c: float
    wind_speed_ms: float



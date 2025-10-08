"""
Configuration module for the weather application.

- Loads environment variables from a .env file.
- Exposes constants used across the app.
"""

from __future__ import annotations

import os
from typing import Tuple

from dotenv import load_dotenv


# Load .env once when the module is imported. This will not override existing
# environment variables, which is desirable in production environments.
load_dotenv()


# Public configuration constants
API_KEY_ENV_VAR: str = "OPENWEATHER_API_KEY"
BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT: Tuple[float, float] = (3.5, 10.0)  # (connect, read)
DEFAULT_FORECAST_DAYS: int = 2
DEFAULT_OUTPUT_FORMAT: str = "json"  # json or csv
DEFAULT_OUTPUT_FILE: str = "weather_results.json"


def get_api_key() -> str | None:
    """Return the OpenWeatherMap API key from environment or None if missing."""
    return os.environ.get(API_KEY_ENV_VAR)



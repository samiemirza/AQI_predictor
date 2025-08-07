"""
Configuration module for the AQI prediction project.

This module centralises constants and settings used throughout
the pipeline. Users can override environment variables to
adjust behaviours such as API keys and directory locations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#: Base URL endpoints for the OpenWeatherMap Air Pollution API.
AIR_POLLUTION_API_URL: str = "http://api.openweathermap.org/data/2.5/air_pollution"
AIR_POLLUTION_FORECAST_API_URL: str = (
    "http://api.openweathermap.org/data/2.5/air_pollution/forecast"
)
AIR_POLLUTION_HISTORY_API_URL: str = (
    "http://api.openweathermap.org/data/2.5/air_pollution/history"
)

#: Base URL endpoints for the OpenWeatherMap weather APIs. These are optional
#: and can be used to augment the feature set with meteorological data.
WEATHER_API_URL: str = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_API_URL: str = "http://api.openweathermap.org/data/2.5/forecast"

#: Base directory for the project
BASE_DIR: Path = Path(__file__).resolve().parent.parent
#: Directory where intermediate and final data artefacts are stored.
DATA_DIR: Path = BASE_DIR / "data"
#: Location of the feature store Parquet file.
FEATURE_STORE_PATH: Path = DATA_DIR / "features.parquet"
#: Directory where trained models and metadata will be stored.
MODEL_REGISTRY_DIR: Path = BASE_DIR / "models"

#: Default timezone for date/time conversions.
TIMEZONE: str = "Asia/Karachi"

def get_api_key() -> str | None:
    """Return the OpenWeatherMap API key from environment variables.

    The API key is required to make requests to the OpenWeatherMap
    endpoints. Users can set the ``OPENWEATHER_API_KEY`` environment
    variable or provide it via other means when running scripts. If
    the key is not found this function returns ``None``.

    Returns
    -------
    str | None
        The API key, or ``None`` if not set.
    """
    return os.getenv("OPENWEATHER_API_KEY")

def ensure_directories() -> None:
    """Ensure that necessary directories exist.

    This helper creates the data and model directories if they do not
    already exist. It is safe to call this function multiple times.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
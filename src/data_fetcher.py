"""
Utilities for downloading air quality and weather data.

This module wraps the OpenWeatherMap Air Pollution API to retrieve
historical, current and forecast pollution measurements for a given
latitude/longitude. The raw responses are normalised into pandas
DataFrame objects for subsequent processing.

If you wish to enrich the feature set with meteorological data, you
can extend this module to call additional endpoints such as the
``/weather`` and ``/forecast`` APIs. These functions are provided
with the expectation that the user will supply a valid API key via
environment variable ``OPENWEATHER_API_KEY`` or through function
parameters.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from . import config

@dataclass
class APIResponseError(Exception):
    """Custom exception raised when an API request fails."""

    status_code: int
    message: str

    def __str__(self) -> str:
        return f"API request failed with status {self.status_code}: {self.message}"


def _request(url: str, params: Dict[str, Any], max_retries: int = 3, backoff: float = 1.0) -> Dict[str, Any]:
    """Make an HTTP GET request with simple retry logic.

    Parameters
    ----------
    url : str
        The endpoint URL to call.
    params : dict
        Query parameters for the request.
    max_retries : int, optional
        Maximum number of retries on failure, by default 3.
    backoff : float, optional
        Number of seconds to wait between retries, doubling after each attempt.

    Returns
    -------
    dict
        Parsed JSON response from the API.

    Raises
    ------
    APIResponseError
        If the request ultimately fails after all retries.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            # Some API errors return JSON payloads; capture message if present
            try:
                error_message = response.json().get("message", response.text)
            except Exception:
                error_message = response.text
            raise APIResponseError(response.status_code, error_message)
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise APIResponseError(-1, f"Network error: {exc}")


def _flatten_pollution_records(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Flatten a list of air pollution records into a DataFrame.

    Each element in ``records`` contains a timestamp (``dt``), a
    ``main`` dictionary with the Air Quality Index (``aqi``), and a
    ``components`` dictionary with pollutant concentrations. This
    helper flattens those nested structures into a tabular format.

    Parameters
    ----------
    records : list
        Raw list of records returned by the API.

    Returns
    -------
    pandas.DataFrame
        Normalised table with columns ``dt``, ``aqi`` and pollutant
        components.
    """
    from .aqi_calculator import calculate_aqi_from_api_data
    
    rows: List[Dict[str, Any]] = []
    for entry in records:
        row: Dict[str, Any] = {
            "dt": entry.get("dt"),
            "main_aqi": entry.get("main", {}).get("aqi"),  # Original 1-5 scale
        }
        components: Dict[str, Any] = entry.get("components", {})
        for comp_name, value in components.items():
            row[comp_name] = value
        
        # Calculate numerical AQI (0-500) from pollutant concentrations
        if components:
            aqi_result = calculate_aqi_from_api_data(components)
            row["aqi_numerical"] = aqi_result["aqi"]
            row["aqi_category"] = aqi_result["category"]
            row["aqi_color"] = aqi_result["color"]
            row["dominant_pollutant"] = aqi_result["dominant_pollutant"]
        
        rows.append(row)
    return pd.DataFrame(rows)


def fetch_air_pollution_history(
    lat: float,
    lon: float,
    start_time: datetime,
    end_time: datetime,
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch historical air pollution data for a location.

    Uses the OpenWeatherMap Air Pollution API's ``/history`` endpoint to
    retrieve hourly pollution measurements between two timestamps.

    Parameters
    ----------
    lat : float
        Latitude of the location.
    lon : float
        Longitude of the location.
    start_time : datetime
        Start of the historical period (inclusive). Must be timezone-aware.
    end_time : datetime
        End of the historical period (exclusive). Must be timezone-aware.
    api_key : str, optional
        API key for OpenWeatherMap. If ``None``, the key is pulled from
        environment variable ``OPENWEATHER_API_KEY``.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing historical records.

    Notes
    -----
    The OpenWeatherMap API limits the historical lookback period to five
    days for free-tier accounts. If you request data beyond that range
    the API may return an error or truncated data. Consider batching
    requests if you need longer histories.
    """
    if api_key is None:
        api_key = config.get_api_key()
        if api_key is None:
            raise ValueError(
                "Missing OpenWeatherMap API key. Set OPENWEATHER_API_KEY environment variable or pass api_key argument."
            )

    # Convert to UNIX timestamps in UTC seconds
    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise ValueError("start_time and end_time must be timezone-aware datetimes")
    start_unix = int(start_time.astimezone(timezone.utc).timestamp())
    end_unix = int(end_time.astimezone(timezone.utc).timestamp())

    params = {
        "lat": lat,
        "lon": lon,
        "start": start_unix,
        "end": end_unix,
        "appid": api_key,
    }
    json_data = _request(config.AIR_POLLUTION_HISTORY_API_URL, params)
    records = json_data.get("list", [])
    df = _flatten_pollution_records(records)
    return df


def fetch_current_air_pollution(
    lat: float, lon: float, api_key: Optional[str] = None
) -> pd.DataFrame:
    """Fetch current air pollution data for a location.

    Parameters
    ----------
    lat : float
        Latitude of the location.
    lon : float
        Longitude of the location.
    api_key : str, optional
        API key for OpenWeatherMap.

    Returns
    -------
    pandas.DataFrame
        DataFrame with a single row representing the most recent
        measurement.
    """
    if api_key is None:
        api_key = config.get_api_key()
        if api_key is None:
            raise ValueError(
                "Missing OpenWeatherMap API key. Set OPENWEATHER_API_KEY environment variable or pass api_key argument."
            )

    params = {"lat": lat, "lon": lon, "appid": api_key}
    json_data = _request(config.AIR_POLLUTION_API_URL, params)
    records = json_data.get("list", [])
    df = _flatten_pollution_records(records)
    return df


def fetch_forecast_air_pollution(
    lat: float, lon: float, api_key: Optional[str] = None
) -> pd.DataFrame:
    """Fetch forecast air pollution data for a location.

    Retrieves predictions for up to 120 hours (five days) into the future.

    Parameters
    ----------
    lat : float
        Latitude of the location.
    lon : float
        Longitude of the location.
    api_key : str, optional
        API key for OpenWeatherMap.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing forecasted records. Each record
        corresponds to a future timestamp.
    """
    if api_key is None:
        api_key = config.get_api_key()
        if api_key is None:
            raise ValueError(
                "Missing OpenWeatherMap API key. Set OPENWEATHER_API_KEY environment variable or pass api_key argument."
            )
    params = {"lat": lat, "lon": lon, "appid": api_key}
    json_data = _request(config.AIR_POLLUTION_FORECAST_API_URL, params)
    records = json_data.get("list", [])
    df = _flatten_pollution_records(records)
    return df
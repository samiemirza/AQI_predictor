"""
Feature engineering utilities for AQI prediction.

This module contains functions to transform raw pollution measurements
into a richer set of features suitable for machine learning models.
Typical transformations include extracting calendar attributes from the
timestamp, computing differences and ratios between pollutants, and
deriving rolling statistics. Feel free to augment these functions
based on your exploratory analysis and modelling needs.
"""

from __future__ import annotations

import pandas as pd
from pandas.tseries.frequencies import to_offset
import numpy as np
from typing import List, Optional

from . import config


def _convert_to_datetime(df: pd.DataFrame, timezone: str = config.TIMEZONE) -> pd.Series:
    """Convert a column of UNIX timestamps to timezone-aware datetimes.

    The raw data returned by the API includes a ``dt`` column expressed
    as seconds since the Unix epoch in UTC. This helper converts
    these integers into pandas ``datetime64[ns, tz]`` values adjusted
    to the target timezone.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing a ``dt`` column.
    timezone : str
        Timezone name (IANA format) to convert to.

    Returns
    -------
    pd.Series
        Series of timezone-aware timestamps.
    """
    dt_series = pd.to_datetime(df["dt"], unit="s", utc=True)
    return dt_series.dt.tz_convert(timezone)


def build_time_features(
    timestamps: pd.Series,
    include_day_of_year: bool = False,
) -> pd.DataFrame:
    """Extract basic calendar-based features from a datetime series.

    Parameters
    ----------
    timestamps : pd.Series
        Series of ``datetime64[ns, tz]`` values.
    include_day_of_year : bool, optional
        Whether to include the day-of-year feature, by default False.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``hour``, ``dayofweek``, ``month``,
        ``day`` and optionally ``dayofyear`` and ``is_weekend``.
    """
    df_time = pd.DataFrame(index=timestamps.index)
    df_time["hour"] = timestamps.dt.hour
    df_time["dayofweek"] = timestamps.dt.weekday
    df_time["month"] = timestamps.dt.month
    df_time["day"] = timestamps.dt.day
    df_time["is_weekend"] = (df_time["dayofweek"] >= 5).astype(int)
    if include_day_of_year:
        df_time["dayofyear"] = timestamps.dt.dayofyear
    return df_time


def compute_features(
    df_raw: pd.DataFrame,
    compute_change: bool = True,
    add_ratios: bool = True,
    rolling_windows: Optional[List[int]] = None,
) -> pd.DataFrame:
    """Compute engineered features from raw pollution data.

    The raw dataset must contain at minimum a ``dt`` column (Unix
    timestamp), ``main_aqi`` and pollutant component columns such as
    ``pm2_5`` and ``pm10``. This function will:

    - Convert the timestamp to a timezone-aware datetime and set it
      as the index.
    - Extract time-based features (hour, day of week, month, etc.).
    - Compute optional difference features (change rates) for the AQI
      and selected pollutants.
    - Compute optional ratio features (e.g. PM2.5/PM10).
    - Compute optional rolling statistics over specified window sizes.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Raw DataFrame as returned by the data fetching functions.
    compute_change : bool, optional
        Whether to compute first-order differences for the ``main_aqi``
        and pollutant columns, by default True.
    add_ratios : bool, optional
        Whether to compute useful ratios such as ``pm_ratio``, by
        default True.
    rolling_windows : list of int, optional
        Window sizes (in number of periods) for computing rolling mean
        and standard deviation of the AQI. If None, no rolling stats
        are added. Large windows may increase computation time.

    Returns
    -------
    pandas.DataFrame
        DataFrame with engineered features. The timestamp will be
        preserved in a ``timestamp`` column, but the DataFrame will
        otherwise use a default integer index.
    """
    df = df_raw.copy().reset_index(drop=True)
    # Convert dt to timezone-aware datetime and keep a copy
    timestamps = _convert_to_datetime(df)
    df["timestamp"] = timestamps
    # Extract time features
    time_features = build_time_features(timestamps)
    df = pd.concat([df, time_features], axis=1)

    pollutant_cols = [
        c
        for c in ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]
        if c in df.columns
    ]

    # Difference features
    if compute_change:
        # Use numerical AQI if available, otherwise fall back to main_aqi
        aqi_col = "aqi_numerical" if "aqi_numerical" in df.columns else "main_aqi"
        df["aqi_change"] = df[aqi_col].diff()
        for col in pollutant_cols:
            df[f"{col}_change"] = df[col].diff()

    # Ratio features
    if add_ratios:
        if all(col in df.columns for col in ["pm2_5", "pm10"]):
            # Avoid division by zero
            df["pm_ratio"] = df["pm2_5"] / df["pm10"].replace(0, np.nan)

    # Rolling statistics on AQI
    if rolling_windows:
        for window in rolling_windows:
            # Rolling mean and std
            df[f"aqi_roll_mean_{window}"] = (
                df[aqi_col].rolling(window=window, min_periods=1).mean()
            )
            df[f"aqi_roll_std_{window}"] = (
                df[aqi_col].rolling(window=window, min_periods=1).std()
            )

    # Remove rows with NaNs produced by diff or ratio operations
    df = df.dropna().reset_index(drop=True)
    return df
"""
Pipeline orchestrators for the AQI prediction project.

This module defines high-level functions to execute the various
pipeline stages in sequence: fetching raw data, engineering
features, persisting them to the feature store, training models
and performing inference. By exposing these steps as functions,
you can integrate them into schedulers, CI/CD systems or manual
workflows as needed.
"""

from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import pandas as pd

from . import config
from .data_fetcher import (
    fetch_air_pollution_history,
    fetch_forecast_air_pollution,
)
from .feature_engineering import compute_features
from .feature_store import FeatureStore
from .training import train_and_select_model
from .model_registry import ModelRegistry


def run_feature_pipeline(
    lat: float,
    lon: float,
    days_back: int = 5,
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch raw pollution data, engineer features and persist them.

    Parameters
    ----------
    lat, lon : float
        Geographic coordinates for which to fetch data.
    days_back : int, optional
        Number of days of historical data to retrieve. Defaults to 5,
        which is the maximum supported by the free tier of the API.
    api_key : str, optional
        API key for OpenWeatherMap. If None, falls back to
        environment variable.

    Returns
    -------
    pandas.DataFrame
        The engineered features that were stored.
    """
    # Determine time window in UTC
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)
    raw_df = fetch_air_pollution_history(
        lat=lat, lon=lon, start_time=start_time, end_time=end_time, api_key=api_key
    )
    if raw_df.empty:
        print("No raw data fetched. Check your API key and network connectivity.")
        return pd.DataFrame()
    features_df = compute_features(
        raw_df,
        compute_change=True,
        add_ratios=True,
        rolling_windows=[3, 12, 24],
    )
    store = FeatureStore()
    store.save(features_df, append=True)
    return features_df


def run_training_pipeline() -> Optional[object]:
    """Execute the training pipeline: load features, train models and register the best one."""
    result = train_and_select_model()
    return result


def run_inference_pipeline(
    lat: float, lon: float, api_key: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Generate AQI forecasts for the next five days using the latest model.

    Parameters
    ----------
    lat, lon : float
        Coordinates for the forecast location.
    api_key : str, optional
        API key for the API. If ``None``, environment variable is used.

    Returns
    -------
    pandas.DataFrame or None
        DataFrame containing timestamps and predicted AQI values.
    """
    # Fetch forecast data
    forecast_raw = fetch_forecast_air_pollution(lat=lat, lon=lon, api_key=api_key)
    if forecast_raw.empty:
        print("Unable to fetch forecast data. Ensure your API key is valid.")
        return None
    # Compute features; note that diff-based features will produce NaNs at the first row; drop them
    forecast_features = compute_features(
        forecast_raw,
        compute_change=True,
        add_ratios=True,
        rolling_windows=[3, 12, 24],
    )
    # The forecasting features DataFrame contains 'main_aqi' but we should not use it to predict itself.
    # We'll prepare the feature matrix using the same feature columns as training.
    registry = ModelRegistry()
    latest_entry = registry.get_latest_model("random_forest")
    if latest_entry is None:
        # Try to load any model
        for model_name in ["random_forest", "ridge_regression", "mlp_regressor", "keras_mlp"]:
            entry = registry.get_latest_model(model_name)
            if entry is not None:
                latest_entry = entry
                break
    if latest_entry is None:
        print("No trained models found in the registry. Run the training pipeline first.")
        return None
    model, metadata = latest_entry
    
    # Use the feature columns that were used during training
    if hasattr(metadata, 'feature_columns') and metadata.feature_columns:
        feature_cols = [col for col in metadata.feature_columns if col in forecast_features.columns]
        if not feature_cols:
            print("None of the training feature columns found in forecast data.")
            return None
    else:
        # Fallback to default feature columns if metadata doesn't have feature_columns
        default_cols = [
            "co",
            "no",
            "no2",
            "o3",
            "so2",
            "pm2_5",
            "pm10",
            "nh3",
            "hour",
            "dayofweek",
            "month",
            "day",
            "is_weekend",
            "aqi_change",
            "pm_ratio",
        ]
        feature_cols = [col for col in default_cols if col in forecast_features.columns]
    
    print(f"Using {len(feature_cols)} features: {feature_cols}")
    
    X_forecast = forecast_features[feature_cols].values.astype(float)
    predictions = model.predict(X_forecast)
    result_df = pd.DataFrame(
        {
            "timestamp": forecast_features["timestamp"],
            "predicted_aqi": predictions,
        }
    )
    
    # Add AQI category information to predictions
    from .aqi_calculator import get_aqi_category
    result_df["aqi_category"] = result_df["predicted_aqi"].apply(
        lambda x: get_aqi_category(x)["category"] if x is not None else "Unknown"
    )
    result_df["aqi_color"] = result_df["predicted_aqi"].apply(
        lambda x: get_aqi_category(x)["color"] if x is not None else "gray"
    )
    
    return result_df


def main() -> None:
    """Command-line interface for the pipeline module.

    Usage examples::

        python -m aqi_project.src.pipeline run_feature_pipeline --lat 24.86 --lon 67.00 --days-back 5
        python -m aqi_project.src.pipeline run_training_pipeline
        python -m aqi_project.src.pipeline run_inference_pipeline --lat 24.86 --lon 67.00

    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="AQI prediction pipeline commands")
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for run_feature_pipeline
    p_feature = subparsers.add_parser(
        "run_feature_pipeline", help="Fetch raw data and compute/store features"
    )
    p_feature.add_argument("--lat", type=float, required=True, help="Latitude")
    p_feature.add_argument("--lon", type=float, required=True, help="Longitude")
    p_feature.add_argument(
        "--days-back",
        type=int,
        default=5,
        help="Number of past days to fetch for feature generation",
    )

    # Subparser for run_training_pipeline
    subparsers.add_parser(
        "run_training_pipeline", help="Train models using stored features"
    )

    # Subparser for run_inference_pipeline
    p_infer = subparsers.add_parser(
        "run_inference_pipeline", help="Generate predictions for the next five days"
    )
    p_infer.add_argument("--lat", type=float, required=True, help="Latitude")
    p_infer.add_argument("--lon", type=float, required=True, help="Longitude")

    args = parser.parse_args()
    if args.command == "run_feature_pipeline":
        df = run_feature_pipeline(lat=args.lat, lon=args.lon, days_back=args.days_back)
        print(f"Generated {len(df)} feature rows.")
    elif args.command == "run_training_pipeline":
        result = run_training_pipeline()
        if result:
            print(f"Best model: {result.name} with RMSE={result.metrics['rmse']:.3f}")
    elif args.command == "run_inference_pipeline":
        df = run_inference_pipeline(lat=args.lat, lon=args.lon)
        if df is not None:
            print(df.head())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
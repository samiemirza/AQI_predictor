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
from .training import train_and_select_model, train_models_for_horizons
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
    # Preserve location so multi-city data can coexist safely in the feature store.
    raw_df["lat"] = lat
    raw_df["lon"] = lon
    features_df = compute_features(
        raw_df,
        compute_change=True,
        add_ratios=True,
        rolling_windows=[3, 12, 24],
    )
    store = FeatureStore()
    store.save(features_df, append=True)
    return features_df


def run_training_pipeline(train_multi_horizons: bool = True) -> Optional[object]:
    """Execute training. If ``train_multi_horizons`` is True, trains 24h/48h/72h models; otherwise trains a single horizon (72h)."""
    if train_multi_horizons:
        results = train_models_for_horizons([24, 48, 72])
        return results[-1] if results else None
    else:
        result = train_and_select_model()
        return result


def run_inference_pipeline(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    prefer_direct_forecast: bool = False,
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
    forecast_raw["lat"] = lat
    forecast_raw["lon"] = lon
    # Compute features; note that diff-based features will produce NaNs at the first row; drop them
    forecast_features = compute_features(
        forecast_raw,
        compute_change=True,
        add_ratios=True,
        rolling_windows=[3, 12, 24],
    )

    # Prefer direct forecast-derived AQI (from pollutant forecast + EPA formula)
    # for more stable location-specific predictions.
    if prefer_direct_forecast and "aqi_numerical" in forecast_features.columns:
        ts_series = forecast_features["timestamp"]
        if not ts_series.empty:
            now_ts = pd.Timestamp.now(tz=ts_series.dt.tz)
            future_mask = ts_series >= now_ts
            base_idx = int(future_mask.idxmax()) if future_mask.any() else 0
            base_time = ts_series.iloc[base_idx]
            results_list = []

            for horizon in [24, 48, 72]:
                target_time = base_time + timedelta(hours=horizon)
                deltas = (ts_series - target_time).abs()
                nearest_idx = int(deltas.idxmin())
                y_hat = forecast_features.loc[nearest_idx, "aqi_numerical"]
                if pd.isna(y_hat):
                    continue
                results_list.append(
                    {
                        "timestamp": ts_series.iloc[nearest_idx],
                        "predicted_aqi": float(y_hat),
                        "horizon_hours": horizon,
                    }
                )

            if results_list:
                result_df = pd.DataFrame(results_list)
                from .aqi_calculator import get_aqi_category
                result_df["aqi_category"] = result_df["predicted_aqi"].apply(
                    lambda x: get_aqi_category(x)["category"] if x is not None else "Unknown"
                )
                result_df["aqi_color"] = result_df["predicted_aqi"].apply(
                    lambda x: get_aqi_category(x)["color"] if x is not None else "gray"
                )
                return result_df
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
    
    # Helper to extract feature columns and predict for a given model/metadata
    def _predict_with_model(current_model, current_metadata) -> Optional[pd.DataFrame]:
        if hasattr(current_metadata, 'feature_columns') and current_metadata.feature_columns:
            feature_cols_local = [col for col in current_metadata.feature_columns if col in forecast_features.columns]
            if not feature_cols_local:
                print("None of the training feature columns found in forecast data.")
                return None
        else:
            default_cols = [
                "lat",
                "lon",
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
            feature_cols_local = [col for col in default_cols if col in forecast_features.columns]

        # Build predictions for the first forecast step only (base time), then map to horizon timestamps
        X_forecast_local = forecast_features[feature_cols_local].values.astype(float)
        preds_local = current_model.predict(X_forecast_local)
        base_time = forecast_features["timestamp"].iloc[0]
        df_local = pd.DataFrame({
            "timestamp": [base_time],
            "predicted_aqi": [float(preds_local[0])],
        })
        return df_local

    # Load horizon-specific models if available and return only up to 3 days
    registry = ModelRegistry()
    horizon_models = {}
    for horizon in [24, 48, 72]:
        # Prefer RandomForest, then Ridge, then MLP, then Keras
        for name in [f"random_forest_h{horizon}", f"ridge_regression_h{horizon}", f"mlp_regressor_h{horizon}", f"keras_mlp_h{horizon}"]:
            entry = registry.get_latest_model(name)
            if entry is not None:
                horizon_models[horizon] = entry
                break

    # Build three predictions anchored at the first forecast timestamp >= now
    ts_series = forecast_features["timestamp"]
    now_ts = pd.Timestamp.now(tz=ts_series.dt.tz)
    future_mask = ts_series >= now_ts
    if future_mask.any():
        base_idx = int(future_mask.idxmax())
    else:
        base_idx = 0

    results_list = []
    def _predict_for_index(mdl, meta, row_index: int) -> Optional[float]:
        # Build features for a single row index using training feature columns
        if hasattr(meta, 'feature_columns') and meta.feature_columns:
            cols = [c for c in meta.feature_columns if c in forecast_features.columns]
        else:
            cols = [
                "lat","lon",
                "co","no","no2","o3","so2","pm2_5","pm10","nh3",
                "hour","dayofweek","month","day","is_weekend","aqi_change","pm_ratio",
            ]
            cols = [c for c in cols if c in forecast_features.columns]
        if not cols:
            return None
        x = forecast_features.loc[row_index, cols].values.astype(float).reshape(1, -1)
        try:
            y_pred = mdl.predict(x)
            return float(y_pred[0])
        except Exception:
            return None

    base_time = ts_series.iloc[base_idx]
    for horizon in [24, 48, 72]:
        entry = horizon_models.get(horizon)
        if entry is None:
            continue
        mdl, meta = entry
        y_hat = _predict_for_index(mdl, meta, base_idx)
        if y_hat is None:
            continue
        predicted_time = base_time + timedelta(hours=horizon)
        results_list.append({
            "timestamp": predicted_time,
            "predicted_aqi": y_hat,
            "horizon_hours": horizon,
        })

    if not results_list:
        # Fallback: use latest generic model at base index, treat as 72h
        y_hat = _predict_for_index(model, metadata, base_idx)
        if y_hat is None:
            return None
        results_list = [{
            "timestamp": base_time + timedelta(hours=72),
            "predicted_aqi": y_hat,
            "horizon_hours": 72,
        }]

    result_df = pd.DataFrame(results_list)
    # Add AQI category information
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

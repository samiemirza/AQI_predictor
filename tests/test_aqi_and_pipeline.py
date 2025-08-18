#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure project root is importable so that `src` package can be found
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # type: ignore

def test_aqi_calculator_basic():
    from src.aqi_calculator import calculate_aqi
    result = calculate_aqi({
        'pm2_5': 20.0,
        'pm10': 40.0,
        'o3': 60.0,
        'no2': 70.0,
        'co': 6.0,
        'so2': 40.0,
    })
    assert result['aqi'] is not None
    assert 0 <= result['aqi'] <= 500
    assert result['category'] in {'Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous'}


def test_feature_engineering_smoke():
    from src.feature_engineering import compute_features
    # Minimal synthetic raw data similar to OpenWeather response format
    df_raw = pd.DataFrame({
        'dt': [1700000000 + 3600 * i for i in range(10)],
        'main_aqi': [1]*10,
        'pm2_5': [10 + i for i in range(10)],
        'pm10': [20 + i for i in range(10)],
        'o3': [40]*10,
        'no2': [30]*10,
        'so2': [5]*10,
        'co': [1]*10,
        'nh3': [2]*10,
    })
    feats = compute_features(df_raw, compute_change=True, add_ratios=True, rolling_windows=[3])
    assert 'timestamp' in feats.columns
    assert 'hour' in feats.columns
    assert 'aqi_change' in feats.columns
    assert 'pm_ratio' in feats.columns


def test_pipeline_prepare_and_registry(tmp_path, monkeypatch):
    # Redirect data and models directories to temp to avoid touching repo files
    from src import config
    # Redirect config paths to tmp directories
    config.DATA_DIR = tmp_path / 'data'
    config.MODEL_REGISTRY_DIR = tmp_path / 'models'
    config.FEATURE_STORE_PATH = config.DATA_DIR / 'features.parquet'
    config.ensure_directories()

    # Create small feature dataset in the feature store
    from src.feature_store import FeatureStore
    from src.feature_engineering import compute_features

    # Build 100 hours of synthetic raw data
    df_raw = pd.DataFrame({
        'dt': [1700000000 + 3600 * i for i in range(100)],
        'main_aqi': [50 + (i % 10) for i in range(100)],
        'pm2_5': [15 + (i % 5) for i in range(100)],
        'pm10': [25 + (i % 5) for i in range(100)],
        'o3': [40]*100,
        'no2': [30]*100,
        'so2': [5]*100,
        'co': [1]*100,
        'nh3': [2]*100,
    })
    feats = compute_features(df_raw, compute_change=True, add_ratios=True, rolling_windows=[3, 12])
    FeatureStore(store_path=config.FEATURE_STORE_PATH).save(feats, append=False)

    # Train and register best model
    from src.training import train_and_select_model
    result = train_and_select_model(target_horizon_hours=3, test_size=0.25)
    assert result is not None
    assert result.metrics['rmse'] >= 0



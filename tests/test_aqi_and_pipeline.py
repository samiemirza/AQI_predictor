#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure project root is importable so that `src` package can be found
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # type: ignore


class DummyModel:
    def predict(self, X):
        return [42.0 for _ in range(len(X))]

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


def test_openweather_gases_are_converted_before_aqi():
    from src.aqi_calculator import calculate_aqi_from_api_data, convert_openweather_components

    converted = convert_openweather_components({'o3': 100.0, 'co': 1000.0})
    assert 50 <= converted['o3'] <= 51
    assert 0.8 <= converted['co'] <= 0.9

    result = calculate_aqi_from_api_data({'o3': 100.0, 'co': 1000.0})
    assert result['sub_indices']['o3'] < 60
    assert result['aqi'] < 60


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


def test_feature_engineering_rolling_without_change():
    from src.feature_engineering import compute_features

    df_raw = pd.DataFrame({
        'dt': [1700000000 + 3600 * i for i in range(4)],
        'main_aqi': [1, 2, 3, 4],
        'pm2_5': [10, 11, 12, 13],
        'pm10': [20, 21, 22, 23],
    })
    feats = compute_features(df_raw, compute_change=False, add_ratios=False, rolling_windows=[3])
    assert 'aqi_roll_mean_3' in feats.columns
    assert 'aqi_change' not in feats.columns


def test_model_registry_resolves_local_file_when_metadata_path_is_stale(tmp_path, monkeypatch):
    import json
    import joblib

    from src import config
    from src.model_registry import ModelRegistry

    monkeypatch.setattr(config, 'MODEL_REGISTRY_DIR', tmp_path)
    config.ensure_directories()
    model_path = tmp_path / 'dummy_model_v1.pkl'
    joblib.dump(DummyModel(), model_path)
    registry_path = tmp_path / 'model_registry.json'
    registry_path.write_text(json.dumps({
        'dummy_model': [{
            'name': 'dummy_model',
            'version': 1,
            'model_type': 'sklearn',
            'metrics': {'rmse': 1.0},
            'created_at': '2026-01-01T00:00:00',
            'file_path': '/old/machine/path/dummy_model_v1.pkl',
            'feature_columns': ['pm2_5'],
        }]
    }))

    model, metadata = ModelRegistry(registry_dir=tmp_path).get_latest_model('dummy_model')
    assert metadata.version == 1
    assert model.predict([[1.0]]) == [42.0]


def test_time_ordered_split_preserves_temporal_holdout():
    import numpy as np

    from src.training import time_ordered_train_test_split

    X = np.arange(10).reshape(-1, 1)
    y = np.arange(10)
    X_train, X_test, y_train, y_test = time_ordered_train_test_split(X, y, test_size=0.3)
    assert X_train.flatten().tolist() == list(range(7))
    assert X_test.flatten().tolist() == [7, 8, 9]
    assert y_train.tolist() == list(range(7))
    assert y_test.tolist() == [7, 8, 9]


def test_training_targets_recompute_stale_aqi_values():
    from src.training import prepare_training_data

    df = pd.DataFrame({
        'timestamp': pd.date_range('2026-01-01', periods=4, freq='h'),
        'aqi_numerical': [190, 190, 190, 190],
        'pm2_5': [1.0, 1.0, 1.0, 1.0],
        'pm10': [2.0, 2.0, 2.0, 2.0],
        'o3': [100.0, 100.0, 100.0, 100.0],
        'no2': [1.0, 1.0, 1.0, 1.0],
        'so2': [1.0, 1.0, 1.0, 1.0],
        'co': [1000.0, 1000.0, 1000.0, 1000.0],
    })

    _, y, _ = prepare_training_data(df, target_horizon_hours=1, feature_cols=['pm2_5'])
    assert y.max() < 60


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

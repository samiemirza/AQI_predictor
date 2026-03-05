"""
Training module for AQI prediction models.

This module orchestrates the process of loading historical features,
preparing training and test splits, fitting multiple models, evaluating
their performance, and registering the best-performing model in the
model registry. Both classical machine learning models (Random
Forest, Ridge Regression) and a simple neural network are considered.

To extend the repertoire of models, simply add new entries to the
``MODELS`` dictionary with an appropriate training function.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Union
import os

import numpy as np
import pandas as pd

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor

from .feature_store import FeatureStore
from .model_registry import ModelRegistry


def _get_tensorflow():
    """Return tensorflow only when explicitly enabled and importable."""
    if os.getenv("AQI_ENABLE_TENSORFLOW", "0") != "1":
        return None
    try:
        import tensorflow as tf  # type: ignore
        return tf
    except Exception:
        return None


@dataclass
class ModelResult:
    name: str
    model: object
    metrics: Dict[str, float]
    model_type: str  # 'sklearn' or 'keras'


def prepare_training_data(
    df: pd.DataFrame,
    target_horizon_hours: int = 72,
    feature_cols: Optional[List[str]] = None,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Prepare features and targets for training.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing engineered features and at least the
        ``main_aqi`` column.
    target_horizon_hours : int, optional
        Number of hours into the future to predict. Defaults to 72 (3
        days for hourly data).
    feature_cols : list of str, optional
        Columns to use as model inputs. If None, a sensible default
        based on the contents of ``df`` will be used.

    Returns
    -------
    tuple
        Tuple ``(X, y, feature_names)`` where ``X`` is a 2D array of
        features, ``y`` is a 1D array of targets and ``feature_names``
        lists the names of the columns used.
    """
    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    # Build target column by shifting AQI backwards
    # Use numerical AQI if available, otherwise fall back to main_aqi
    aqi_col = "aqi_numerical" if "aqi_numerical" in df_sorted.columns else "main_aqi"
    target_column = f"aqi_future_{target_horizon_hours}h"
    df_sorted[target_column] = df_sorted[aqi_col].shift(-target_horizon_hours)
    # Drop last horizon rows with NaNs in target
    df_sorted = df_sorted.dropna(subset=[target_column])

    # Determine feature columns if not provided
    if feature_cols is None:
        default_features = [
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
        feature_cols = [col for col in default_features if col in df_sorted.columns]

    X = df_sorted[feature_cols].values.astype(float)
    y = df_sorted[target_column].values.astype(float)
    return X, y, feature_cols


def train_models_for_horizons(
    horizons: List[int] = [24, 48, 72],
    test_size: float = 0.2,
    random_state: int = 42,
) -> List[ModelResult]:
    """Train and register models for multiple prediction horizons.

    For each horizon in hours, the function prepares the target column by shifting
    the AQI accordingly, trains a set of candidate models, evaluates them, and
    registers the best one with a horizon-specific model name, e.g.,
    ``random_forest_h24``.

    Returns a list of best ``ModelResult`` per horizon.
    """
    store = FeatureStore()
    df = store.load()
    if df.empty:
        print("No features found in the feature store. Run the feature pipeline first.")
        return []

    results: List[ModelResult] = []

    for horizon in horizons:
        X, y, feature_cols = prepare_training_data(df, target_horizon_hours=horizon)
        if len(X) < 10:
            print(f"Insufficient data for training horizon {horizon}h. Need at least 10 samples.")
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        candidates: List[ModelResult] = []
        try:
            rf_model = train_random_forest(X_train, y_train)
            rf_metrics = evaluate_model(rf_model, X_test, y_test)
            candidates.append(ModelResult(f"random_forest_h{horizon}", rf_model, rf_metrics, "sklearn"))
        except Exception as e:
            print(f"Random Forest training failed for {horizon}h: {e}")

        try:
            ridge_model = train_ridge_regression(X_train, y_train)
            ridge_metrics = evaluate_model(ridge_model, X_test, y_test)
            candidates.append(ModelResult(f"ridge_regression_h{horizon}", ridge_model, ridge_metrics, "sklearn"))
        except Exception as e:
            print(f"Ridge Regression training failed for {horizon}h: {e}")

        try:
            mlp_model = train_mlp_regressor(X_train, y_train)
            mlp_metrics = evaluate_model(mlp_model, X_test, y_test)
            candidates.append(ModelResult(f"mlp_regressor_h{horizon}", mlp_model, mlp_metrics, "sklearn"))
        except Exception as e:
            print(f"MLP Regressor training failed for {horizon}h: {e}")

        if _get_tensorflow() is not None:
            try:
                keras_model = train_keras_mlp(X_train, y_train, X_test, y_test)
                if keras_model is not None:
                    keras_metrics = evaluate_model(keras_model, X_test, y_test)
                    candidates.append(ModelResult(f"keras_mlp_h{horizon}", keras_model, keras_metrics, "keras"))
            except Exception as e:
                print(f"Keras MLP training failed for {horizon}h: {e}")

        if not candidates:
            print(f"All model training attempts failed for horizon {horizon}h.")
            continue

        best_model = min(candidates, key=lambda m: m.metrics["rmse"])\
            if candidates else None
        if best_model is None:
            continue
        print(f"Best model for {horizon}h: {best_model.name} with RMSE={best_model.metrics['rmse']:.3f}")

        registry = ModelRegistry()
        metadata = registry.register_model(
            best_model.model,
            best_model.name,
            best_model.model_type,
            best_model.metrics,
            feature_columns=feature_cols,
        )
        results.append(best_model)

    return results


def train_random_forest(X_train: np.ndarray, y_train: np.ndarray) -> object:
    """Train a RandomForestRegressor with sensible defaults."""
    model = RandomForestRegressor(
        n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model


def train_ridge_regression(X_train: np.ndarray, y_train: np.ndarray) -> object:
    """Train a Ridge Regression model wrapped in a pipeline for scaling."""
    model = Pipeline(
        steps=[("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))]
    )
    model.fit(X_train, y_train)
    return model


def train_mlp_regressor(X_train: np.ndarray, y_train: np.ndarray) -> object:
    """Train a Multi-layer Perceptron regressor using scikit-learn.

    Although not as powerful as Keras-based neural networks, scikit's
    MLPRegressor provides a simple feed-forward architecture that
    satisfies the requirement for deep learning models without the
    dependency overhead. You can adjust the hidden layer sizes or other
    hyperparameters as needed.
    """
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        random_state=42,
        max_iter=500,
        early_stopping=True,
    )
    model.fit(X_train, y_train)
    return model


def train_keras_mlp(
    X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray
) -> Optional[object]:
    """Train a simple Keras feed-forward neural network.

    This model is only trained if TensorFlow is available in the
    environment. It uses an early stopping callback to prevent
    overfitting.
    """
    tf = _get_tensorflow()
    if tf is None:
        return None
    input_dim = X_train.shape[1]
    model = tf.keras.Sequential(
        [
            tf.keras.layers.InputLayer(input_shape=(input_dim,)),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(1),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="mse",
        metrics=[tf.keras.metrics.RootMeanSquaredError(), "mae"],
    )
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )
    model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=[early_stop],
        verbose=0,
    )
    return model


def evaluate_model(model: object, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """Compute evaluation metrics for a trained model."""
    preds = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae = float(mean_absolute_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def train_and_select_model(
    target_horizon_hours: int = 72,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Optional[ModelResult]:
    """Train multiple models and select the best performing one.

    This function trains several different model types and selects the
    one with the lowest RMSE on the test set. The best model is
    automatically registered in the model registry.

    Parameters
    ----------
    target_horizon_hours : int, optional
        Number of hours into the future to predict, by default 72.
    test_size : float, optional
        Proportion of data to use for testing, by default 0.2.
    random_state : int, optional
        Random seed for reproducibility, by default 42.

    Returns
    -------
    ModelResult or None
        The best performing model with its metrics, or None if training fails.
    """
    # Load features from the feature store
    store = FeatureStore()
    df = store.load()
    if df.empty:
        print("No features found in the feature store. Run the feature pipeline first.")
        return None

    # Prepare training data
    X, y, feature_cols = prepare_training_data(df, target_horizon_hours)
    if len(X) < 10:
        print("Insufficient data for training. Need at least 10 samples.")
        return None

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Train models
    models = []
    
    # Random Forest
    try:
        rf_model = train_random_forest(X_train, y_train)
        rf_metrics = evaluate_model(rf_model, X_test, y_test)
        models.append(
            ModelResult("random_forest", rf_model, rf_metrics, "sklearn")
        )
    except Exception as e:
        print(f"Random Forest training failed: {e}")

    # Ridge Regression
    try:
        ridge_model = train_ridge_regression(X_train, y_train)
        ridge_metrics = evaluate_model(ridge_model, X_test, y_test)
        models.append(
            ModelResult("ridge_regression", ridge_model, ridge_metrics, "sklearn")
        )
    except Exception as e:
        print(f"Ridge Regression training failed: {e}")

    # MLP Regressor
    try:
        mlp_model = train_mlp_regressor(X_train, y_train)
        mlp_metrics = evaluate_model(mlp_model, X_test, y_test)
        models.append(
            ModelResult("mlp_regressor", mlp_model, mlp_metrics, "sklearn")
        )
    except Exception as e:
        print(f"MLP Regressor training failed: {e}")

    # Keras MLP (if TensorFlow is available)
    if _get_tensorflow() is not None:
        try:
            keras_model = train_keras_mlp(X_train, y_train, X_test, y_test)
            if keras_model is not None:
                keras_metrics = evaluate_model(keras_model, X_test, y_test)
                models.append(
                    ModelResult("keras_mlp", keras_model, keras_metrics, "keras")
                )
        except Exception as e:
            print(f"Keras MLP training failed: {e}")

    if not models:
        print("All model training attempts failed.")
        return None

    # Select best model
    best_model = min(models, key=lambda m: m.metrics["rmse"])
    print(f"Best model: {best_model.name} with RMSE={best_model.metrics['rmse']:.3f}")

    # Register the best model
    registry = ModelRegistry()
    metadata = registry.register_model(
        best_model.model,
        best_model.name,
        best_model.model_type,
        best_model.metrics,
    )
    
    # Store feature columns in metadata
    metadata.feature_columns = feature_cols
    print(f"Registered model '{best_model.name}' version {metadata.version} with metrics: {best_model.metrics}")

    return best_model

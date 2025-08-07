"""
Package initialiser for the AQI prediction project.

This package bundles together modules for data acquisition, feature
engineering, model training, model registry management, pipelines,
scheduling and dashboarding.
"""

__all__ = [
    "config",
    "data_fetcher",
    "feature_engineering",
    "feature_store",
    "model_registry",
    "training",
    "pipeline",
    "scheduler",
    "aqi_calculator",
]
"""
Task scheduler for the AQI prediction pipeline.

This module uses the ``schedule`` library to periodically execute
various pipeline stages. The feature extraction job runs every
hour by default, while the training job executes once per day. You
can customise the scheduling rules by modifying the schedule
expressions in the ``start_scheduler`` function.

Note that this scheduler runs in a blocking loop. To deploy it in
a production environment you may want to use a more robust task
scheduler (e.g., Apache Airflow, Celery, or cloud-native cron jobs).
"""

from __future__ import annotations

import time
from typing import Optional

import schedule  # type: ignore

from .pipeline import run_feature_pipeline, run_training_pipeline


def start_scheduler(lat: float, lon: float, api_key: Optional[str] = None) -> None:
    """Start the recurring tasks for feature extraction and training.

    Parameters
    ----------
    lat, lon : float
        Location for which to fetch data and train models.
    api_key : str, optional
        API key to pass through to pipeline functions. If None,
        environment variables are used.
    """
    # Schedule the feature pipeline every hour
    schedule.every().hour.do(run_feature_pipeline, lat=lat, lon=lon, api_key=api_key)
    # Schedule the training pipeline daily at midnight
    schedule.every().day.at("00:00").do(run_training_pipeline)

    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Scheduler stopped.")


def main() -> None:
    """Command-line interface entry point for the scheduler.

    Example::

        python -m aqi_project.src.scheduler --lat 24.86 --lon 67.00

    """
    import argparse

    parser = argparse.ArgumentParser(description="Run the AQI scheduler")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    args = parser.parse_args()
    start_scheduler(lat=args.lat, lon=args.lon)


if __name__ == "__main__":
    main()
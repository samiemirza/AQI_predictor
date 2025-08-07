"""
Simple feature store built on top of Parquet files.

This module implements a rudimentary feature store backed by a
Parquet file on disk. While far less sophisticated than cloud-based
solutions like Hopsworks or Vertex AI Feature Store, it serves the
purpose of persisting engineered features between runs of the pipeline.

Features are stored in a single Parquet file keyed by the
``timestamp`` column. When appending new records, duplicates based
on the timestamp are removed and the combined data is sorted in
ascending order of time.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional

from . import config


class FeatureStore:
    """Interface to persist and retrieve features from disk."""

    def __init__(self, store_path: Path | None = None) -> None:
        """Initialise the feature store.

        Parameters
        ----------
        store_path : pathlib.Path, optional
            Location of the Parquet file used as the feature store.
            Defaults to ``config.FEATURE_STORE_PATH``.
        """
        self.store_path: Path = store_path or config.FEATURE_STORE_PATH
        # Ensure parent directories exist
        config.ensure_directories()

    def load(self) -> pd.DataFrame:
        """Load the full set of stored features.

        Returns
        -------
        pandas.DataFrame
            The feature DataFrame, or an empty DataFrame if the
            store file does not exist.
        """
        if not self.store_path.exists():
            return pd.DataFrame()
        try:
            df = pd.read_parquet(self.store_path)
            # Ensure timestamp column is properly converted to datetime
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        except Exception:
            # Fallback to reading CSV if Parquet not available or corrupt
            try:
                df = pd.read_csv(self.store_path)
                # Ensure timestamp column is properly converted to datetime
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                return df
            except Exception:
                return pd.DataFrame()

    def save(self, df: pd.DataFrame, append: bool = True) -> None:
        """Persist features to disk.

        Parameters
        ----------
        df : pandas.DataFrame
            Feature DataFrame to store. Must include a ``timestamp``
            column.
        append : bool, optional
            Whether to append to existing data (deduplicating on
            timestamp) or overwrite entirely. Defaults to True.
        """
        if "timestamp" not in df.columns:
            raise ValueError("Feature DataFrame must contain a 'timestamp' column")

        if append and self.store_path.exists():
            existing = self.load()
            combined = pd.concat([existing, df], ignore_index=True)
            # Drop duplicates based on timestamp
            combined = combined.drop_duplicates(subset=["timestamp"]).sort_values(
                by="timestamp"
            ).reset_index(drop=True)
        else:
            combined = df.copy().sort_values(by="timestamp").reset_index(drop=True)

        # Save as Parquet if possible; otherwise fallback to CSV
        try:
            combined.to_parquet(self.store_path, index=False)
        except Exception:
            combined.to_csv(self.store_path, index=False)

    def purge(self) -> None:
        """Remove all stored features.

        This deletes the underlying store file. Use with caution.
        """
        if self.store_path.exists():
            self.store_path.unlink()
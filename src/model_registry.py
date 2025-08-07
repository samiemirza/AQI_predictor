"""
Model registry for storing and retrieving trained models.

This module implements a lightweight model registry that saves
individual models to disk and tracks associated metadata. Each
registered model is assigned a version number based on its name,
allowing multiple iterations of the same model architecture to
co-exist. Metadata includes evaluation metrics and training
timestamps to aid in comparison and reproducibility.

Two types of models are supported:

* ``sklearn`` models, persisted via ``joblib``. These are plain
  Python objects that can be loaded with ``joblib.load``.
* ``keras`` models, persisted using ``tensorflow.keras.Model.save`` and
  loaded via ``tensorflow.keras.models.load_model``.

If additional model frameworks are introduced, you can extend the
registry by providing appropriate save and load handlers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type

import joblib

from . import config

try:
    import tensorflow as tf  # type: ignore
except ImportError:
    tf = None  # type: ignore


@dataclass
class ModelMetadata:
    """Metadata describing a stored model."""

    name: str
    version: int
    model_type: str  # either "sklearn" or "keras"
    metrics: Dict[str, float]
    created_at: str  # ISO8601 timestamp
    file_path: str
    feature_columns: Optional[list] = None  # List of feature column names used during training


class ModelRegistry:
    """A simple file-based model registry."""

    REGISTRY_FILE = "model_registry.json"

    def __init__(self, registry_dir: Optional[Path] = None) -> None:
        self.registry_dir: Path = registry_dir or config.MODEL_REGISTRY_DIR
        config.ensure_directories()
        self.registry_path: Path = self.registry_dir / self.REGISTRY_FILE

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return {}
        with open(self.registry_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_registry(self, data: Dict[str, Any]) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _get_next_version(self, model_name: str, registry: Dict[str, Any]) -> int:
        versions = registry.get(model_name, [])
        if not versions:
            return 1
        latest_version = max(entry["version"] for entry in versions)
        return latest_version + 1

    def _get_model_filepath(self, model_name: str, version: int, model_type: str) -> Path:
        ext = "pkl" if model_type == "sklearn" else "keras"
        filename = f"{model_name}_v{version}.{ext}"
        return self.registry_dir / filename

    def register_model(
        self,
        model: Any,
        model_name: str,
        model_type: str,
        metrics: Dict[str, float],
    ) -> ModelMetadata:
        """Persist a trained model and register its metadata.

        Parameters
        ----------
        model : Any
            The trained model object.
        model_name : str
            Logical name of the model (e.g. ``"random_forest"``).
        model_type : str
            Either ``"sklearn"`` or ``"keras"`` indicating the
            serialization mechanism to use.
        metrics : dict
            Evaluation metrics for this model on a holdout set.

        Returns
        -------
        ModelMetadata
            Metadata describing the registered model.
        """
        registry = self._load_registry()
        version = self._get_next_version(model_name, registry)
        file_path = self._get_model_filepath(model_name, version, model_type)

        # Persist the model
        if model_type == "sklearn":
            joblib.dump(model, file_path)
        elif model_type == "keras":
            if tf is None:
                raise RuntimeError(
                    "TensorFlow is not installed; cannot save Keras models."
                )
            model.save(file_path)
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")

        metadata = ModelMetadata(
            name=model_name,
            version=version,
            model_type=model_type,
            metrics=metrics,
            created_at=datetime.utcnow().isoformat(),
            file_path=str(file_path),
        )

        # Update registry
        model_entries = registry.get(model_name, [])
        model_entries.append(asdict(metadata))
        registry[model_name] = model_entries
        self._save_registry(registry)
        return metadata

    def list_models(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """List registered models.

        Parameters
        ----------
        model_name : str, optional
            If provided, only return entries for the given model.

        Returns
        -------
        dict
            Mapping from model names to lists of metadata dictionaries.
        """
        registry = self._load_registry()
        if model_name:
            return {model_name: registry.get(model_name, [])}
        return registry

    def get_latest_model(self, model_name: str) -> Tuple[Any, ModelMetadata] | None:
        """Load the most recent version of a model.

        Parameters
        ----------
        model_name : str
            Name of the model.

        Returns
        -------
        tuple or None
            A tuple ``(model, metadata)`` for the latest version, or
            ``None`` if no model exists.
        """
        registry = self._load_registry()
        entries = registry.get(model_name)
        if not entries:
            return None
        # Determine latest version
        latest_entry = max(entries, key=lambda x: x["version"])
        metadata = ModelMetadata(**latest_entry)
        file_path = Path(metadata.file_path)
        # Load model
        if metadata.model_type == "sklearn":
            model = joblib.load(file_path)
        elif metadata.model_type == "keras":
            if tf is None:
                raise RuntimeError(
                    "TensorFlow is not installed; cannot load Keras models."
                )
            model = tf.keras.models.load_model(file_path)
        else:
            raise ValueError(f"Unsupported model_type: {metadata.model_type}")
        return model, metadata
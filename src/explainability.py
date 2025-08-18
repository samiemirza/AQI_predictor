"""
Model explainability utilities (optional SHAP integration).

This module provides helper functions to compute global and local SHAP
explanations for tree-based models and scikit-learn pipelines. It is
designed to be entirely optional: if SHAP is not available in the
environment, functions will raise a clear ImportError with guidance.
"""

from __future__ import annotations

from typing import Dict, Optional
import numpy as np


def _import_shap():
    try:
        import shap  # type: ignore
        return shap
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "SHAP is not installed. Install it with `pip install shap` to enable explainability."
        ) from exc


def compute_global_importance(model: object, X: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Compute global SHAP feature importances for a fitted model.

    Returns a dictionary with `mean_abs_shap` and `shap_values` arrays.
    """
    shap = _import_shap()

    # Try TreeExplainer first (RandomForest), fall back to KernelExplainer
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
    except Exception:
        # KernelExplainer can be slow; use a small background subset
        background = X[np.random.choice(X.shape[0], min(100, X.shape[0]), replace=False)]
        explainer = shap.KernelExplainer(model.predict, background)
        shap_values = explainer.shap_values(X, nsamples=200)

    # For regressors, shap_values is an array; take absolute mean per feature
    values = np.array(shap_values)
    if values.ndim == 3:
        # Some models return (classes, samples, features); aggregate over classes
        values = values.mean(axis=0)
    mean_abs = np.mean(np.abs(values), axis=0)
    return {"mean_abs_shap": mean_abs, "shap_values": values}


def compute_local_explanations(model: object, X: np.ndarray, index: int) -> np.ndarray:
    """
    Compute local SHAP values for a single sample `index`.
    Returns a 1D array of SHAP values per feature.
    """
    shap = _import_shap()
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X[index : index + 1])
    except Exception:
        background = X[np.random.choice(X.shape[0], min(100, X.shape[0]), replace=False)]
        explainer = shap.KernelExplainer(model.predict, background)
        shap_values = explainer.shap_values(X[index : index + 1], nsamples=200)

    values = np.array(shap_values)
    if values.ndim == 3:
        values = values.mean(axis=0)
    return values.reshape(-1)



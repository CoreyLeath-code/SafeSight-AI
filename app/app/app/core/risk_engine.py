"""Compatibility wrapper around the release-supported SafeSight risk policy."""

from typing import List

from safesight.policy import RiskPolicy


def compute_risk(predictions: List[List[float]]) -> str:
    """Return the deterministic policy label for a prediction-score row."""
    return RiskPolicy().classify_predictions(predictions).level.value

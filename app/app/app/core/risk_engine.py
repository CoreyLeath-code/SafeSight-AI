"""Compatibility wrapper around the release-supported SafeSight risk policy."""

from safesight.policy import RiskPolicy


def compute_risk(predictions: list[list[float]]) -> str:
    """Return the deterministic policy label for a prediction-score row."""
    return RiskPolicy().classify_predictions(predictions).level.value

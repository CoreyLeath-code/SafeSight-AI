import math

import pytest

from safesight.policy import RiskLevel, RiskPolicy


def test_default_threshold_boundaries_are_explicit():
    policy = RiskPolicy()
    assert policy.classify(0.0).level is RiskLevel.LOW
    assert policy.classify(0.599999).level is RiskLevel.LOW
    assert policy.classify(0.60).level is RiskLevel.MEDIUM
    assert policy.classify(0.849999).level is RiskLevel.MEDIUM
    assert policy.classify(0.85).level is RiskLevel.HIGH
    assert policy.classify(1.0).level is RiskLevel.HIGH


def test_custom_thresholds_are_supported():
    policy = RiskPolicy(medium_threshold=0.4, high_threshold=0.7)
    decision = policy.classify(0.7)
    assert decision.level is RiskLevel.HIGH
    assert decision.medium_threshold == 0.4
    assert decision.high_threshold == 0.7


@pytest.mark.parametrize("value", [-0.1, 1.1, math.inf, -math.inf, math.nan, "bad", None])
def test_invalid_confidence_is_rejected(value):
    with pytest.raises(ValueError):
        RiskPolicy().classify(value)


@pytest.mark.parametrize(
    ("medium", "high"),
    [(0.8, 0.8), (0.9, 0.8), (-0.1, 0.8), (0.5, 1.1), (math.nan, 0.8)],
)
def test_invalid_threshold_configuration_is_rejected(medium, high):
    with pytest.raises(ValueError):
        RiskPolicy(medium_threshold=medium, high_threshold=high)


def test_prediction_shape_classifies_maximum_score():
    decision = RiskPolicy().classify_predictions([[0.1, 0.86, 0.04]])
    assert decision.level is RiskLevel.HIGH
    assert decision.confidence == 0.86


def test_empty_prediction_shape_is_rejected():
    with pytest.raises(ValueError):
        RiskPolicy().classify_predictions([])
    with pytest.raises(ValueError):
        RiskPolicy().classify_predictions([[]])

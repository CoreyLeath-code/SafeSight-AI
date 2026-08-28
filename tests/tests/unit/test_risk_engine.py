import pytest

from safesight.policy import RiskLevel, RiskPolicy


def test_high_risk():
    assert RiskPolicy().classify_predictions([[0.9, 0.1]]).level is RiskLevel.HIGH


def test_medium_risk():
    assert RiskPolicy().classify_predictions([[0.7, 0.3]]).level is RiskLevel.MEDIUM


def test_low_risk():
    assert RiskPolicy().classify_predictions([[0.4, 0.59]]).level is RiskLevel.LOW


def test_empty_predictions_raises():
    with pytest.raises(ValueError):
        RiskPolicy().classify_predictions([])


def test_empty_inner_list_raises():
    with pytest.raises(ValueError):
        RiskPolicy().classify_predictions([[]])

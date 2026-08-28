import pytest

from src.detector import SafetyDetector


def test_detection_output_is_deterministic_synthetic_fixture():
    detector = SafetyDetector()
    events = detector.run_detection()
    assert events == [
        {"zone": "Warehouse A", "risk": 0.82, "type": "Slip Hazard"},
        {"zone": "Site B", "risk": 0.91, "type": "No PPE"},
    ]


def test_detection_event_contract_and_risk_range():
    for event in SafetyDetector().run_detection():
        assert set(event) == {"zone", "risk", "type"}
        assert 0.0 <= event["risk"] <= 1.0


def test_custom_threshold_filters_events(monkeypatch):
    monkeypatch.setenv("DETECTION_THRESHOLD", "0.90")
    events = SafetyDetector().run_detection()
    assert events == [{"zone": "Site B", "risk": 0.91, "type": "No PPE"}]


@pytest.mark.parametrize("value", ["bad", "-0.1", "1.1", "nan", "inf"])
def test_invalid_threshold_fails_closed(monkeypatch, value):
    monkeypatch.setenv("DETECTION_THRESHOLD", value)
    with pytest.raises(ValueError):
        SafetyDetector()

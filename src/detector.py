"""Deterministic synthetic event fixture used by the legacy demo loop.

This is not a computer-vision detector. It exists only to exercise downstream
alerting behavior without fabricating model-backed detections.
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List


_SYNTHETIC_EVENTS: tuple[dict[str, Any], ...] = (
    {"zone": "Warehouse A", "risk": 0.82, "type": "Slip Hazard"},
    {"zone": "Site B", "risk": 0.91, "type": "No PPE"},
)


class SafetyDetector:
    """Filter deterministic synthetic events through a configured threshold."""

    def __init__(self) -> None:
        raw = os.environ.get("DETECTION_THRESHOLD", "0.75")
        try:
            threshold = float(raw)
        except ValueError as exc:
            raise ValueError("DETECTION_THRESHOLD must be a number in [0, 1]") from exc
        if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
            raise ValueError("DETECTION_THRESHOLD must be a finite number in [0, 1]")
        self.threshold = threshold

    def run_detection(self) -> List[Dict[str, Any]]:
        """Return copies of synthetic events meeting the configured threshold."""
        return [dict(event) for event in _SYNTHETIC_EVENTS if event["risk"] >= self.threshold]

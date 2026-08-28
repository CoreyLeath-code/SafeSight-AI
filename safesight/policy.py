"""Deterministic risk-policy primitives.

This module classifies already-produced confidence scores. It does not perform
computer-vision inference and its outputs are not model-quality evidence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class RiskLevel(str, Enum):
    """Policy labels emitted by :class:`RiskPolicy`."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskDecision:
    """A risk-policy result for one confidence value."""

    level: RiskLevel
    confidence: float
    medium_threshold: float
    high_threshold: float


@dataclass(frozen=True)
class RiskPolicy:
    """Validate confidence values and map them to deterministic risk levels."""

    medium_threshold: float = 0.60
    high_threshold: float = 0.85

    def __post_init__(self) -> None:
        medium = self._validate_probability(self.medium_threshold, "medium_threshold")
        high = self._validate_probability(self.high_threshold, "high_threshold")
        if medium >= high:
            raise ValueError("medium_threshold must be lower than high_threshold")

    @staticmethod
    def _validate_probability(value: float, name: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a finite number in [0, 1]") from exc
        if not math.isfinite(number) or not 0.0 <= number <= 1.0:
            raise ValueError(f"{name} must be a finite number in [0, 1]")
        return number

    def classify(self, confidence: float) -> RiskDecision:
        """Classify one confidence score after validating its numeric domain."""
        score = self._validate_probability(confidence, "confidence")
        if score >= self.high_threshold:
            level = RiskLevel.HIGH
        elif score >= self.medium_threshold:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        return RiskDecision(
            level=level,
            confidence=score,
            medium_threshold=self.medium_threshold,
            high_threshold=self.high_threshold,
        )

    def classify_predictions(self, predictions: Sequence[Sequence[float]]) -> RiskDecision:
        """Classify the maximum score in the first prediction row.

        This compatibility helper makes the policy usable with common
        ``[[score_a, score_b, ...]]`` model-output shapes while remaining
        explicit that SafeSight v0.1.0 does not ship a verified model.
        """
        if not predictions or not predictions[0]:
            raise ValueError("predictions must contain at least one score")
        scores = [
            self._validate_probability(value, "prediction score")
            for value in predictions[0]
        ]
        return self.classify(max(scores))

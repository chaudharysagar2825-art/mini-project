"""Transparent risk rules for Manas Setu.

Rules are explainable decision-support signals.
They must not be treated as clinical diagnoses.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.nlp.crisis_signals import CrisisSignals
from ai.nlp.sentiment_features import SentimentFeatures


@dataclass(frozen=True)
class RiskFactor:
    name: str
    score: float
    reason: str


def evaluate_rules(
    sentiment: SentimentFeatures,
    crisis: CrisisSignals,
) -> list[RiskFactor]:
    """Evaluate transparent rules against extracted NLP features."""

    factors: list[RiskFactor] = []

    if sentiment.negative_score >= 0.10:
        factors.append(
            RiskFactor(
                name="negative_sentiment",
                score=0.15,
                reason="The check-in contains notable negative emotional language.",
            )
        )

    if sentiment.emotional_intensity >= 0.20:
        factors.append(
            RiskFactor(
                name="emotional_intensity",
                score=0.15,
                reason="The check-in contains emotionally intense language.",
            )
        )

    if crisis.distress_signal:
        factors.append(
            RiskFactor(
                name="distress_signal",
                score=0.20,
                reason="The text contains a distress-related signal.",
            )
        )

    if crisis.hopelessness_signal:
        factors.append(
            RiskFactor(
                name="hopelessness_signal",
                score=0.25,
                reason="The text contains language associated with hopelessness or helplessness.",
            )
        )

    if crisis.fear_signal:
        factors.append(
            RiskFactor(
                name="fear_signal",
                score=0.15,
                reason="The text contains fear or perceived-safety concerns.",
            )
        )

    if crisis.isolation_signal:
        factors.append(
            RiskFactor(
                name="isolation_signal",
                score=0.10,
                reason="The text contains indications of loneliness or isolation.",
            )
        )

    if crisis.overwhelming_stress_signal:
        factors.append(
            RiskFactor(
                name="overwhelming_stress",
                score=0.20,
                reason="The text indicates difficulty coping with current stress.",
            )
        )

    if crisis.support_request_signal:
        factors.append(
            RiskFactor(
                name="support_request",
                score=0.10,
                reason="The person appears to be requesting support.",
            )
        )

    return factors


def calculate_rule_score(factors: list[RiskFactor]) -> float:
    """Combine rule contributions into a bounded 0-1 score."""

    score = sum(factor.score for factor in factors)

    return round(min(score, 1.0), 3)
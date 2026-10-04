"""Risk scoring engine for Manas Setu.

The score is a decision-support indicator for authorized human review.
It is not a clinical diagnosis or an autonomous emergency decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ai.nlp.crisis_signals import CrisisSignals
from ai.nlp.sentiment_features import SentimentFeatures
from ai.risk_engine.rules import RiskFactor, calculate_rule_score, evaluate_rules


RiskLevel = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class RiskAssessment:
    """Structured result produced by the risk engine."""

    score: float
    level: RiskLevel
    factors: tuple[RiskFactor, ...]
    requires_human_review: bool
    model_version: str


MODEL_VERSION = "manas-setu-rule-engine-v1"


def classify_risk(score: float) -> RiskLevel:
    """Convert a normalized score into a review category."""

    if score < 0.30:
        return "low"

    if score < 0.60:
        return "moderate"

    return "high"


def assess_risk(
    sentiment: SentimentFeatures,
    crisis: CrisisSignals,
) -> RiskAssessment:
    """Generate a transparent risk assessment."""

    factors = evaluate_rules(sentiment, crisis)
    score = calculate_rule_score(factors)
    level = classify_risk(score)

    # Every non-low result should receive human review.
    # High-risk results should never be interpreted as an automated diagnosis.
    requires_human_review = level in {"moderate", "high"}

    return RiskAssessment(
        score=score,
        level=level,
        factors=tuple(factors),
        requires_human_review=requires_human_review,
        model_version=MODEL_VERSION,
    )


def assess_text(text: str) -> RiskAssessment:
    """Run the complete NLP-to-risk pipeline for one check-in."""

    from ai.nlp.crisis_signals import detect_crisis_signals
    from ai.nlp.sentiment_features import extract_sentiment_features

    sentiment = extract_sentiment_features(text)
    crisis = detect_crisis_signals(text)

    return assess_risk(sentiment, crisis)


if __name__ == "__main__":
    examples = [
        "I feel calm and supported today.",
        "I am stressed and worried about everything.",
        "I feel overwhelmed and alone and I need help.",
    ]

    for text in examples:
        result = assess_text(text)

        print(f"Text: {text}")
        print(f"Score: {result.score}")
        print(f"Level: {result.level}")
        print(f"Human review: {result.requires_human_review}")
        print(f"Model: {result.model_version}")
        print("Factors:")

        for factor in result.factors:
            print(f"  - {factor.name}: {factor.reason}")

        print()
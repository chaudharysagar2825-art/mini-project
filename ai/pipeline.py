"""Unified AI pipeline for Manas Setu.

This module combines language detection, NLP signal extraction,
risk scoring, and explainability into one decision-support pipeline.

It is not a clinical diagnostic system.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.nlp.crisis_signals import CrisisSignals, detect_crisis_signals
from ai.nlp.language_detection import LanguageResult, detect_language
from ai.nlp.sentiment_features import (
    SentimentFeatures,
    extract_sentiment_features,
)
from ai.risk_engine.explainability import RiskExplanation, explain_assessment
from ai.risk_engine.scoring import RiskAssessment, assess_text


@dataclass(frozen=True)
class AIPipelineResult:
    """Complete result produced by the Manas Setu AI pipeline."""

    language: LanguageResult
    sentiment: SentimentFeatures
    crisis_signals: CrisisSignals
    risk_assessment: RiskAssessment
    explanation: RiskExplanation


def analyze_checkin(text: str) -> AIPipelineResult:
    """Run the complete AI analysis pipeline for one check-in."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if not text.strip():
        raise ValueError("text cannot be empty.")

    language = detect_language(text)
    sentiment = extract_sentiment_features(text)
    crisis_signals = detect_crisis_signals(text)
    risk_assessment = assess_text(text)
    explanation = explain_assessment(risk_assessment)

    return AIPipelineResult(
        language=language,
        sentiment=sentiment,
        crisis_signals=crisis_signals,
        risk_assessment=risk_assessment,
        explanation=explanation,
    )


def print_result(result: AIPipelineResult) -> None:
    """Print a readable representation of the pipeline result."""

    print("Manas Setu AI Analysis")
    print("======================")

    print(f"Language: {result.language.language}")
    print(f"Language confidence: {result.language.confidence}")
    print(f"Language method: {result.language.method}")

    print()
    print("Sentiment")
    print("---------")
    print(f"Positive score: {result.sentiment.positive_score}")
    print(f"Negative score: {result.sentiment.negative_score}")
    print(f"Emotional intensity: {result.sentiment.emotional_intensity}")
    print(f"Polarity: {result.sentiment.polarity}")
    print(f"Uncertainty: {result.sentiment.uncertainty}")

    print()
    print("Distress Signals")
    print("----------------")
    print(f"Signal count: {result.crisis_signals.signal_count}")
    print(
        f"Matched signals: "
        f"{result.crisis_signals.matched_signals}"
    )

    print()
    print("Risk Assessment")
    print("---------------")
    print(f"Score: {result.risk_assessment.score}")
    print(f"Level: {result.risk_assessment.level}")
    print(
        "Human review required: "
        f"{result.risk_assessment.requires_human_review}"
    )
    print(f"Model: {result.risk_assessment.model_version}")

    print()
    print("Explanation")
    print("-----------")
    print(result.explanation.summary)

    for factor in result.explanation.factors:
        print(f"- {factor}")


if __name__ == "__main__":
    examples = [
        "I feel calm and supported today.",
        "I am stressed and worried about what will happen.",
        "I feel overwhelmed and alone and I need help.",
    ]

    for text in examples:
        print(f"\nCheck-in: {text}\n")

        result = analyze_checkin(text)

        print_result(result)

        print("\n" + "=" * 50)
"""AI integration service for Manas Setu.

Connects the backend check-in flow to the AI pipeline.

The AI output is decision-support information only.
It does not independently create alerts, diagnoses,
or emergency decisions.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.pipeline import AIPipelineResult, analyze_checkin


@dataclass(frozen=True)
class AIAnalysisResult:
    """Backend-friendly representation of an AI analysis."""

    pipeline_result: AIPipelineResult
    analyzed_text: str


def _combine_answers(answers: dict[str, str]) -> str:
    """Combine textual questionnaire answers into one analysis input."""

    parts: list[str] = []

    for question_id, answer in answers.items():
        normalized_answer = str(answer).strip()

        if not normalized_answer:
            continue

        parts.append(
            f"{question_id}: {normalized_answer}"
        )

    return "\n".join(parts)


def analyze_checkin_answers(
    answers: dict[str, str],
) -> AIAnalysisResult:
    """Run the AI pipeline against questionnaire answers."""

    if not isinstance(answers, dict):
        raise TypeError("answers must be a dictionary.")

    analyzed_text = _combine_answers(answers)

    if not analyzed_text:
        raise ValueError(
            "No textual check-in answers were available "
            "for AI analysis."
        )

    result = analyze_checkin(analyzed_text)

    return AIAnalysisResult(
        pipeline_result=result,
        analyzed_text=analyzed_text,
    )


def get_ai_summary(
    result: AIAnalysisResult,
) -> dict[str, object]:
    """Convert the AI result into a backend-friendly summary."""

    pipeline = result.pipeline_result

    return {
        "language": pipeline.language.language,
        "language_confidence": pipeline.language.confidence,
        "sentiment": {
            "positive_score": pipeline.sentiment.positive_score,
            "negative_score": pipeline.sentiment.negative_score,
            "emotional_intensity": (
                pipeline.sentiment.emotional_intensity
            ),
            "polarity": pipeline.sentiment.polarity,
            "uncertainty": pipeline.sentiment.uncertainty,
        },
        "crisis_signals": {
            "signal_count": pipeline.crisis_signals.signal_count,
            "matched_signals": list(
                pipeline.crisis_signals.matched_signals
            ),
        },
        "risk": {
            "score": pipeline.risk_assessment.score,
            "level": pipeline.risk_assessment.level,
            "human_review_required": (
                pipeline.risk_assessment.requires_human_review
            ),
            "model_version": (
                pipeline.risk_assessment.model_version
            ),
        },
        "explanation": pipeline.explanation.summary,
        "factors": list(pipeline.explanation.factors),
    }
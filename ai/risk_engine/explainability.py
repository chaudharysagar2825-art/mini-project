"""Explainability utilities for Manas Setu.

This module converts risk-engine factors into clear, human-readable
explanations for authorized reviewers.

These explanations are decision-support information, not clinical diagnoses.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.risk_engine.rules import RiskFactor
from ai.risk_engine.scoring import RiskAssessment


@dataclass(frozen=True)
class RiskExplanation:
    """Human-readable explanation of a risk assessment."""

    summary: str
    factors: tuple[str, ...]
    review_required: bool
    model_version: str


def explain_assessment(
    assessment: RiskAssessment,
) -> RiskExplanation:
    """Convert a risk assessment into an interpretable explanation."""

    if assessment.level == "low":
        summary = (
            "The current check-in produced a low decision-support "
            "risk score. No additional automated escalation is indicated."
        )
    elif assessment.level == "moderate":
        summary = (
            "The current check-in produced a moderate decision-support "
            "risk score and should receive human review."
        )
    else:
        summary = (
            "The current check-in produced a high decision-support "
            "risk score and requires human review."
        )

    factors = tuple(
        f"{factor.name}: {factor.reason}"
        for factor in assessment.factors
    )

    return RiskExplanation(
        summary=summary,
        factors=factors,
        review_required=assessment.requires_human_review,
        model_version=assessment.model_version,
    )


def format_explanation(
    assessment: RiskAssessment,
) -> str:
    """Create a readable explanation for a reviewer."""

    explanation = explain_assessment(assessment)

    lines = [
        "Risk Assessment",
        "----------------",
        f"Score: {assessment.score}",
        f"Level: {assessment.level}",
        f"Human review required: {explanation.review_required}",
        f"Model version: {explanation.model_version}",
        "",
        f"Summary: {explanation.summary}",
        "",
        "Contributing factors:",
    ]

    if explanation.factors:
        lines.extend(
            f"- {factor}"
            for factor in explanation.factors
        )
    else:
        lines.append("- No significant rule-based factors detected.")

    return "\n".join(lines)


if __name__ == "__main__":
    from ai.risk_engine.scoring import assess_text

    examples = [
        "I feel calm and supported today.",
        "I am stressed and worried about everything.",
        "I feel overwhelmed and alone and I need help.",
    ]

    for text in examples:
        assessment = assess_text(text)

        print(f"Text: {text}")
        print(format_explanation(assessment))
        print()
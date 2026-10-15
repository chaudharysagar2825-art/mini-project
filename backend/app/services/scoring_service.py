from dataclasses import dataclass

from app.services.risk_engine import (
    RiskSignal,
    calculate_distress_score,
)


@dataclass
class RiskResult:
    risk_level: str
    direction: str
    score: int
    confidence: float
    reason: str
    model_version: str
    risk_category: str = "low"


MODEL_VERSION = "rule-v1"


def map_risk_category(risk_level: str, score: int) -> str:
    """Map internal risk_level and score (scale 0-10) to mutually exclusive 4-tier category.

    Documented Distress Scale (0-10):
    - Low: 0–3
    - Moderate: greater than 3 and below 7 (scores 4, 5, 6)
    - High: 7 and below 8 (score 7)
    - Urgent: 8–10 (or direct safety escalation rule)
    """
    if risk_level == "urgent":
        return "urgent"
    if score >= 8:
        return "urgent"
    if 7 <= score < 8 or risk_level == "high":
        return "high"
    if 3 < score < 7 or risk_level == "follow_up":
        return "moderate"
    return "low"



def calculate_risk(
    distress_score: int,
    baseline_score: int | None = None,
    direct_safety_concern: bool | None = None,
    missing_data: bool = False,
) -> RiskResult:
    """Calculate structured risk assessment from distress score (0-10 scale)."""
    score = max(0, min(distress_score, 10))


    reasons = []

    if direct_safety_concern is True:
        risk_level = "urgent"
        reasons.append("Direct safety concern reported")

    else:
        if baseline_score is not None:
            change = score - baseline_score

            if change >= 3:
                reasons.append(
                    f"Distress increased by {change} points from baseline"
                )

            elif change <= -3:
                reasons.append(
                    f"Distress decreased by {abs(change)} points from baseline"
                )

        if score >= 8:
            risk_level = "urgent"
            reasons.append("High distress score")

        elif score >= 5:
            risk_level = "follow_up"
            reasons.append("Moderate distress score")

        else:
            risk_level = "routine"
            reasons.append("Low distress score")

    if baseline_score is None:
        direction = "unknown"

    elif score > baseline_score:
        direction = "worsening"

    elif score < baseline_score:
        direction = "improving"

    else:
        direction = "stable"

    confidence = 0.9

    if missing_data:
        confidence = 0.5
        reasons.append("Incomplete check-in: some questions were omitted or skipped; provisional score requires caseworker review")

    risk_category = map_risk_category(risk_level, score)

    return RiskResult(
        risk_level=risk_level,
        direction=direction,
        score=score,
        confidence=confidence,
        reason="; ".join(reasons),
        model_version=MODEL_VERSION,
        risk_category=risk_category,
    )



def evaluate_checkin(
    answers: dict[str, str],
    baseline_score: int | None = None,
    safety_question_ids: set[str] | None = None,
) -> RiskResult:

    signal: RiskSignal = calculate_distress_score(
        answers=answers,
        safety_question_ids=safety_question_ids,
    )

    return calculate_risk(
        distress_score=signal.distress_score,
        baseline_score=baseline_score,
        direct_safety_concern=signal.direct_safety_concern,
        missing_data=signal.missing_data,
    )
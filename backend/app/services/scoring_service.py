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


MODEL_VERSION = "rule-v1"


def calculate_risk(
    distress_score: int,
    baseline_score: int | None = None,
    direct_safety_concern: bool | None = None,
    missing_data: bool = False,
) -> RiskResult:

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
        confidence = 0.6
        reasons.append("Some check-in data is missing")

    return RiskResult(
        risk_level=risk_level,
        direction=direction,
        score=score,
        confidence=confidence,
        reason="; ".join(reasons),
        model_version=MODEL_VERSION,
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
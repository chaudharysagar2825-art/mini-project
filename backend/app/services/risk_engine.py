from dataclasses import dataclass


@dataclass
class RiskSignal:
    distress_score: int
    direct_safety_concern: bool | None
    missing_data: bool
    reason: str


MODEL_VERSION = "risk-engine-v1"


def calculate_distress_score(
    answers: dict[str, str],
    safety_question_ids: set[str] | None = None,
) -> RiskSignal:

    safety_question_ids = safety_question_ids or set()

    if not answers:
        return RiskSignal(
            distress_score=0,
            direct_safety_concern=None,
            missing_data=True,
            reason="No check-in answers were provided",
        )

    score = 0
    answered_count = 0
    direct_safety_concern = False

    for question_id, answer in answers.items():

        if not answer or not answer.strip():
            continue

        answered_count += 1
        normalized = answer.strip().lower()

        if question_id in safety_question_ids:
            if normalized in {
                "yes",
                "y",
                "true",
                "1",
            }:
                direct_safety_concern = True

        if normalized in {
            "not at all",
            "none",
            "never",
            "no",
            "0",
        }:
            score += 0

        elif normalized in {
            "sometimes",
            "mild",
            "low",
            "1",
        }:
            score += 1

        elif normalized in {
            "often",
            "moderate",
            "medium",
            "2",
        }:
            score += 2

        elif normalized in {
            "almost always",
            "severe",
            "high",
            "3",
        }:
            score += 3

    missing_data = answered_count < len(answers)

    score = min(score, 10)

    if direct_safety_concern:
        reason = "Direct safety concern reported"
    elif missing_data:
        reason = "Some check-in data is missing"
    else:
        reason = "Distress signal calculated from check-in responses"

    return RiskSignal(
        distress_score=score,
        direct_safety_concern=direct_safety_concern,
        missing_data=missing_data,
        reason=reason,
    )

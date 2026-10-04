"""Trend features for Manas Setu.

These features describe changes in risk-related signals over time.
They are decision-support indicators and are not clinical diagnoses.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskObservation:
    """Risk information from one historical check-in."""

    score: float
    timestamp: str


@dataclass(frozen=True)
class TrendFeatures:
    """Calculated changes across recent risk observations."""

    current_score: float
    previous_score: float
    score_change: float
    average_score: float
    rising_trend: bool
    observation_count: int


def calculate_trend(
    observations: list[RiskObservation],
) -> TrendFeatures:
    """Calculate simple interpretable risk trends.

    Observations should be ordered from oldest to newest.
    """

    if not observations:
        return TrendFeatures(
            current_score=0.0,
            previous_score=0.0,
            score_change=0.0,
            average_score=0.0,
            rising_trend=False,
            observation_count=0,
        )

    scores = [
        max(0.0, min(1.0, observation.score))
        for observation in observations
    ]

    current_score = scores[-1]

    previous_score = scores[-2] if len(scores) >= 2 else current_score

    score_change = current_score - previous_score

    average_score = sum(scores) / len(scores)

    rising_trend = (
        len(scores) >= 2
        and score_change >= 0.10
    )

    return TrendFeatures(
        current_score=round(current_score, 3),
        previous_score=round(previous_score, 3),
        score_change=round(score_change, 3),
        average_score=round(average_score, 3),
        rising_trend=rising_trend,
        observation_count=len(scores),
    )


if __name__ == "__main__":
    observations = [
        RiskObservation(0.15, "2026-10-01T10:00:00"),
        RiskObservation(0.25, "2026-10-02T10:00:00"),
        RiskObservation(0.45, "2026-10-03T10:00:00"),
    ]

    result = calculate_trend(observations)

    print("Trend analysis")
    print(f"Current score: {result.current_score}")
    print(f"Previous score: {result.previous_score}")
    print(f"Score change: {result.score_change}")
    print(f"Average score: {result.average_score}")
    print(f"Rising trend: {result.rising_trend}")
    print(f"Observations: {result.observation_count}")
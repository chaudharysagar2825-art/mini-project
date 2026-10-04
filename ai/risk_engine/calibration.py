"""Risk-score calibration utilities for Manas Setu.

The current implementation provides a transparent normalization layer.
It does not claim clinical validity or statistical calibration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationResult:
    """Result of normalizing a raw risk score."""

    raw_score: float
    calibrated_score: float
    method: str


def calibrate_score(
    raw_score: float,
) -> CalibrationResult:
    """Normalize a risk score to the range 0.0-1.0."""

    calibrated_score = max(
        0.0,
        min(1.0, raw_score),
    )

    return CalibrationResult(
        raw_score=round(raw_score, 3),
        calibrated_score=round(calibrated_score, 3),
        method="bounded_normalization_v1",
    )


if __name__ == "__main__":
    examples = [
        0.15,
        0.45,
        0.85,
        1.20,
        -0.10,
    ]

    for score in examples:
        result = calibrate_score(score)

        print(
            f"Raw: {result.raw_score} | "
            f"Calibrated: {result.calibrated_score} | "
            f"Method: {result.method}"
        )
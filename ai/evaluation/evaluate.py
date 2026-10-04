"""Evaluation runner for the Manas Setu AI prototype.

This module evaluates the rule-based risk engine against synthetic
development cases. It must not be used as clinical validation.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai.evaluation.metrics import calculate_metrics
from ai.risk_engine.scoring import assess_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "ai" / "data" / "synthetic_cases.json"


def load_cases() -> list[dict]:
    """Load synthetic evaluation cases from JSON."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Synthetic dataset not found: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "synthetic_cases.json must contain a JSON list."
        )

    return data


def evaluate_cases(cases: list[dict]) -> tuple[list[int], list[int]]:
    """Run the risk engine against all supplied cases."""

    actual: list[int] = []
    predicted: list[int] = []

    for case in cases:
        text = str(case.get("text", "")).strip()

        if not text:
            continue

        expected = case.get("expected_high_risk")

        if expected is None:
            continue

        assessment = assess_text(text)

        actual.append(1 if bool(expected) else 0)
        predicted.append(
            1 if assessment.level == "high" else 0
        )

    return actual, predicted


def main() -> None:
    """Run the complete synthetic-data evaluation."""

    cases = load_cases()

    actual, predicted = evaluate_cases(cases)

    metrics = calculate_metrics(
        actual=actual,
        predicted=predicted,
    )

    print("Manas Setu AI Evaluation")
    print("========================")
    print(f"Cases evaluated: {len(actual)}")
    print()
    print(f"Accuracy:  {metrics.accuracy}")
    print(f"Precision: {metrics.precision}")
    print(f"Recall:    {metrics.recall}")
    print(f"F1 score:  {metrics.f1_score}")


if __name__ == "__main__":
    main()
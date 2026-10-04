"""Evaluation metrics for the Manas Setu AI prototype.

These metrics are intended for development and testing on synthetic data.
They are not clinical validation metrics.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationMetrics:
    """Basic binary classification metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float


def calculate_metrics(
    actual: list[int],
    predicted: list[int],
) -> ClassificationMetrics:
    """Calculate basic binary classification metrics.

    Labels must be 0 or 1.
    """

    if len(actual) != len(predicted):
        raise ValueError(
            "actual and predicted must contain the same number of values."
        )

    if not actual:
        return ClassificationMetrics(
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
        )

    if any(value not in {0, 1} for value in actual + predicted):
        raise ValueError("Labels must be either 0 or 1.")

    true_positive = sum(
        a == 1 and p == 1
        for a, p in zip(actual, predicted)
    )

    true_negative = sum(
        a == 0 and p == 0
        for a, p in zip(actual, predicted)
    )

    false_positive = sum(
        a == 0 and p == 1
        for a, p in zip(actual, predicted)
    )

    false_negative = sum(
        a == 1 and p == 0
        for a, p in zip(actual, predicted)
    )

    total = len(actual)

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0.0
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0.0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0.0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return ClassificationMetrics(
        accuracy=round(accuracy, 3),
        precision=round(precision, 3),
        recall=round(recall, 3),
        f1_score=round(f1_score, 3),
    )


if __name__ == "__main__":
    actual = [0, 0, 1, 1, 1]
    predicted = [0, 1, 1, 1, 0]

    result = calculate_metrics(actual, predicted)

    print("Evaluation Metrics")
    print("------------------")
    print(f"Accuracy:  {result.accuracy}")
    print(f"Precision: {result.precision}")
    print(f"Recall:    {result.recall}")
    print(f"F1 score:  {result.f1_score}")
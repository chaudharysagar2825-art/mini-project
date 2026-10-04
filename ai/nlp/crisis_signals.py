"""Distress-signal extraction for Manas Setu.

This module identifies textual indicators that may warrant additional
human review. It does not provide a clinical diagnosis or emergency
determination.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CrisisSignals:
    distress_signal: bool
    hopelessness_signal: bool
    fear_signal: bool
    isolation_signal: bool
    overwhelming_stress_signal: bool
    support_request_signal: bool
    signal_count: int
    matched_signals: tuple[str, ...]


SIGNAL_PATTERNS = {
    "distress": (
        r"\b(distressed|extremely stressed|emotionally exhausted)\b",
    ),
    "hopelessness": (
        r"\b(hopeless|no hope|nothing will get better|feel helpless)\b",
    ),
    "fear": (
        r"\b(afraid|scared|terrified|fearful|feel unsafe)\b",
    ),
    "isolation": (
        r"\b(alone|lonely|isolated|no one understands)\b",
    ),
    "overwhelming_stress": (
        r"\b(overwhelmed|can't cope|cannot cope|too much to handle)\b",
    ),
    "support_request": (
        r"\b(need help|want help|need someone to talk|need support)\b",
    ),
}


def _contains_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    """Return True if any pattern matches the supplied text."""
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def detect_crisis_signals(text: str) -> CrisisSignals:
    """Extract potentially important distress-related signals.

    The returned signals should be treated as decision-support
    features and reviewed in context by an authorized human.
    """

    normalized_text = " ".join(text.strip().split())

    if not normalized_text:
        return CrisisSignals(
            distress_signal=False,
            hopelessness_signal=False,
            fear_signal=False,
            isolation_signal=False,
            overwhelming_stress_signal=False,
            support_request_signal=False,
            signal_count=0,
            matched_signals=(),
        )

    detected = {
        name: _contains_pattern(normalized_text, patterns)
        for name, patterns in SIGNAL_PATTERNS.items()
    }

    matched_signals = tuple(
        name
        for name, detected_signal in detected.items()
        if detected_signal
    )

    return CrisisSignals(
        distress_signal=detected["distress"],
        hopelessness_signal=detected["hopelessness"],
        fear_signal=detected["fear"],
        isolation_signal=detected["isolation"],
        overwhelming_stress_signal=detected["overwhelming_stress"],
        support_request_signal=detected["support_request"],
        signal_count=len(matched_signals),
        matched_signals=matched_signals,
    )


if __name__ == "__main__":
    examples = [
        "I feel overwhelmed and alone.",
        "I am afraid and I need help.",
        "Today I feel calm and supported.",
    ]

    for text in examples:
        print(f"Text: {text}")
        print(detect_crisis_signals(text))
        print()
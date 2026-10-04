"""Sentiment feature extraction for Manas Setu.

These features are decision-support signals only.
They are not clinical diagnoses.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SentimentFeatures:
    positive_score: float
    negative_score: float
    emotional_intensity: float
    polarity: float
    uncertainty: float
    word_count: int


POSITIVE_WORDS = {
    "happy",
    "calm",
    "better",
    "good",
    "hope",
    "hopeful",
    "safe",
    "okay",
    "fine",
    "peaceful",
    "supported",
    "confident",
    "relaxed",
    "positive",
    "improving",
}

NEGATIVE_WORDS = {
    "sad",
    "angry",
    "afraid",
    "fear",
    "scared",
    "worried",
    "stress",
    "stressed",
    "anxious",
    "anxiety",
    "lonely",
    "hopeless",
    "helpless",
    "upset",
    "tired",
    "exhausted",
    "hurt",
    "pain",
    "distressed",
    "overwhelmed",
}

INTENSITY_WORDS = {
    "very",
    "extremely",
    "really",
    "completely",
    "deeply",
    "severely",
    "constantly",
    "unable",
}

UNCERTAINTY_WORDS = {
    "maybe",
    "perhaps",
    "might",
    "possibly",
    "unsure",
    "uncertain",
    "sometimes",
}


def _tokenize(text: str) -> list[str]:
    """Convert text into lowercase word tokens."""
    return re.findall(r"[a-zA-Z]+", text.lower())


def _score_words(
    tokens: list[str],
    vocabulary: set[str],
) -> float:
    """Calculate the proportion of tokens matching a vocabulary."""
    if not tokens:
        return 0.0

    matches = sum(token in vocabulary for token in tokens)
    return round(matches / len(tokens), 3)


def extract_sentiment_features(text: str) -> SentimentFeatures:
    """Extract simple interpretable sentiment features."""

    tokens = _tokenize(text)
    word_count = len(tokens)

    if word_count == 0:
        return SentimentFeatures(
            positive_score=0.0,
            negative_score=0.0,
            emotional_intensity=0.0,
            polarity=0.0,
            uncertainty=0.0,
            word_count=0,
        )

    positive_score = _score_words(tokens, POSITIVE_WORDS)
    negative_score = _score_words(tokens, NEGATIVE_WORDS)

    intensity_matches = sum(
        token in INTENSITY_WORDS
        for token in tokens
    )

    uncertainty_matches = sum(
        token in UNCERTAINTY_WORDS
        for token in tokens
    )

    emotional_intensity = min(
        1.0,
        negative_score * 2.0
        + intensity_matches / word_count,
    )

    polarity = max(
        -1.0,
        min(
            1.0,
            positive_score - negative_score,
        ),
    )

    uncertainty = min(
        1.0,
        uncertainty_matches / word_count,
    )

    return SentimentFeatures(
        positive_score=round(positive_score, 3),
        negative_score=round(negative_score, 3),
        emotional_intensity=round(emotional_intensity, 3),
        polarity=round(polarity, 3),
        uncertainty=round(uncertainty, 3),
        word_count=word_count,
    )


if __name__ == "__main__":
    examples = [
        "I feel calm and supported today.",
        "I am very stressed and overwhelmed.",
        "Maybe I am worried about what will happen.",
    ]

    for text in examples:
        print(f"Text: {text}")
        print(extract_sentiment_features(text))
        print()
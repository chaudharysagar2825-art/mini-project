"""Lightweight language detection for Manas Setu."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class LanguageResult:
    language: str
    confidence: float
    method: str


SCRIPT_PATTERNS = {
    "hi": re.compile(r"[\u0900-\u097F]"),  # Devanagari
    "bn": re.compile(r"[\u0980-\u09FF]"),  # Bengali
    "pa": re.compile(r"[\u0A00-\u0A7F]"),  # Gurmukhi
    "gu": re.compile(r"[\u0A80-\u0AFF]"),  # Gujarati
    "ta": re.compile(r"[\u0B80-\u0BFF]"),  # Tamil
    "te": re.compile(r"[\u0C00-\u0C7F]"),  # Telugu
    "kn": re.compile(r"[\u0C80-\u0CFF]"),  # Kannada
    "ml": re.compile(r"[\u0D00-\u0D7F]"),  # Malayalam
}


def detect_language(text: str) -> LanguageResult:
    """Detect the dominant writing system and return a language estimate."""

    text = text.strip()

    if not text:
        return LanguageResult("unknown", 0.0, "empty_input")

    letters = [char for char in text if char.isalpha()]

    if not letters:
        return LanguageResult("unknown", 0.0, "no_letters")

    total = len(letters)

    scores = {
        language: sum(
            bool(pattern.fullmatch(char))
            for char in letters
        ) / total
        for language, pattern in SCRIPT_PATTERNS.items()
    }

    language, confidence = max(scores.items(), key=lambda item: item[1])

    if confidence >= 0.50:
        return LanguageResult(
            language=language,
            confidence=round(confidence, 3),
            method="unicode_script",
        )

    latin_count = sum(
        char.isascii() and char.isalpha()
        for char in letters
    )

    latin_ratio = latin_count / total

    if latin_ratio >= 0.50:
        return LanguageResult(
            language="en",
            confidence=round(latin_ratio, 3),
            method="latin_script",
        )

    return LanguageResult(
        language="unknown",
        confidence=round(confidence, 3),
        method="low_confidence",
    )


if __name__ == "__main__":
    examples = [
        "I am feeling stressed today.",
        "मैं आज बहुत परेशान महसूस कर रहा हूँ।",
        "আজ আমি খুব চিন্তিত।",
    ]

    for text in examples:
        print(text)
        print(detect_language(text))
        print()
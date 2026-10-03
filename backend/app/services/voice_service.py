from dataclasses import dataclass


@dataclass
class VoiceSignal:
    distress_score: int
    confidence: float
    reason: str


def analyze_voice(text: str) -> dict:
    """
    Basic interpretable voice/text signal analysis.

    This is a supporting signal only.
    It must not be treated as a clinical diagnosis.
    """

    if not text or not text.strip():
        raise ValueError("Voice text cannot be empty")

    normalized = text.strip().lower()

    distress_words = {
        "sad",
        "hopeless",
        "scared",
        "afraid",
        "helpless",
        "alone",
        "stressed",
        "stress",
        "anxious",
        "anxiety",
        "depressed",
        "depression",
        "hurt",
        "unsafe",
        "danger",
        "suicide",
        "die",
        "death",
    }

    matched_words = [
        word
        for word in distress_words
        if word in normalized
    ]

    score = min(len(matched_words), 10)

    if score >= 5:
        level = "high"

    elif score >= 2:
        level = "moderate"

    else:
        level = "low"

    if matched_words:
        reason = (
            "Potential distress-related language detected"
        )
        confidence = 0.6
    else:
        reason = (
            "No strong distress-related language detected"
        )
        confidence = 0.4

    return {
        "distress_score": score,
        "risk_signal": level,
        "confidence": confidence,
        "reason": reason,
        "matched_signals": matched_words,
        "model_version": "voice-rule-v1",
    }
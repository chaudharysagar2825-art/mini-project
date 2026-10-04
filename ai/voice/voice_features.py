"""Voice feature extraction for Manas Setu.

These features are non-clinical decision-support signals.
They must not be interpreted as a diagnosis or definitive
assessment of a person's mental state.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceFeatures:
    """Interpretable features derived from voice metadata."""

    duration_seconds: float
    speech_rate: float
    pause_ratio: float
    volume_variability: float


def extract_voice_features(
    duration_seconds: float,
    word_count: int,
    pause_seconds: float = 0.0,
    volume_variability: float = 0.0,
) -> VoiceFeatures:
    """Calculate simple voice features from supplied metadata.

    Parameters:
        duration_seconds: Total recording duration.
        word_count: Number of transcribed words.
        pause_seconds: Estimated total pause duration.
        volume_variability: Normalized variability in speech volume.

    Returns:
        A VoiceFeatures object containing normalized features.
    """

    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than zero.")

    if word_count < 0:
        raise ValueError("word_count cannot be negative.")

    if pause_seconds < 0:
        raise ValueError("pause_seconds cannot be negative.")

    if pause_seconds > duration_seconds:
        raise ValueError(
            "pause_seconds cannot exceed duration_seconds."
        )

    if volume_variability < 0:
        raise ValueError(
            "volume_variability cannot be negative."
        )

    speech_duration = max(
        duration_seconds - pause_seconds,
        0.001,
    )

    speech_rate = word_count / speech_duration

    pause_ratio = pause_seconds / duration_seconds

    return VoiceFeatures(
        duration_seconds=round(duration_seconds, 3),
        speech_rate=round(speech_rate, 3),
        pause_ratio=round(pause_ratio, 3),
        volume_variability=round(volume_variability, 3),
    )


if __name__ == "__main__":
    result = extract_voice_features(
        duration_seconds=60,
        word_count=90,
        pause_seconds=12,
        volume_variability=0.25,
    )

    print("Manas Setu Voice Features")
    print("=========================")
    print(f"Duration: {result.duration_seconds}s")
    print(f"Speech rate: {result.speech_rate} words/sec")
    print(f"Pause ratio: {result.pause_ratio}")
    print(f"Volume variability: {result.volume_variability}")
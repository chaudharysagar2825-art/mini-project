"""Speech-to-text interface for Manas Setu.

This module defines the interface expected by the AI pipeline.
Actual speech recognition can be connected later through a trusted
speech-to-text provider or local model.

No audio is processed by this prototype implementation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeechToTextResult:
    """Result returned by a speech-to-text system."""

    text: str
    language: str
    confidence: float
    provider: str


def transcribe_audio(
    audio_path: str,
    language: str = "auto",
) -> SpeechToTextResult:
    """Transcribe an audio file.

    This is currently a development stub. A real speech-to-text
    implementation should be connected here later.
    """

    if not audio_path.strip():
        raise ValueError("audio_path cannot be empty.")

    if not language.strip():
        raise ValueError("language cannot be empty.")

    raise NotImplementedError(
        "Speech-to-text provider is not connected yet."
    )


if __name__ == "__main__":
    print("Manas Setu Speech-to-Text")
    print("=========================")
    print("Status: interface ready")
    print("Status: speech-to-text provider not connected")
"""
Speech-to-text implementation for Manas Setu.

Uses Faster-Whisper for local speech recognition.

The transcription result is intended to be used as an input
to the AI pipeline. Transcription itself is not a diagnosis
or mental-health assessment.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class SpeechToTextResult:
    """Result returned by the speech-to-text system."""

    text: str
    language: str
    confidence: float
    provider: str


SUPPORTED_AUDIO_FORMATS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm",
    ".flac",
}


_MODEL = None


def _get_model():
    """
    Load the Whisper model lazily.

    The model is loaded only when transcription is requested.
    This prevents the backend from loading the model at startup.
    """

    global _MODEL

    if _MODEL is not None:
        return _MODEL

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. "
            "Install it with: pip install faster-whisper"
        ) from exc

    model_size = os.getenv(
        "STT_MODEL_SIZE",
        "small"
    )

    device = os.getenv(
        "STT_DEVICE",
        "auto"
    )

    compute_type = os.getenv(
        "STT_COMPUTE_TYPE",
        "auto"
    )

    _MODEL = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
    )

    return _MODEL


def validate_audio_file(audio_path: str) -> Path:
    """
    Validate an audio file before transcription.
    """

    if not audio_path or not audio_path.strip():
        raise ValueError(
            "audio_path cannot be empty."
        )

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    if not path.is_file():
        raise ValueError(
            "The supplied audio path is not a file."
        )

    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported formats: "
            f"{', '.join(sorted(SUPPORTED_AUDIO_FORMATS))}"
        )

    return path


def transcribe_audio(
    audio_path: str,
    language: str = "auto",
) -> SpeechToTextResult:
    """
    Transcribe an audio file using Faster-Whisper.

    Parameters
    ----------
    audio_path:
        Path to the audio file.

    language:
        Language code such as:
        - "en" for English
        - "hi" for Hindi
        - "pa" for Punjabi
        - "bn" for Bengali

        Use "auto" for automatic language detection.

    Returns
    -------
    SpeechToTextResult
        Contains transcript, detected language,
        confidence and provider name.
    """

    path = validate_audio_file(audio_path)

    if not language or not language.strip():
        raise ValueError(
            "language cannot be empty."
        )

    model = _get_model()

    language_argument = None

    if language.lower() != "auto":
        language_argument = language.lower()

    segments, info = model.transcribe(
        str(path),
        language=language_argument,
        beam_size=5,
        vad_filter=True,
    )

    transcript_parts = []

    confidence_values = []

    for segment in segments:

        text = segment.text.strip()

        if text:
            transcript_parts.append(text)

        if hasattr(segment, "avg_logprob"):
            confidence_values.append(
                float(segment.avg_logprob)
            )

    transcript = " ".join(
        transcript_parts
    ).strip()

    detected_language = getattr(
        info,
        "language",
        language if language != "auto" else "unknown"
    )

    language_probability = getattr(
        info,
        "language_probability",
        0.0
    )

    confidence = float(
        language_probability or 0.0
    )

    return SpeechToTextResult(
        text=transcript,
        language=detected_language,
        confidence=round(confidence, 4),
        provider="faster-whisper",
    )


if __name__ == "__main__":

    print("Manas Setu Speech-to-Text")
    print("=========================")

    audio_file = input(
        "Enter audio file path: "
    ).strip()

    try:

        result = transcribe_audio(
            audio_file
        )

        print()
        print("Transcription:")
        print(result.text)

        print()
        print("Language:")
        print(result.language)

        print()
        print("Confidence:")
        print(result.confidence)

        print()
        print("Provider:")
        print(result.provider)

    except Exception as exc:

        print()
        print(f"Transcription failed: {exc}")
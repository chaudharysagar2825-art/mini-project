"""Voice & IVR Integration Interface for Manas Setu.

Provides provider-independent handling of interactive telephony events,
DTMF keypress parsing, and callback signature verification.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IVREventResult:
    call_id: str
    caller_phone: str
    event_type: str  # "dtmf_response", "call_completed", "call_initiated"
    answers: dict[str, str] = field(default_factory=dict)
    direct_safety_concern: bool = False
    requested_human_contact: bool = False
    is_valid_signature: bool = True
    is_mock: bool = True
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def verify_ivr_signature(
    secret: str,
    payload_bytes: bytes,
    signature_header: str,
) -> bool:
    """Verify telephony provider HMAC-SHA256 callback signature.

    Returns True if valid or if secret is unset (development mode).
    Returns False if signature does not match.
    """
    if not secret:
        # Development mode without strict signature verification
        return True

    expected = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


class BaseIVRProvider(ABC):
    """Abstract interface for IVR telephony events."""

    @abstractmethod
    def parse_event(
        self,
        payload: dict[str, Any],
        raw_body: bytes = b"",
        signature: str | None = None,
    ) -> IVREventResult:
        """Parse incoming provider callback into standard internal IVREventResult."""
        pass

    @abstractmethod
    def build_call_menu(self, case_code: str, language: str = "hi") -> dict[str, Any]:
        """Generate dynamic telephony voice menu (TwiML / XML / JSON)."""
        pass


class MockIVRProvider(BaseIVRProvider):
    """Simulated IVR provider for local testing and demo interactions."""

    def __init__(self, webhook_secret: str | None = None) -> None:
        self.webhook_secret = webhook_secret or os.getenv("IVR_WEBHOOK_SECRET", "")

    def parse_event(
        self,
        payload: dict[str, Any],
        raw_body: bytes = b"",
        signature: str | None = None,
    ) -> IVREventResult:
        is_valid = True
        if self.webhook_secret and signature:
            is_valid = verify_ivr_signature(self.webhook_secret, raw_body, signature)

        call_id = payload.get("call_id", f"mock-call-{datetime.now().strftime('%H%M%S')}")
        caller = payload.get("caller_phone") or payload.get("From") or ""

        # Map DTMF digits (0-3) to standardized answer categories
        dtmf_map = {
            "0": "none",
            "1": "mild",
            "2": "moderate",
            "3": "severe",
        }

        raw_answers = payload.get("answers", {})
        parsed_answers: dict[str, str] = {}

        if isinstance(raw_answers, dict):
            for q_id, val in raw_answers.items():
                parsed_answers[str(q_id)] = dtmf_map.get(str(val).strip(), str(val).strip())

        # Support direct DTMF string (e.g. "1203" for q1=mild, q2=mod, q3=none, q4=severe)
        digits = payload.get("Digits", "")
        if digits and len(digits) >= 4:
            parsed_answers = {
                "sleep_quality": dtmf_map.get(digits[0], "none"),
                "anxiety_intensity": dtmf_map.get(digits[1], "mild"),
                "isolation_feeling": dtmf_map.get(digits[2], "none"),
                "coping_difficulty": dtmf_map.get(digits[3], "mild"),
            }

        # Check immediate crisis flag (e.g., pressed 9 or direct flag)
        direct_safety = bool(
            payload.get("direct_safety_concern")
            or payload.get("emergency_flag")
            or "9" in digits
        )
        request_contact = bool(
            payload.get("requested_human_contact")
            or payload.get("operator_request")
            or "0" in digits[4:] if len(digits) > 4 else False
        )

        return IVREventResult(
            call_id=call_id,
            caller_phone=caller,
            event_type=payload.get("event_type", "dtmf_response"),
            answers=parsed_answers,
            direct_safety_concern=direct_safety,
            requested_human_contact=request_contact,
            is_valid_signature=is_valid,
            is_mock=True,
        )

    def build_call_menu(self, case_code: str, language: str = "hi") -> dict[str, Any]:
        return {
            "welcome_prompt": "Namaste. This is your Manas Setu daily wellness call.",
            "questions": [
                {"id": "sleep_quality", "prompt": "For sleep disturbance, press 0 for none, 1 for mild, 2 for moderate, 3 for severe."},
                {"id": "anxiety_intensity", "prompt": "For anxiety or distress, press 0 to 3."},
                {"id": "isolation_feeling", "prompt": "For loneliness or isolation, press 0 to 3."},
                {"id": "coping_difficulty", "prompt": "For difficulty managing daily tasks, press 0 to 3."},
            ],
            "emergency_prompt": "Press 9 at any time to connect immediately with a caseworker or crisis support.",
            "language": language,
            "provider": "MockIVRProvider",
        }


_DEFAULT_IVR_PROVIDER: BaseIVRProvider | None = None


def get_ivr_provider() -> BaseIVRProvider:
    """Return configured IVR provider."""
    global _DEFAULT_IVR_PROVIDER
    if _DEFAULT_IVR_PROVIDER is None:
        _DEFAULT_IVR_PROVIDER = MockIVRProvider()
    return _DEFAULT_IVR_PROVIDER

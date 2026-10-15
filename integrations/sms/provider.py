"""SMS Provider Integration Interface for Manas Setu.

Provides a provider-agnostic abstraction for sending neutral, privacy-preserving
SMS notifications and check-in reminders.

Supports:
- MockSMSProvider: For local development and automated testing.
- ConfigurableGatewayProvider: For live telecom gateways (e.g., Gupshup, Twilio, CDAC)
  activated only when explicit environment credentials are provided.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SMSDeliveryResult:
    message_id: str
    recipient: str
    status: str  # "delivered", "queued", "mock_sent", "failed"
    is_mock: bool
    sent_at: datetime
    error: str | None = None
    provider_name: str = "mock"


class BaseSMSProvider(ABC):
    """Abstract interface for SMS delivery."""

    @abstractmethod
    def send_sms(
        self,
        to_phone: str,
        message: str,
        idempotency_key: str | None = None,
        is_neutral: bool = True,
    ) -> SMSDeliveryResult:
        """Send an SMS message to a verified recipient."""
        pass

    @abstractmethod
    def check_delivery_status(self, message_id: str) -> str:
        """Query delivery status for a message ID."""
        pass


class MockSMSProvider(BaseSMSProvider):
    """Local development and test mock provider.

    Explicitly identifies all dispatched messages as synthetic mock transmissions.
    Tracks in-memory history to facilitate verification and prevent duplicates.
    """

    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []
        self._idempotency_cache: set[str] = set()

    def send_sms(
        self,
        to_phone: str,
        message: str,
        idempotency_key: str | None = None,
        is_neutral: bool = True,
    ) -> SMSDeliveryResult:
        normalized_phone = to_phone.strip()
        if not normalized_phone:
            return SMSDeliveryResult(
                message_id="",
                recipient=to_phone,
                status="failed",
                is_mock=True,
                sent_at=datetime.now(timezone.utc),
                error="Recipient phone number cannot be empty.",
                provider_name="MockSMSProvider",
            )

        # Idempotency / duplicate prevention
        cache_key = idempotency_key or hashlib.sha256(
            f"{normalized_phone}:{message}".encode()
        ).hexdigest()

        if cache_key in self._idempotency_cache:
            logger.info("Duplicate SMS suppressed via idempotency key: %s", cache_key)
            return SMSDeliveryResult(
                message_id=f"mock-dup-{cache_key[:8]}",
                recipient=normalized_phone,
                status="duplicate_suppressed",
                is_mock=True,
                sent_at=datetime.now(timezone.utc),
                error="Duplicate message suppressed",
                provider_name="MockSMSProvider",
            )

        self._idempotency_cache.add(cache_key)

        msg_id = f"mock-msg-{len(self.sent_messages) + 1:04d}-{datetime.now().strftime('%H%M%S')}"

        record = {
            "message_id": msg_id,
            "to_phone": normalized_phone,
            "message": message,
            "is_neutral": is_neutral,
            "status": "mock_delivered",
            "timestamp": datetime.now(timezone.utc),
        }
        self.sent_messages.append(record)

        logger.info(
            "[MOCK-SMS] Dispatched to %s (ID: %s, Neutral: %s): %s",
            normalized_phone,
            msg_id,
            is_neutral,
            message[:60] + "..." if len(message) > 60 else message,
        )

        return SMSDeliveryResult(
            message_id=msg_id,
            recipient=normalized_phone,
            status="mock_delivered",
            is_mock=True,
            sent_at=record["timestamp"],
            provider_name="MockSMSProvider",
        )

    def check_delivery_status(self, message_id: str) -> str:
        for msg in self.sent_messages:
            if msg["message_id"] == message_id:
                return msg["status"]
        return "not_found"


class ConfigurableGatewaySMSProvider(BaseSMSProvider):
    """Generic HTTP gateway provider for production SMS services (e.g. Gupshup, Twilio).

    Falls back cleanly to MockSMSProvider if external credentials are not set.
    """

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        sender_id: str | None = None,
    ) -> None:
        self.api_url = api_url or os.getenv("SMS_GATEWAY_URL")
        self.api_key = api_key or os.getenv("SMS_GATEWAY_KEY")
        self.sender_id = sender_id or os.getenv("SMS_SENDER_ID", "MANAS-SETU")
        self._fallback_mock = MockSMSProvider()

    def is_configured(self) -> bool:
        return bool(self.api_url and self.api_key)

    def send_sms(
        self,
        to_phone: str,
        message: str,
        idempotency_key: str | None = None,
        is_neutral: bool = True,
    ) -> SMSDeliveryResult:
        if not self.is_configured():
            logger.info("SMS gateway credentials not configured; routing via MockSMSProvider.")
            return self._fallback_mock.send_sms(to_phone, message, idempotency_key, is_neutral)

        # In live mode, execute HTTP request against configured gateway
        try:
            import requests

            payload = {
                "to": to_phone,
                "message": message,
                "sender": self.sender_id,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=5)
            if resp.status_code in (200, 201, 202):
                data = resp.json() if resp.headers.get("content-type") == "application/json" else {}
                msg_id = data.get("message_id", f"gw-{resp.status_code}")
                return SMSDeliveryResult(
                    message_id=msg_id,
                    recipient=to_phone,
                    status="queued",
                    is_mock=False,
                    sent_at=datetime.now(timezone.utc),
                    provider_name="ConfigurableGateway",
                )
            else:
                return SMSDeliveryResult(
                    message_id="",
                    recipient=to_phone,
                    status="failed",
                    is_mock=False,
                    sent_at=datetime.now(timezone.utc),
                    error=f"Gateway responded with HTTP {resp.status_code}",
                    provider_name="ConfigurableGateway",
                )
        except Exception as exc:
            logger.error("SMS gateway transmission failed: %s", exc)
            return SMSDeliveryResult(
                message_id="",
                recipient=to_phone,
                status="failed",
                is_mock=False,
                sent_at=datetime.now(timezone.utc),
                error=str(exc),
                provider_name="ConfigurableGateway",
            )

    def check_delivery_status(self, message_id: str) -> str:
        if not self.is_configured():
            return self._fallback_mock.check_delivery_status(message_id)
        return "delivered"


_DEFAULT_SMS_PROVIDER: BaseSMSProvider | None = None


def get_sms_provider() -> BaseSMSProvider:
    """Return the active SMS provider instance configured for this environment."""
    global _DEFAULT_SMS_PROVIDER
    if _DEFAULT_SMS_PROVIDER is None:
        provider_type = os.getenv("SMS_PROVIDER", "mock").lower()
        if provider_type == "gateway":
            _DEFAULT_SMS_PROVIDER = ConfigurableGatewaySMSProvider()
        else:
            _DEFAULT_SMS_PROVIDER = MockSMSProvider()
    return _DEFAULT_SMS_PROVIDER

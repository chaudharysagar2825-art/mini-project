"""Multi-Channel Communication Service for Manas Setu.

Implements the unified communication intake and notification workflow:
Inbound Channel (Text/SMS/Voice) -> Phone/Identity Verification -> Consent Check
-> Check-in Normalization -> Distress Risk Scoring -> Assessment Persistence
-> Alert Workflow -> Staff Review & Audit Logging.

Enforces DPDP Act privacy safeguards:
- Strict consent verification before processing.
- Neutral notifications (no sensitive trauma keywords in SMS previews).
- Provider-independent mock/live switching.
"""

from datetime import datetime, timezone
import json
import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.checkin import CheckIn
from app.models.consent import Consent
from app.models.safe_contact import SafeContact
from app.models.victim_case import VictimCase
from app.services.audit_service import create_audit_log
from app.services.checkin_service import create_checkin
from app.services.consent_service import check_consent_status
from integrations.ivr.provider import get_ivr_provider
from integrations.sms.provider import SMSDeliveryResult, get_sms_provider

logger = logging.getLogger(__name__)


def find_case_by_phone(db: Session, phone_number: str) -> VictimCase | None:
    """Locate the associated victim case from a verified phone number.

    Searches active Safe Contacts registered to cases.
    """
    clean_phone = re.sub(r"[\s\-\(\)]", "", phone_number)
    if not clean_phone:
        return None

    # Search for contact with matching phone
    contact = (
        db.query(SafeContact)
        .filter(
            SafeContact.is_active == True,
            SafeContact.phone.ilike(f"%{clean_phone[-10:]}"),
        )
        .first()
    )

    if contact is not None:
        return db.get(VictimCase, contact.case_id)

    return None


def normalize_sms_to_answers(sms_body: str) -> tuple[dict[str, str], bool, bool]:
    """Parse raw SMS text into internal questionnaire answers.

    Returns:
    - answers: dict of question_id -> response string
    - direct_safety_concern: bool
    - requested_human_contact: bool
    """
    text = sms_body.strip()
    direct_safety = False
    request_contact = False

    # Check for direct keywords
    lower_text = text.lower()
    if any(k in lower_text for k in ("danger", "threat", "emergency", "unsafe", "crisis", "sos")):
        direct_safety = True
    if any(k in lower_text for k in ("help", "call me", "contact", "reach out", "caseworker")):
        request_contact = True

    # Check for comma-separated or space-separated numeric ratings (e.g., "1, 2, 0, 1")
    dtmf_map = {"0": "none", "1": "mild", "2": "moderate", "3": "severe"}
    digits = re.findall(r"\b[0-3]\b", text)

    answers: dict[str, str] = {}
    if len(digits) >= 4:
        answers["sleep_quality"] = dtmf_map.get(digits[0], "none")
        answers["anxiety_intensity"] = dtmf_map.get(digits[1], "mild")
        answers["isolation_feeling"] = dtmf_map.get(digits[2], "none")
        answers["coping_difficulty"] = dtmf_map.get(digits[3], "mild")
    else:
        # If unstructured text, map to free reflection and baseline indicators
        answers["free_reflection"] = text
        answers["sleep_quality"] = "moderate" if "sleep" in lower_text else "none"
        answers["anxiety_intensity"] = "moderate" if any(w in lower_text for w in ("anxious", "worry", "stress", "scared")) else "none"
        answers["isolation_feeling"] = "moderate" if any(w in lower_text for w in ("alone", "lonely", "isolated")) else "none"
        answers["coping_difficulty"] = "moderate" if "overwhelmed" in lower_text else "none"

    return answers, direct_safety, request_contact


def process_inbound_sms(
    db: Session,
    sender_phone: str,
    sms_text: str,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """Execute unified intake pipeline for inbound SMS.

    Validates sender, consent, creates check-in, runs AI scoring, persists assessment,
    and returns processing receipt.
    """
    clean_sender = sender_phone.strip()
    if not clean_sender or not sms_text.strip():
        raise ValueError("Sender phone and message text cannot be empty.")

    case = find_case_by_phone(db, clean_sender)
    if case is None:
        logger.warning("Inbound SMS from unrecognized phone: %s", clean_sender[-4:])
        return {
            "status": "unrecognized_sender",
            "message": "Sender is not registered with an active case.",
            "phone_suffix": clean_sender[-4:],
        }

    # Verify DPDP consent
    consent_ok, consent_reason = check_consent_status(db, case.id)
    if not consent_ok:
        logger.warning("SMS check-in rejected due to consent: %s (Case #%d)", consent_reason, case.id)
        return {
            "status": "consent_required",
            "message": consent_reason,
            "case_id": case.id,
        }

    answers, direct_safety, request_contact = normalize_sms_to_answers(sms_text)

    # Ingest through standard check-in service (which executes AI distress scoring and alert generation)
    checkin = create_checkin(
        db=db,
        case_id=case.id,
        questionnaire_version="sms-inbound-v1",
        answers=json.dumps(answers),
        direct_safety_concern=direct_safety,
        user_skipped_questions=None,
        requested_human_contact=request_contact,
        created_by=case.user_id,
    )

    create_audit_log(
        db=db,
        user_id=case.user_id,
        action="inbound_sms_processed",
        resource_type="checkin",
        resource_id=str(checkin.id),
        details=f"SMS check-in received from phone ending {clean_sender[-4:]}; Case #{case.id}",
    )

    # Send neutral confirmation SMS
    sms_provider = get_sms_provider()
    sms_provider.send_sms(
        to_phone=clean_sender,
        message="Thank you for your response. Your update has been noted by your support team.",
        idempotency_key=idempotency_key,
        is_neutral=True,
    )

    return {
        "status": "processed",
        "case_id": case.id,
        "checkin_id": checkin.id,
        "direct_safety_concern": direct_safety,
        "requested_human_contact": request_contact,
    }


def process_inbound_ivr_event(
    db: Session,
    payload: dict[str, Any],
    raw_body: bytes = b"",
    signature: str | None = None,
) -> dict[str, Any]:
    """Execute unified intake pipeline for IVR telephony events."""
    ivr_provider = get_ivr_provider()
    event = ivr_provider.parse_event(payload, raw_body, signature)

    if not event.is_valid_signature:
        raise ValueError("Invalid IVR callback signature.")

    if not event.caller_phone:
        raise ValueError("Caller phone is required in IVR event.")

    case = find_case_by_phone(db, event.caller_phone)
    if case is None:
        return {
            "status": "unrecognized_caller",
            "message": "Caller phone is not associated with an active case.",
            "phone_suffix": event.caller_phone[-4:],
        }

    # Verify DPDP consent
    consent_ok, consent_reason = check_consent_status(db, case.id)
    if not consent_ok:
        return {
            "status": "consent_required",
            "message": consent_reason,
            "case_id": case.id,
        }

    # Default missing questions to 'none' if empty
    answers = event.answers or {
        "sleep_quality": "none",
        "anxiety_intensity": "none",
        "isolation_feeling": "none",
        "coping_difficulty": "none",
    }

    checkin = create_checkin(
        db=db,
        case_id=case.id,
        questionnaire_version="ivr-dtmf-v1",
        answers=json.dumps(answers),
        direct_safety_concern=event.direct_safety_concern,
        user_skipped_questions=None,
        requested_human_contact=event.requested_human_contact,
        created_by=case.user_id,
    )

    create_audit_log(
        db=db,
        user_id=case.user_id,
        action="inbound_ivr_processed",
        resource_type="checkin",
        resource_id=str(checkin.id),
        details=f"IVR check-in received from call #{event.call_id}; Case #{case.id}",
    )

    return {
        "status": "processed",
        "case_id": case.id,
        "checkin_id": checkin.id,
        "call_id": event.call_id,
        "direct_safety_concern": event.direct_safety_concern,
    }


def send_wellness_reminder(
    db: Session,
    case_id: int,
    phone_number: str,
    requested_by: int | None = None,
) -> SMSDeliveryResult:
    """Dispatch a privacy-preserving wellness check-in reminder SMS."""
    case = db.get(VictimCase, case_id)
    if case is None:
        raise ValueError("Case not found.")

    consent_ok, reason = check_consent_status(db, case_id)
    if not consent_ok:
        raise ValueError(f"Cannot dispatch reminder: {reason}")

    # Enforce neutral content
    neutral_message = (
        "Namaste from Manas Setu. This is your routine wellness reminder. "
        "Please complete your daily check-in or reply with your status."
    )

    sms_provider = get_sms_provider()
    result = sms_provider.send_sms(
        to_phone=phone_number,
        message=neutral_message,
        is_neutral=True,
    )

    create_audit_log(
        db=db,
        user_id=requested_by,
        action="wellness_reminder_dispatched",
        resource_type="safe_contact",
        resource_id=str(case_id),
        details=f"Reminder sent to {phone_number[-4:]} (status: {result.status}, provider: {result.provider_name})",
    )

    return result

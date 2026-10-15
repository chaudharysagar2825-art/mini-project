from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.consent import Consent
from app.models.victim_case import VictimCase


def create_consent(
    db: Session,
    case_id: int,
    status: str,
    version: str,
    scope: str,
    channel: str,
) -> Consent:

    case = db.get(VictimCase, case_id)

    if case is None:
        raise ValueError("Case not found")

    now = datetime.now(timezone.utc)

    consent = Consent(
        case_id=case_id,
        status=status,
        version=version,
        scope=scope,
        channel=channel,
        consented_at=now if status == "granted" else None,
        paused_at=now if status == "paused" else None,
        withdrawn_at=now if status == "withdrawn" else None,
    )

    db.add(consent)
    db.commit()
    db.refresh(consent)

    return consent


def get_latest_consent(
    db: Session,
    case_id: int,
) -> Consent | None:

    return (
        db.query(Consent)
        .filter(Consent.case_id == case_id)
        .order_by(Consent.created_at.desc())
        .first()
    )


def has_active_consent(
    db: Session,
    case_id: int,
) -> bool:

    consent = get_latest_consent(db, case_id)

    if consent is None:
        return False

    return consent.status == "granted"


def check_consent_status(
    db: Session,
    case_id: int,
) -> tuple[bool, str]:
    """Verify consent status and return a clear reason if disallowed."""
    consent = get_latest_consent(db, case_id)

    if consent is None:
        return False, "No consent record found. Active consent is required before submitting a check-in"

    if consent.status == "paused":
        return False, "Consent is currently paused. Please resume consent before submitting a check-in"

    if consent.status == "withdrawn":
        return False, "Consent has been withdrawn. Active consent is required before submitting a check-in"

    if consent.status != "granted":
        return False, f"Consent status '{consent.status}' does not permit check-in processing"

    return True, "Active consent verified"



def update_consent_status(
    db: Session,
    case_id: int,
    status: str,
) -> Consent:

    allowed_statuses = {
        "granted",
        "paused",
        "withdrawn",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid consent status")

    consent = get_latest_consent(db, case_id)

    if consent is None:
        raise ValueError("No consent record found")

    now = datetime.now(timezone.utc)
    consent.status = status

    if status == "granted":
        consent.consented_at = now
        consent.paused_at = None
        consent.withdrawn_at = None

    elif status == "paused":
        consent.paused_at = now
        consent.withdrawn_at = None

    elif status == "withdrawn":
        consent.withdrawn_at = now
        consent.paused_at = None

    db.commit()
    db.refresh(consent)

    return consent

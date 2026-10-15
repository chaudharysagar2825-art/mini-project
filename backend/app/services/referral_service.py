from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.victim_case import VictimCase
from app.services.audit_service import create_audit_log


def create_referral(
    db: Session,
    case_id: int,
    referral_type: str,
    organization: str,
    reason: str,
    priority: str,
    created_by: int,
) -> Referral:

    case = db.get(VictimCase, case_id)

    if case is None:
        raise ValueError("Case not found")

    referral = Referral(
        case_id=case_id,
        referral_type=referral_type,
        organization=organization,
        reason=reason,
        priority=priority,
        status="created",
        created_by=created_by,
    )

    db.add(referral)
    db.flush()

    create_audit_log(
        db=db,
        user_id=created_by,
        action="referral_created",
        resource_type="referral",
        resource_id=str(referral.id),
        details=(
            f"Referral ({referral_type}) created for case #{case_id}; "
            f"Provider: {organization}; Priority: {priority}"
        ),
    )

    db.commit()
    db.refresh(referral)

    return referral


def get_referral(
    db: Session,
    referral_id: int,
) -> Referral | None:

    return db.get(Referral, referral_id)


def get_case_referrals(
    db: Session,
    case_id: int,
) -> list[Referral]:

    return (
        db.query(Referral)
        .filter(Referral.case_id == case_id)
        .order_by(Referral.created_at.desc())
        .all()
    )


def update_referral_status(
    db: Session,
    referral_id: int,
    status: str,
    notes: str | None = None,
    updated_by: int | None = None,
) -> Referral:

    referral = db.get(Referral, referral_id)

    if referral is None:
        raise ValueError("Referral not found")

    allowed_statuses = {
        "created",
        "acknowledged",
        "in_progress",
        "completed",
        "cancelled",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid referral status")

    valid_transitions = {
        "created": {"acknowledged", "cancelled"},
        "acknowledged": {"in_progress", "cancelled"},
        "in_progress": {"completed", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }

    if referral.status in ("completed", "cancelled") and status != referral.status:
        raise ValueError(
            f"Cannot update referral that is already in terminal state '{referral.status}'"
        )

    if status != referral.status and status not in valid_transitions.get(referral.status, set()):
        raise ValueError(
            f"Invalid status transition from '{referral.status}' to '{status}'"
        )

    referral.status = status

    if notes and notes.strip():
        # Append follow-up note to reason record for auditability
        referral.reason = f"{referral.reason}\n[Follow-up {status}]: {notes.strip()}"

    create_audit_log(
        db=db,
        user_id=updated_by,
        action="referral_status_updated",
        resource_type="referral",
        resource_id=str(referral.id),
        details=(
            f"Referral #{referral.id} transitioned to '{status}'"
            + (f"; Note: {notes.strip()}" if notes and notes.strip() else "")
        ),
    )

    db.commit()
    db.refresh(referral)

    return referral
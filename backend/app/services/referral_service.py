from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.victim_case import VictimCase


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

    referral.status = status

    db.commit()
    db.refresh(referral)

    return referral
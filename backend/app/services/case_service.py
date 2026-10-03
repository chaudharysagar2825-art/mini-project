from sqlalchemy.orm import Session

from app.models.victim_case import VictimCase
from app.models.user import User


def create_case(
    db: Session,
    case_code: str,
    user_id: int,
) -> VictimCase:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    case = VictimCase(
        case_code=case_code,
        user_id=user_id,
        status="active",
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def get_case(
    db: Session,
    case_id: int,
) -> VictimCase | None:

    return db.get(VictimCase, case_id)


def get_user_cases(
    db: Session,
    user_id: int,
) -> list[VictimCase]:

    return (
        db.query(VictimCase)
        .filter(VictimCase.user_id == user_id)
        .order_by(VictimCase.created_at.desc())
        .all()
    )


def update_case_status(
    db: Session,
    case_id: int,
    status: str,
) -> VictimCase:

    case = db.get(VictimCase, case_id)

    if case is None:
        raise ValueError("Case not found")

    allowed_statuses = {
        "active",
        "paused",
        "closed",
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid case status")

    case.status = status

    db.commit()
    db.refresh(case)

    return case
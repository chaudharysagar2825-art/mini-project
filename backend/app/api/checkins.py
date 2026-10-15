import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment
from app.schemas.checkin import CheckInCreate, CheckInResponse
from app.security.auth import get_current_user
from app.services.case_service import get_case
from app.services.checkin_service import (
    create_checkin,
    get_case_checkins,
    get_checkin,
)

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


def attach_risk_level(db: Session, checkin):
    """Attach the associated assessment's risk level to a check-in."""
    assessment = (
        db.query(Assessment)
        .filter(Assessment.checkin_id == checkin.id)
        .first()
    )

    checkin.risk_level = (
        assessment.risk_level if assessment is not None else None
    )
    return checkin


@router.post(
    "/{case_id}",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_checkin(
    case_id: int,
    payload: CheckInCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(db=db, case_id=case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    if case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this case",
        )

    try:
        checkin = create_checkin(
            db=db,
            case_id=case_id,
            questionnaire_version=payload.questionnaire_version,
            answers=json.dumps(
                {a.question_id: a.answer for a in payload.answers}
            ),
            direct_safety_concern=payload.direct_safety_concern,
            user_skipped_questions=json.dumps(payload.user_skipped_questions) if payload.user_skipped_questions else None,
            requested_human_contact=payload.requested_human_contact,
            created_by=current_user["user_id"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return attach_risk_level(db, checkin)


@router.get(
    "/case/{case_id}",
    response_model=list[CheckInResponse],
)
def get_checkins_for_case(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(db=db, case_id=case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    user_role = current_user.get("role", "")
    is_owner = case.user_id == current_user["user_id"]
    is_staff = user_role in ("admin", "caseworker", "counsellor")

    if not (is_owner or is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this case",
        )

    checkins = get_case_checkins(db=db, case_id=case_id)
    return [attach_risk_level(db, checkin) for checkin in checkins]


@router.get(
    "/{checkin_id}",
    response_model=CheckInResponse,
)
def get_checkin_by_id(
    checkin_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    checkin = get_checkin(db=db, checkin_id=checkin_id)

    if checkin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found",
        )

    case = get_case(db=db, case_id=checkin.case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    user_role = current_user.get("role", "")
    is_owner = case.user_id == current_user["user_id"]
    is_staff = user_role in ("admin", "caseworker", "counsellor")

    if not (is_owner or is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this check-in",
        )

    return attach_risk_level(db, checkin)

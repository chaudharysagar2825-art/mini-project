import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.checkin import CheckInCreate, CheckInResponse
from app.security.auth import get_current_user
from app.services.case_service import get_case
from app.services.checkin_service import (
    create_checkin,
    get_case_checkins,
    get_checkin,
)


router = APIRouter(
    prefix="/checkins",
    tags=["Check-ins"],
)


@router.post(
    "/{case_id}",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_checkin(
    case_id: int,
    data: CheckInCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(
        db=db,
        case_id=case_id,
    )

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

    answers_dict = {
        answer.question_id: answer.answer
        for answer in data.answers
    }

    answers_json = json.dumps(answers_dict)

    skipped_json = json.dumps(
        data.user_skipped_questions
    )

    try:
        checkin = create_checkin(
            db=db,
            case_id=case_id,
            questionnaire_version=data.questionnaire_version,
            answers=answers_json,
            direct_safety_concern=data.direct_safety_concern,
            user_skipped_questions=skipped_json,
            requested_human_contact=data.requested_human_contact,
            created_by=current_user["user_id"],
        )

        return checkin

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{checkin_id}",
    response_model=CheckInResponse,
)
def get_checkin_by_id(
    checkin_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    checkin = get_checkin(
        db=db,
        checkin_id=checkin_id,
    )

    if checkin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found",
        )

    case = get_case(
        db=db,
        case_id=checkin.case_id,
    )

    if case is None or case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this check-in",
        )

    return checkin


@router.get(
    "/case/{case_id}",
    response_model=list[CheckInResponse],
)
def get_checkins_for_case(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(
        db=db,
        case_id=case_id,
    )

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

    return get_case_checkins(
        db=db,
        case_id=case_id,
    )
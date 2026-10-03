from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.consent import ConsentCreate, ConsentResponse
from app.security.auth import get_current_user
from app.services.consent_service import (
    create_consent,
    get_latest_consent,
    update_consent_status,
)
from app.services.case_service import get_case


router = APIRouter(
    prefix="/consent",
    tags=["Consent"],
)


@router.post(
    "/{case_id}",
    response_model=ConsentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case_consent(
    case_id: int,
    data: ConsentCreate,
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

    try:
        return create_consent(
            db=db,
            case_id=case_id,
            status=data.status,
            version=data.version,
            scope=data.scope,
            channel=data.channel,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{case_id}",
    response_model=ConsentResponse,
)
def get_case_consent(
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

    consent = get_latest_consent(
        db=db,
        case_id=case_id,
    )

    if consent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No consent record found",
        )

    return consent


@router.patch(
    "/{case_id}/status",
    response_model=ConsentResponse,
)
def change_consent_status(
    case_id: int,
    status_value: str,
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

    allowed_statuses = {
        "granted",
        "paused",
        "withdrawn",
    }

    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent status",
        )

    try:
        return update_consent_status(
            db=db,
            case_id=case_id,
            status=status_value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
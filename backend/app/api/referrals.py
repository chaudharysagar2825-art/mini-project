from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.referral import ReferralCreate, ReferralResponse
from app.security.auth import get_current_user
from app.services.case_service import get_case
from app.services.referral_service import (
    create_referral,
    get_case_referrals,
    get_referral,
    update_referral_status,
)


router = APIRouter(
    prefix="/referrals",
    tags=["Referrals"],
)


@router.post(
    "/{case_id}",
    response_model=ReferralResponse,
    status_code=201,
)
def create_case_referral(
    case_id: int,
    data: ReferralCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(
        db=db,
        case_id=case_id,
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    if case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this case",
        )

    try:
        return create_referral(
            db=db,
            case_id=case_id,
            referral_type=data.referral_type,
            organization=data.organization,
            reason=data.reason,
            priority=data.priority,
            created_by=current_user["user_id"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{referral_id}",
    response_model=ReferralResponse,
)
def get_referral_by_id(
    referral_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    referral = get_referral(
        db=db,
        referral_id=referral_id,
    )

    if referral is None:
        raise HTTPException(
            status_code=404,
            detail="Referral not found",
        )

    case = get_case(
        db=db,
        case_id=referral.case_id,
    )

    if case is None or case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this referral",
        )

    return referral


@router.get(
    "/case/{case_id}",
    response_model=list[ReferralResponse],
)
def get_referrals_for_case(
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
            status_code=404,
            detail="Case not found",
        )

    if case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this case",
        )

    return get_case_referrals(
        db=db,
        case_id=case_id,
    )


@router.patch(
    "/{referral_id}/status",
    response_model=ReferralResponse,
)
def change_referral_status(
    referral_id: int,
    status_value: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    referral = get_referral(
        db=db,
        referral_id=referral_id,
    )

    if referral is None:
        raise HTTPException(
            status_code=404,
            detail="Referral not found",
        )

    case = get_case(
        db=db,
        case_id=referral.case_id,
    )

    if case is None or case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this referral",
        )

    try:
        return update_referral_status(
            db=db,
            referral_id=referral_id,
            status=status_value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
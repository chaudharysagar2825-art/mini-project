from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.case import CaseCreate, CaseResponse
from app.security.auth import get_current_user
from app.services.case_service import (
    create_case,
    get_case,
    get_user_cases,
    update_case_status,
)
from app.utils.identifiers import generate_case_code


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_case(
    data: CaseCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        case = create_case(
            db=db,
            case_code=data.case_code,
            user_id=current_user["user_id"],
        )

        return case

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/generate",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_new_case(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case_code = generate_case_code()

    try:
        case = create_case(
            db=db,
            case_code=case_code,
            user_id=current_user["user_id"],
        )

        return case

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/my",
    response_model=list[CaseResponse],
)
def get_my_cases(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_cases(
        db=db,
        user_id=current_user["user_id"],
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
def get_case_by_id(
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

    return case


@router.patch(
    "/{case_id}/status",
    response_model=CaseResponse,
)
def change_case_status(
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

    try:
        return update_case_status(
            db=db,
            case_id=case_id,
            status=status_value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
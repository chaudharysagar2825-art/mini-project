
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.victim_case import VictimCase
from app.schemas.safe_contacts import SafeContactCreate, SafeContactResponse
from app.security.auth import get_current_user
from app.services.safe_contact_service import (
    create_safe_contact,
    get_case_safe_contacts,
    get_safe_contact,
    deactivate_safe_contact,
)

router = APIRouter(prefix="/safe-contacts", tags=["Safe Contacts"])


def verify_case_ownership(
    db: Session,
    case_id: int,
    current_user: dict,
) -> VictimCase:
    case = db.get(VictimCase, case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this case",
        )

    return case


@router.post(
    "/{case_id}",
    response_model=SafeContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    case_id: int,
    data: SafeContactCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_case_ownership(db, case_id, current_user)

    try:
        return create_safe_contact(
            db=db,
            case_id=case_id,
            contact_name=data.contact_name,
            relationship=data.relationship,
            phone=data.phone,
            preferred_language=data.preferred_language,
            preferred_channel=data.preferred_channel,
            safe_time=data.safe_time,
            neutral_notification=data.neutral_notification,
            fallback_contact=data.fallback_contact,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/{case_id}",
    response_model=list[SafeContactResponse],
)
def list_contacts(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_case_ownership(db, case_id, current_user)
    return get_case_safe_contacts(db, case_id)


@router.delete(
    "/{case_id}/{contact_id}",
    response_model=SafeContactResponse,
)
def deactivate_contact(
    case_id: int,
    contact_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_case_ownership(db, case_id, current_user)

    contact = get_safe_contact(db, contact_id)

    if contact is None or contact.case_id != case_id:
        raise HTTPException(status_code=404, detail="Safe contact not found")

    try:
        return deactivate_safe_contact(db, contact_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

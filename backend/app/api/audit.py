from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.auth import get_current_user
from app.services.audit_service import get_audit_logs


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get("")
def get_my_audit_logs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_audit_logs(
        db=db,
        user_id=current_user["user_id"],
    )


@router.get("/resource")
def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_audit_logs(
        db=db,
        resource_type=resource_type,
        resource_id=resource_id,
    )
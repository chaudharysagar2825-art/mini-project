"""API endpoints for Distress Risk Assessments in Manas Setu."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentResponse
from app.security.auth import get_current_user
from app.services.case_service import get_case

router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


@router.get(
    "/case/{case_id}",
    response_model=list[AssessmentResponse],
)
def get_assessments_for_case(
    case_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve historical structured risk assessments for a case.

    Accessible to: Case owner (victim) or authorized staff (admin, caseworker, counsellor).
    """
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

    assessments = (
        db.query(Assessment)
        .filter(Assessment.case_id == case_id)
        .order_by(Assessment.created_at.desc(), Assessment.id.desc())
        .limit(limit)
        .all()
    )

    return assessments


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment_by_id(
    assessment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve single assessment by ID.

    Accessible to: Case owner (victim) or authorized staff (admin, caseworker, counsellor).
    """
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    case = get_case(db=db, case_id=assessment.case_id)
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
            detail="You do not have access to this assessment",
        )

    return assessment

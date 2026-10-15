from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.assessment import Assessment
from app.models.checkin import CheckIn
from app.models.referral import Referral
from app.models.victim_case import VictimCase
from app.schemas.assessment import CaseTrendsResponse, LongitudinalTrendItem
from app.security.auth import get_current_user
from app.services.case_service import get_case


router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards"],
)


@router.get("/summary")
def dashboard_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user["user_id"]
    user_role = current_user.get("role", "")
    is_staff = user_role in ("admin", "caseworker", "counsellor")

    if is_staff:
        total_cases = db.query(func.count(VictimCase.id)).scalar()

        open_alerts = (
            db.query(func.count(Alert.id))
            .filter(
                Alert.status.in_(
                    ["open", "acknowledged", "assigned", "escalated"]
                )
            )
            .scalar()
        )

        active_referrals = (
            db.query(func.count(Referral.id))
            .filter(
                Referral.status.in_(
                    ["created", "acknowledged", "in_progress"]
                )
            )
            .scalar()
        )
    else:
        total_cases = (
            db.query(func.count(VictimCase.id))
            .filter(VictimCase.user_id == user_id)
            .scalar()
        )

        open_alerts = (
            db.query(func.count(Alert.id))
            .join(
                VictimCase,
                VictimCase.id == Alert.case_id,
            )
            .filter(
                VictimCase.user_id == user_id,
                Alert.status.in_(
                    ["open", "acknowledged", "assigned", "escalated"]
                ),
            )
            .scalar()
        )

        active_referrals = (
            db.query(func.count(Referral.id))
            .join(
                VictimCase,
                VictimCase.id == Referral.case_id,
            )
            .filter(
                VictimCase.user_id == user_id,
                Referral.status.in_(
                    ["created", "acknowledged", "in_progress"]
                ),
            )
            .scalar()
        )

    return {
        "total_cases": total_cases or 0,
        "open_alerts": open_alerts or 0,
        "active_referrals": active_referrals or 0,
    }


@router.get(
    "/case/{case_id}/trends",
    response_model=CaseTrendsResponse,
)
def get_case_trends(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve persisted longitudinal distress trends for a case.

    Authorized for: Case owner (victim) or authorized staff.
    Guarantees cross-case isolation and non-N+1 query performance.
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

    # Fetch check-ins and assessments in chronological order (oldest to newest for trend)
    checkins = (
        db.query(CheckIn)
        .filter(CheckIn.case_id == case_id)
        .order_by(CheckIn.submitted_at.asc(), CheckIn.id.asc())
        .all()
    )

    if not checkins:
        return CaseTrendsResponse(
            case_id=case.id,
            case_code=case.case_code,
            total_checkins=0,
            current_risk_level="routine",
            current_risk_category="low",
            overall_direction="unknown",
            average_score=0.0,
            history=[],
        )

    checkin_ids = [c.id for c in checkins]
    assessments = (
        db.query(Assessment)
        .filter(Assessment.checkin_id.in_(checkin_ids))
        .all()
    )
    assessment_map = {a.checkin_id: a for a in assessments}

    history: list[LongitudinalTrendItem] = []
    total_score = 0
    scored_count = 0

    for chk in checkins:
        asm = assessment_map.get(chk.id)
        if asm is not None:
            score = asm.score
            r_level = asm.risk_level
            r_cat = asm.risk_category
            direction = asm.direction
            reason = asm.reason
            asm_id = asm.id
            total_score += score
            scored_count += 1
        else:
            score = 0
            r_level = "routine"
            r_cat = "low"
            direction = "unknown"
            reason = "Awaiting assessment"
            asm_id = None

        history.append(
            LongitudinalTrendItem(
                checkin_id=chk.id,
                assessment_id=asm_id,
                timestamp=chk.submitted_at,
                score=score,
                risk_level=r_level,
                risk_category=r_cat,
                direction=direction,
                reason=reason,
            )
        )

    avg_score = round(total_score / scored_count, 1) if scored_count > 0 else 0.0
    latest = history[-1]

    # Calculate overall direction by comparing early and recent scores
    if len(history) >= 2:
        first_half_avg = sum(h.score for h in history[:len(history)//2]) / (len(history)//2)
        second_half_avg = sum(h.score for h in history[len(history)//2:]) / (len(history) - len(history)//2)
        if second_half_avg > first_half_avg + 0.5:
            overall_direction = "worsening"
        elif second_half_avg < first_half_avg - 0.5:
            overall_direction = "improving"
        else:
            overall_direction = "stable"
    else:
        overall_direction = latest.direction

    return CaseTrendsResponse(
        case_id=case.id,
        case_code=case.case_code,
        total_checkins=len(checkins),
        current_risk_level=latest.risk_level,
        current_risk_category=latest.risk_category,
        overall_direction=overall_direction,
        average_score=avg_score,
        history=history,
    )
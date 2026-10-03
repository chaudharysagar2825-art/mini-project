from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.referral import Referral
from app.models.victim_case import VictimCase
from app.security.auth import get_current_user


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
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.assessment import Assessment
from app.services.scoring_service import RiskResult


def create_alert(
    db: Session,
    case_id: int,
    assessment: Assessment,
    risk_result: RiskResult,
) -> Alert | None:

    if risk_result.risk_level == "routine":
        return None

    existing_alert = (
        db.query(Alert)
        .filter(Alert.assessment_id == assessment.id)
        .first()
    )
    if existing_alert is not None:
        return existing_alert

    alert_type = (
        "urgent"
        if risk_result.risk_level == "urgent"
        else "follow_up"
    )


    alert = Alert(
        case_id=case_id,
        assessment_id=assessment.id,
        alert_type=alert_type,
        risk_level=risk_result.risk_level,
        status="open",
        reason=risk_result.reason,
        direction=risk_result.direction,
        confidence=risk_result.confidence,
    )

    db.add(alert)
    db.flush()

    return alert


def get_alert(
    db: Session,
    alert_id: int,
) -> Alert | None:

    return db.get(Alert, alert_id)


def get_case_alerts(
    db: Session,
    case_id: int,
) -> list[Alert]:

    return (
        db.query(Alert)
        .filter(Alert.case_id == case_id)
        .order_by(Alert.created_at.desc())
        .all()
    )


def update_alert_status(
    db: Session,
    alert_id: int,
    action: str,
    reason: str | None = None,
    assigned_to: int | None = None,
) -> Alert:

    alert = db.get(Alert, alert_id)

    if alert is None:
        raise ValueError("Alert not found")

    if alert.status in ("resolved", "dismissed"):
        raise ValueError(f"Cannot update alert that is already {alert.status}")

    status_map = {
        "acknowledge": "acknowledged",
        "assign": "assigned",
        "escalate": "escalated",
        "resolve": "resolved",
        "dismiss": "dismissed",
    }

    if action not in status_map:
        raise ValueError("Invalid alert action")

    if action == "assign":
        if assigned_to is None:
            raise ValueError("Assignee user ID is required when action is 'assign'")

        from app.models.user import User

        assignee = db.get(User, assigned_to)
        if assignee is None:
            raise ValueError("Assignee user not found")
        if not assignee.is_active:
            raise ValueError("Assignee user is not active")
        if assignee.role == "victim":
            raise ValueError("Alerts cannot be assigned to victim accounts")

        alert.assigned_to = assigned_to

    alert.status = status_map[action]
    alert.action_reason = reason

    db.commit()
    db.refresh(alert)

    return alert
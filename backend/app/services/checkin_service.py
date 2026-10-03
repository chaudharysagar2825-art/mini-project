import json

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.checkin import CheckIn
from app.models.victim_case import VictimCase
from app.services.alert_service import create_alert
from app.services.audit_service import create_audit_log
from app.services.consent_service import has_active_consent
from app.services.risk_engine import calculate_distress_score
from app.services.scoring_service import calculate_risk


def create_checkin(
    db: Session,
    case_id: int,
    questionnaire_version: str,
    answers: str,
    direct_safety_concern: bool | None,
    user_skipped_questions: str | None,
    requested_human_contact: bool,
    created_by: int | None = None,
) -> CheckIn:

    case = db.get(VictimCase, case_id)

    if case is None:
        raise ValueError("Case not found")

    if not has_active_consent(db, case_id):
        raise ValueError(
            "Active consent is required before submitting a check-in"
        )

    try:
        answer_data = json.loads(answers)
    except json.JSONDecodeError:
        raise ValueError("Invalid check-in answer format")

    if not isinstance(answer_data, dict):
        raise ValueError("Check-in answers must be a JSON object")

    checkin = CheckIn(
        case_id=case_id,
        questionnaire_version=questionnaire_version,
        answers=answers,
        direct_safety_concern=direct_safety_concern,
        user_skipped_questions=user_skipped_questions,
        requested_human_contact=requested_human_contact,
        status="submitted",
    )

    db.add(checkin)
    db.flush()

    signal = calculate_distress_score(
        answers=answer_data,
    )

    final_safety_concern = (
        True
        if direct_safety_concern is True
        else signal.direct_safety_concern
    )

    risk_result = calculate_risk(
        distress_score=signal.distress_score,
        baseline_score=None,
        direct_safety_concern=final_safety_concern,
        missing_data=signal.missing_data,
    )

    assessment = Assessment(
        checkin_id=checkin.id,
        case_id=case_id,
        risk_level=risk_result.risk_level,
        direction=risk_result.direction,
        score=risk_result.score,
        confidence=risk_result.confidence,
        reason=risk_result.reason,
        model_version=risk_result.model_version,
    )

    db.add(assessment)
    db.flush()

    alert = create_alert(
        db=db,
        case_id=case_id,
        assessment=assessment,
        risk_result=risk_result,
    )

    if alert is not None:
        db.flush()

    create_audit_log(
        db=db,
        user_id=created_by,
        action="checkin_submitted",
        resource_type="checkin",
        resource_id=str(checkin.id),
        details=(
            f"Risk level: {risk_result.risk_level}; "
            f"direction: {risk_result.direction}; "
            f"model: {risk_result.model_version}"
        ),
    )

    db.commit()
    db.refresh(checkin)

    return checkin


def get_checkin(
    db: Session,
    checkin_id: int,
) -> CheckIn | None:

    return db.get(CheckIn, checkin_id)


def get_case_checkins(
    db: Session,
    case_id: int,
) -> list[CheckIn]:

    return (
        db.query(CheckIn)
        .filter(CheckIn.case_id == case_id)
        .order_by(CheckIn.submitted_at.desc())
        .all()
    )
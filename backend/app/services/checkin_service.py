import json

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.checkin import CheckIn
from app.models.victim_case import VictimCase
from app.services.ai__services import safe_analyze_checkin
from app.services.alert_service import create_alert
from app.services.audit_service import create_audit_log
from app.services.consent_service import check_consent_status, has_active_consent
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

    consent_ok, consent_reason = check_consent_status(db, case_id)
    if not consent_ok:
        raise ValueError(consent_reason)

    try:
        answer_data = json.loads(answers)
    except json.JSONDecodeError:
        raise ValueError("Invalid check-in answer format")

    if not isinstance(answer_data, dict):
        raise ValueError("Check-in answers must be a JSON object")

    # Retrieve latest prior assessment for baseline tracking
    previous_assessment = (
        db.query(Assessment)
        .filter(Assessment.case_id == case_id)
        .order_by(Assessment.created_at.desc(), Assessment.id.desc())
        .first()
    )
    baseline_score = (
        previous_assessment.score if previous_assessment is not None else None
    )

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

    # Rule-based distress calculation
    signal = calculate_distress_score(
        answers=answer_data,
    )

    # AI Decision Support analysis (non-blocking fallback)
    ai_summary = safe_analyze_checkin(answer_data)
    ai_crisis_detected = False
    if ai_summary:
        crisis_info = ai_summary.get("crisis_signals")
        if isinstance(crisis_info, dict) and crisis_info.get("signal_count", 0) > 0:
            ai_crisis_detected = True

    final_safety_concern = (
        True
        if direct_safety_concern is True or signal.direct_safety_concern or ai_crisis_detected
        else False
    )

    risk_result = calculate_risk(
        distress_score=signal.distress_score,
        baseline_score=baseline_score,
        direct_safety_concern=final_safety_concern,
        missing_data=signal.missing_data,
    )

    # Enrich explanation and model version when AI analysis is available
    if ai_summary is not None:
        reasons = [risk_result.reason] if risk_result.reason else []
        ai_exp = ai_summary.get("explanation")
        if ai_exp:
            reasons.append(f"AI Decision Support: {ai_exp}")
        matched = ai_summary.get("crisis_signals", {}).get("matched_signals", [])
        if matched:
            reasons.append(f"Detected signals: {', '.join(matched)}")
        risk_result.reason = "; ".join(reasons)
        risk_result.model_version = f"{risk_result.model_version}+ai-pipeline-v1"

    existing_assessment = (
        db.query(Assessment)
        .filter(Assessment.checkin_id == checkin.id)
        .first()
    )
    if existing_assessment is not None:
        assessment = existing_assessment
        assessment.risk_level = risk_result.risk_level
        assessment.direction = risk_result.direction
        assessment.score = risk_result.score
        assessment.confidence = risk_result.confidence
        assessment.reason = risk_result.reason
        assessment.model_version = risk_result.model_version
    else:
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
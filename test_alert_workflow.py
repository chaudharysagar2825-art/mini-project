
import sys

sys.path.insert(0, "backend")

from app.database import SessionLocal
from app.services.checkin_service import create_checkin
from app.models.assessment import Assessment
from app.models.alert import Alert

db = SessionLocal()

try:
    checkin = create_checkin(
        db=db,
        case_id=1,
        questionnaire_version="test-urgent-1.0",
        answers=(
            '{"test_q1":"severe","test_q2":"high",'
            '"test_q3":"often","test_q4":"moderate"}'
        ),
        direct_safety_concern=True,
        user_skipped_questions="[]",
        requested_human_contact=True,
        created_by=1,
    )

    assessment = (
        db.query(Assessment)
        .filter(Assessment.checkin_id == checkin.id)
        .first()
    )

    alert = (
        db.query(Alert)
        .filter(Alert.assessment_id == assessment.id)
        .first()
    ) if assessment else None

    print("Check-in ID:", checkin.id)
    print("Assessment ID:", assessment.id if assessment else None)
    print("Risk level:", assessment.risk_level if assessment else None)
    print("Alert ID:", alert.id if alert else None)
    print("Alert type:", alert.alert_type if alert else None)
    print("Alert status:", alert.status if alert else None)

except Exception as exc:
    db.rollback()
    print("Test failed:", repr(exc))

finally:
    db.close()
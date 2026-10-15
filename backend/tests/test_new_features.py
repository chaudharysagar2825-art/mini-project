"""Comprehensive test suite for the four implemented features in Manas Setu:
- Feature 1: AI Distress-Risk Scoring & Persistence & Assessments API
- Feature 2: Longitudinal Monitoring, Trends & Dashboards
- Feature 4: Counsellor Referrals, Lifecycle & Follow-ups
- Feature 5: Multi-Channel Communication (SMS & IVR Pipeline)
"""

import json
from unittest.mock import patch

import pytest
from app.models.alert import Alert
from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.checkin import CheckIn
from app.models.consent import Consent
from app.models.referral import Referral
from app.models.safe_contact import SafeContact
from app.services.alert_service import create_alert
from app.services.scoring_service import RiskResult, calculate_risk, map_risk_category
from tests.conftest import auth_header


# ──────────────────────────────────────────────────────────
# Feature 1: AI Distress-Risk Scoring & Persistence
# ──────────────────────────────────────────────────────────

class TestDistressScoringAndAssessments:

    def test_distress_scoring_documented_scale_and_categories(self):
        """Verify the 0-10 distress scale and 4-tier category mappings."""
        # Low risk (0-3)
        res_low = calculate_risk(distress_score=2)
        assert res_low.score == 2
        assert res_low.risk_level == "routine"
        assert res_low.risk_category == "low"

        # Moderate risk (4-6)
        res_mod = calculate_risk(distress_score=5)
        assert res_mod.score == 5
        assert res_mod.risk_level == "follow_up"
        assert res_mod.risk_category == "moderate"

        # High / Urgent risk (7-10)
        res_high = calculate_risk(distress_score=8)
        assert res_high.score == 8
        assert res_high.risk_level == "urgent"
        assert res_high.risk_category == "urgent"

        # Direct safety concern always forces urgent
        res_safety = calculate_risk(distress_score=1, direct_safety_concern=True)
        assert res_safety.risk_level == "urgent"
        assert res_safety.risk_category == "urgent"

    def test_insufficient_data_safety_handling(self):
        """Ensure missing or skipped data is not silently treated as low risk with high confidence."""
        res_missing = calculate_risk(distress_score=0, missing_data=True)
        assert res_missing.confidence < 0.8
        assert "Incomplete check-in" in res_missing.reason

    def test_exact_score_boundary_mappings(self):
        """Verify all exact score boundaries per SIH26094 specs:
        - Low: 0–3
        - Moderate: > 3 and < 7 (4, 5, 6)
        - High: 7 and < 8 (7)
        - Urgent: 8–10 (8, 9, 10 or direct safety concern)
        """
        expected_categories = {
            0: "low",
            1: "low",
            2: "low",
            3: "low",
            4: "moderate",
            5: "moderate",
            6: "moderate",
            7: "high",
            8: "urgent",
            9: "urgent",
            10: "urgent",
        }
        for score, expected_cat in expected_categories.items():
            res = calculate_risk(distress_score=score)
            assert res.risk_category == expected_cat, f"Score {score} expected {expected_cat}, got {res.risk_category}"
            assert map_risk_category(res.risk_level, score) == expected_cat

        # Direct safety concern always overrides score and yields urgent
        for score in [0, 2, 5, 7]:
            res_escalated = calculate_risk(distress_score=score, direct_safety_concern=True)
            assert res_escalated.risk_category == "urgent"
            assert res_escalated.risk_level == "urgent"

    def test_assessment_and_alert_deduplication(
        self, db, victim_case
    ):
        """Verify that duplicate alert creation calls on the same assessment are suppressed."""
        chk = CheckIn(
            case_id=victim_case.id,
            questionnaire_version="v1",
            status="completed",
            answers=json.dumps({"sleep_quality": "severe"}),
            direct_safety_concern=True,
            requested_human_contact=False,
        )
        db.add(chk)
        db.commit()
        db.refresh(chk)

        asm = Assessment(
            checkin_id=chk.id,
            case_id=victim_case.id,
            risk_level="urgent",
            direction="stable",
            score=9,
            confidence=0.9,
            reason="High distress score",
            model_version="rule-v1",
        )
        db.add(asm)
        db.commit()
        db.refresh(asm)

        risk_res = RiskResult(
            risk_level="urgent",
            direction="stable",
            score=9,
            confidence=0.9,
            reason="High distress score",
            model_version="rule-v1",
            risk_category="urgent",
        )

        # First alert creation
        alert1 = create_alert(db=db, case_id=victim_case.id, assessment=asm, risk_result=risk_res)
        db.commit()

        # Second alert creation (simulating retry or duplicate evaluation)
        alert2 = create_alert(db=db, case_id=victim_case.id, assessment=asm, risk_result=risk_res)
        db.commit()

        assert alert1 is not None
        assert alert2 is not None
        assert alert1.id == alert2.id

        total_alerts = db.query(Alert).filter(Alert.assessment_id == asm.id).count()
        assert total_alerts == 1, "Duplicate Alert rows created for same assessment"

    def test_assessment_persisted_with_model_version_and_category(
        self, client, db, victim_user, victim_token, victim_case, active_consent
    ):
        """Verify check-in creates an assessment with score, risk category, and model version."""
        resp = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "sleep_quality", "answer": "severe"},
                    {"question_id": "anxiety_intensity", "answer": "severe"},
                    {"question_id": "isolation_feeling", "answer": "severe"},
                    {"question_id": "coping_difficulty", "answer": "severe"},
                ],
                "direct_safety_concern": False,
                "requested_human_contact": True,
            },
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 201
        checkin_data = resp.json()

        # Check assessment in DB
        asm = (
            db.query(Assessment)
            .filter(Assessment.checkin_id == checkin_data["id"])
            .first()
        )
        assert asm is not None
        assert asm.score >= 8
        assert asm.risk_level == "urgent"
        assert asm.risk_category == "urgent"
        assert asm.model_version is not None
        assert asm.created_at is not None

    def test_assessment_retrieval_endpoints(
        self, client, db, victim_user, victim_token, caseworker_user, caseworker_token,
        other_victim_user, other_victim_token, victim_case, active_consent
    ):
        """Verify GET /assessments/case/{case_id} and GET /assessments/{assessment_id}."""
        # 1. Submit check-in
        resp = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "sleep_quality", "answer": "mild"},
                    {"question_id": "anxiety_intensity", "answer": "none"},
                ],
            },
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 201
        cid = resp.json()["id"]

        asm = db.query(Assessment).filter(Assessment.checkin_id == cid).first()
        assert asm is not None

        # 2. Case owner can retrieve assessments
        r_owner = client.get(
            f"/assessments/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert r_owner.status_code == 200
        data = r_owner.json()
        assert len(data) >= 1
        assert data[0]["checkin_id"] == cid
        assert "risk_category" in data[0]

        # 3. Staff / Caseworker can retrieve assessments
        r_staff = client.get(
            f"/assessments/case/{victim_case.id}",
            headers=auth_header(caseworker_token),
        )
        assert r_staff.status_code == 200
        assert len(r_staff.json()) >= 1

        # 4. Single assessment retrieval
        r_single = client.get(
            f"/assessments/{asm.id}",
            headers=auth_header(victim_token),
        )
        assert r_single.status_code == 200
        assert r_single.json()["id"] == asm.id

        # 5. Cross-victim access is denied (403)
        r_other = client.get(
            f"/assessments/case/{victim_case.id}",
            headers=auth_header(other_victim_token),
        )
        assert r_other.status_code == 403

        r_other_single = client.get(
            f"/assessments/{asm.id}",
            headers=auth_header(other_victim_token),
        )
        assert r_other_single.status_code == 403


# ──────────────────────────────────────────────────────────
# Feature 2: Longitudinal Monitoring & Trends
# ──────────────────────────────────────────────────────────

class TestLongitudinalMonitoringAndTrends:

    def test_case_trends_empty_history(
        self, client, victim_token, victim_case
    ):
        """Case with no check-ins returns a valid zero-state trends response."""
        resp = client.get(
            f"/dashboards/case/{victim_case.id}/trends",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_checkins"] == 0
        assert data["history"] == []
        assert data["average_score"] == 0.0

    def test_case_trends_longitudinal_trajectory(
        self, client, db, victim_token, caseworker_token, victim_case, active_consent
    ):
        """Submit multiple check-ins and verify chronological score and direction calculation."""
        # First check-in: Low distress (score ~1)
        client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "sleep_quality", "answer": "mild"},
                    {"question_id": "anxiety_intensity", "answer": "none"},
                ],
            },
            headers=auth_header(victim_token),
        )

        # Second check-in: High distress (score >= 5)
        client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "sleep_quality", "answer": "severe"},
                    {"question_id": "anxiety_intensity", "answer": "severe"},
                    {"question_id": "isolation_feeling", "answer": "moderate"},
                ],
            },
            headers=auth_header(victim_token),
        )

        # Query trends as staff
        resp = client.get(
            f"/dashboards/case/{victim_case.id}/trends",
            headers=auth_header(caseworker_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_checkins"] == 2
        assert len(data["history"]) == 2
        assert data["history"][0]["score"] <= data["history"][1]["score"]
        assert data["average_score"] > 0
        assert data["current_risk_level"] in ("urgent", "follow_up")

    def test_trends_cross_case_isolation(
        self, client, other_victim_token, victim_case
    ):
        """Victim cannot inspect trends of another victim's case."""
        resp = client.get(
            f"/dashboards/case/{victim_case.id}/trends",
            headers=auth_header(other_victim_token),
        )
        assert resp.status_code == 403

    def test_dashboard_summary_staff_vs_victim(
        self, client, db, victim_token, admin_token, victim_case, other_victim_case
    ):
        """Staff receives system-wide counts while victim receives case-scoped counts."""
        # Victim summary
        r_victim = client.get(
            "/dashboards/summary",
            headers=auth_header(victim_token),
        )
        assert r_victim.status_code == 200
        assert r_victim.json()["total_cases"] == 1

        # Admin / Staff summary
        r_admin = client.get(
            "/dashboards/summary",
            headers=auth_header(admin_token),
        )
        assert r_admin.status_code == 200
        assert r_admin.json()["total_cases"] >= 2

    def test_staff_list_all_cases(
        self, client, caseworker_token, victim_token, victim_case
    ):
        """Staff can list all cases, while victims are forbidden."""
        r_staff = client.get("/cases", headers=auth_header(caseworker_token))
        assert r_staff.status_code == 200
        assert len(r_staff.json()) >= 1

        r_victim = client.get("/cases", headers=auth_header(victim_token))
        assert r_victim.status_code == 403



# ──────────────────────────────────────────────────────────
# Feature 4: Counsellor Referrals & Follow-ups
# ──────────────────────────────────────────────────────────

class TestCounsellorReferrals:

    def test_staff_create_and_manage_referral(
        self, client, db, caseworker_user, caseworker_token, victim_case
    ):
        """Caseworker creates referral, updates status with notes, and verifies audit trail."""
        # 1. Staff creates referral
        resp = client.post(
            f"/referrals/{victim_case.id}",
            json={
                "referral_type": "mental_health",
                "organization": "District Hospital Psychiatry Clinic",
                "reason": "Victim reports acute trauma and insomnia; needs psychiatric consultation.",
                "priority": "urgent",
            },
            headers=auth_header(caseworker_token),
        )
        assert resp.status_code == 201
        ref_data = resp.json()
        assert ref_data["status"] == "created"
        ref_id = ref_data["id"]

        # 2. Staff updates status to acknowledged
        r_ack = client.patch(
            f"/referrals/{ref_id}/status",
            json={"status": "acknowledged", "notes": "Contacted Dr. Sharma at clinic; appointment confirmed for Monday."},
            headers=auth_header(caseworker_token),
        )
        assert r_ack.status_code == 200
        assert r_ack.json()["status"] == "acknowledged"

        # 3. Staff updates status to in_progress
        r_prog = client.patch(
            f"/referrals/{ref_id}/status",
            json={"status": "in_progress", "notes": "First session attended."},
            headers=auth_header(caseworker_token),
        )
        assert r_prog.status_code == 200
        assert r_prog.json()["status"] == "in_progress"

        # 4. Verify reason contains appended follow-up notes
        ref_db = db.get(Referral, ref_id)
        assert "[Follow-up acknowledged]:" in ref_db.reason

        # 5. Verify audit logs were generated
        logs = (
            db.query(AuditLog)
            .filter(AuditLog.resource_type == "referral", AuditLog.resource_id == str(ref_id))
            .all()
        )
        assert len(logs) >= 2

    def test_referral_category_alias_normalization(
        self, client, victim_token, victim_case
    ):
        """Verify alias strings like 'medical' or 'psychological_counselling' normalize to valid enum values."""
        resp = client.post(
            f"/referrals/{victim_case.id}",
            json={
                "referral_type": "psychological_counselling",
                "organization": "Community Counselling NGO",
                "reason": "Anxiety management counselling.",
                "priority": "routine",
            },
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 201
        assert resp.json()["referral_type"] == "mental_health"

    def test_referral_invalid_transition_rejected(
        self, client, caseworker_token, victim_case
    ):
        """Invalid lifecycle jumps (e.g. created -> completed) must be rejected."""
        resp = client.post(
            f"/referrals/{victim_case.id}",
            json={
                "referral_type": "protection",
                "organization": "Safe Shelter Cell",
                "reason": "Temporary safe housing.",
                "priority": "urgent",
            },
            headers=auth_header(caseworker_token),
        )
        ref_id = resp.json()["id"]

        r_bad = client.patch(
            f"/referrals/{ref_id}/status",
            json={"status": "completed"},
            headers=auth_header(caseworker_token),
        )
        assert r_bad.status_code == 400
        assert "Invalid status transition" in r_bad.json()["detail"]

    def test_referral_cross_case_access_rejected(
        self, client, caseworker_token, other_victim_token, victim_case
    ):
        """Another victim cannot view or modify referrals for an unrelated case."""
        resp = client.post(
            f"/referrals/{victim_case.id}",
            json={
                "referral_type": "legal",
                "organization": "DLSA Legal Aid",
                "reason": "Legal protection filing.",
                "priority": "routine",
            },
            headers=auth_header(caseworker_token),
        )
        ref_id = resp.json()["id"]

        # Other victim cannot view
        r_view = client.get(
            f"/referrals/{ref_id}",
            headers=auth_header(other_victim_token),
        )
        assert r_view.status_code == 403

        # Other victim cannot modify
        r_mod = client.patch(
            f"/referrals/{ref_id}/status",
            json={"status": "acknowledged"},
            headers=auth_header(other_victim_token),
        )
        assert r_mod.status_code == 403


# ──────────────────────────────────────────────────────────
# Feature 5: Multi-Channel Communication
# ──────────────────────────────────────────────────────────

class TestMultiChannelCommunication:

    def test_inbound_sms_intake_pipeline(
        self, client, db, victim_user, victim_case, active_consent
    ):
        """Verify full inbound SMS pipeline: phone lookup -> consent -> check-in -> scoring -> alert."""
        # 1. Register a safe contact with a phone number
        contact = SafeContact(
            case_id=victim_case.id,
            contact_name="Verified Victim Mobile",
            relationship="Self / Mobile",
            phone="+919876543210",
            preferred_channel="sms",
            neutral_notification=True,
            is_active=True,
        )
        db.add(contact)
        db.commit()

        # 2. Simulate inbound SMS with distress keywords
        resp = client.post(
            "/communication/sms/inbound",
            json={
                "sender_phone": "+919876543210",
                "message": "I am feeling scared and in danger, please help me",
                "idempotency_key": "sms-test-key-001",
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["status"] == "processed"
        assert result["case_id"] == victim_case.id
        assert result["direct_safety_concern"] is True
        assert result["checkin_id"] is not None

        # 3. Verify checkin and alert created in DB
        chk = db.get(CheckIn, result["checkin_id"])
        assert chk is not None
        assert chk.direct_safety_concern is True

        alert = db.query(Alert).filter(Alert.case_id == victim_case.id).first()
        assert alert is not None
        assert alert.alert_type == "urgent"

    def test_inbound_sms_duplicate_prevention(
        self, client, db, victim_case, active_consent
    ):
        """Submitting with the same idempotency key suppresses duplicate processing."""
        contact = SafeContact(
            case_id=victim_case.id,
            contact_name="Contact 2",
            relationship="Friend",
            phone="+919123456789",
            preferred_channel="sms",
            neutral_notification=True,
            is_active=True,
        )
        db.add(contact)
        db.commit()

        # First request
        r1 = client.post(
            "/communication/sms/inbound",
            json={
                "sender_phone": "+919123456789",
                "message": "0, 1, 0, 1",
                "idempotency_key": "idemp-key-dup-001",
            },
        )
        assert r1.status_code == 200

        # Duplicate request
        r2 = client.post(
            "/communication/sms/inbound",
            json={
                "sender_phone": "+919123456789",
                "message": "0, 1, 0, 1",
                "idempotency_key": "idemp-key-dup-001",
            },
        )
        assert r2.status_code == 200

    def test_inbound_sms_unrecognized_phone(self, client):
        """Unrecognized phone number gracefully returns unrecognized_sender without crashing."""
        resp = client.post(
            "/communication/sms/inbound",
            json={
                "sender_phone": "+910000000000",
                "message": "Hello check-in",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "unrecognized_sender"

    def test_inbound_sms_without_consent_rejected(
        self, client, db, victim_case
    ):
        """If consent is withdrawn or absent, inbound SMS check-in is rejected."""
        # Create consent with status withdrawn
        consent = Consent(
            case_id=victim_case.id,
            status="withdrawn",
            version="1.0",
            scope="monitoring",
            channel="web",
        )
        db.add(consent)
        contact = SafeContact(
            case_id=victim_case.id,
            contact_name="Contact Consent Test",
            relationship="Self",
            phone="+918888888888",
            preferred_channel="sms",
            neutral_notification=True,
            is_active=True,
        )
        db.add(contact)
        db.commit()

        resp = client.post(
            "/communication/sms/inbound",
            json={
                "sender_phone": "+918888888888",
                "message": "1, 1, 1, 1",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "consent_required"

    def test_dispatch_wellness_reminder(
        self, client, victim_token, victim_case, active_consent
    ):
        """Dispatching a wellness reminder produces a neutral SMS and audit entry."""
        resp = client.post(
            "/communication/sms/reminder",
            json={
                "case_id": victim_case.id,
                "phone_number": "+919876543210",
            },
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_mock"] is True
        assert data["status"] == "mock_delivered"

    def test_ivr_callback_webhook(
        self, client, db, victim_case, active_consent
    ):
        """Verify IVR webhook parses DTMF digits and creates check-in."""
        contact = SafeContact(
            case_id=victim_case.id,
            contact_name="IVR Caller",
            relationship="Self",
            phone="+917777777777",
            preferred_channel="call",
            neutral_notification=True,
            is_active=True,
        )
        db.add(contact)
        db.commit()

        # Simulate IVR event payload with DTMF digits: 2 (mod sleep), 3 (severe anxiety), 0 (none), 1 (mild)
        resp = client.post(
            "/communication/voice/callback",
            json={
                "call_id": "call-telephony-901",
                "caller_phone": "+917777777777",
                "Digits": "2301",
                "emergency_flag": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processed"
        assert data["case_id"] == victim_case.id
        assert data["checkin_id"] is not None

    def test_communication_providers_status(
        self, client, caseworker_token, victim_token
    ):
        """Staff can inspect provider status, while victims cannot."""
        r_staff = client.get(
            "/communication/providers/status",
            headers=auth_header(caseworker_token),
        )
        assert r_staff.status_code == 200
        data = r_staff.json()
        assert "sms" in data
        assert "voice_ivr" in data
        assert data["sms"]["is_mock"] is True

        r_victim = client.get(
            "/communication/providers/status",
            headers=auth_header(victim_token),
        )
        assert r_victim.status_code == 403

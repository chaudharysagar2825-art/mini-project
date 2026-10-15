"""Comprehensive API tests for Manas Setu backend.

Covers: authentication, cases, check-ins, alerts, consent,
referrals, safe contacts, dashboards, and cross-user isolation.
"""

from unittest.mock import patch

from app.models.alert import Alert
from app.models.assessment import Assessment
from tests.conftest import auth_header


# ──────────────────────────────────────────────────────────
# Authentication Tests
# ──────────────────────────────────────────────────────────

class TestAuthentication:

    def test_login_success(self, client, victim_user):
        resp = client.post("/auth/login", json={
            "username": "testvictim",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, victim_user):
        resp = client.post("/auth/login", json={
            "username": "testvictim",
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/auth/login", json={
            "username": "nouser",
            "password": "SomePass123!",
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post("/auth/login", json={
            "username": "testvictim",
        })
        assert resp.status_code == 422

    def test_get_me_authenticated(self, client, victim_user, victim_token):
        resp = client.get("/auth/me", headers=auth_header(victim_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testvictim"
        assert data["role"] == "victim"
        assert data["is_active"] is True

    def test_get_me_no_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        resp = client.get("/auth/me", headers=auth_header("invalid.token.here"))
        assert resp.status_code == 401


# ──────────────────────────────────────────────────────────
# Case Tests
# ──────────────────────────────────────────────────────────

class TestCases:

    def test_create_case(self, client, victim_user, victim_token):
        resp = client.post("/cases", json={
            "case_code": "CASE-NEW001",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["case_code"] == "CASE-NEW001"
        assert data["status"] == "active"

    def test_create_case_unauthenticated(self, client):
        resp = client.post("/cases", json={
            "case_code": "CASE-NOAUTH",
        })
        assert resp.status_code == 401

    def test_get_my_cases(self, client, victim_user, victim_token, victim_case):
        resp = client.get("/cases/my", headers=auth_header(victim_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert any(c["case_code"] == "CASE-TEST001" for c in data)

    def test_get_case_by_id_owner(self, client, victim_user, victim_token, victim_case):
        resp = client.get(
            f"/cases/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["case_code"] == "CASE-TEST001"

    def test_get_case_by_id_other_user_forbidden(
        self, client, victim_case, other_victim_user, other_victim_token,
    ):
        resp = client.get(
            f"/cases/{victim_case.id}",
            headers=auth_header(other_victim_token),
        )
        assert resp.status_code == 403

    def test_get_case_not_found(self, client, victim_user, victim_token):
        resp = client.get("/cases/99999", headers=auth_header(victim_token))
        assert resp.status_code == 404


# ──────────────────────────────────────────────────────────
# Consent Tests
# ──────────────────────────────────────────────────────────

class TestConsent:

    def test_create_consent(self, client, victim_user, victim_token, victim_case):
        resp = client.post(f"/consent/{victim_case.id}", json={
            "status": "granted",
            "version": "1.0",
            "scope": "mental_health_checkins",
            "channel": "web",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "granted"
        assert data["case_id"] == victim_case.id

    def test_get_consent(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        resp = client.get(
            f"/consent/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "granted"

    def test_update_consent_status(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        resp = client.patch(
            f"/consent/{victim_case.id}/status?status_value=paused",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "paused"

    def test_consent_cross_user_forbidden(
        self, client, victim_case, other_victim_user, other_victim_token,
    ):
        resp = client.post(f"/consent/{victim_case.id}", json={
            "status": "granted",
            "version": "1.0",
            "scope": "test",
            "channel": "web",
        }, headers=auth_header(other_victim_token))
        assert resp.status_code == 403


# ──────────────────────────────────────────────────────────
# Check-in Tests (CRITICAL PATH)
# ──────────────────────────────────────────────────────────

LOW_DISTRESS_ANSWERS = [
    {"question_id": "q1", "answer": "not at all"},
    {"question_id": "q2", "answer": "never"},
    {"question_id": "q3", "answer": "none"},
]

HIGH_DISTRESS_ANSWERS = [
    {"question_id": "q1", "answer": "severe"},
    {"question_id": "q2", "answer": "almost always"},
    {"question_id": "q3", "answer": "severe"},
    {"question_id": "q4", "answer": "almost always"},
]


class TestCheckins:

    def test_submit_checkin_success(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
            "direct_safety_concern": False,
            "user_skipped_questions": [],
            "requested_human_contact": False,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["case_id"] == victim_case.id
        assert data["status"] == "submitted"
        assert data["questionnaire_version"] == "v1"
        assert "risk_level" in data

    def test_submit_checkin_no_consent(
        self, client, victim_user, victim_token, victim_case,
    ):
        """Check-in should fail when no consent record exists."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 400
        assert "consent" in resp.json()["detail"].lower()

    def test_submit_checkin_paused_consent(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Check-in should fail when consent is paused."""
        client.patch(
            f"/consent/{victim_case.id}/status?status_value=paused",
            headers=auth_header(victim_token),
        )
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 400
        assert "paused" in resp.json()["detail"].lower()

    def test_submit_checkin_withdrawn_consent(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Check-in should fail when consent is withdrawn."""
        client.patch(
            f"/consent/{victim_case.id}/status?status_value=withdrawn",
            headers=auth_header(victim_token),
        )
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 400
        assert "withdrawn" in resp.json()["detail"].lower()

    def test_submit_checkin_wrong_case(
        self, client, victim_case, active_consent,
        other_victim_user, other_victim_token,
    ):
        """Another user cannot submit check-ins against someone else's case."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(other_victim_token))
        assert resp.status_code == 403

    def test_submit_checkin_invalid_answers(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Empty answers list should be rejected by schema validation."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": [],
        }, headers=auth_header(victim_token))
        assert resp.status_code == 422

    def test_checkin_risk_level_persisted(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """After submitting, the returned risk_level should be non-null."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["risk_level"] is not None
        assert data["risk_level"] == "routine"

    def test_checkin_high_distress_risk_level(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """High distress answers should produce urgent risk level."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
            "direct_safety_concern": False,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["risk_level"] in ("urgent", "follow_up")

    def test_direct_safety_concern_urgent(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """direct_safety_concern=True should always produce urgent risk."""
        resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
            "direct_safety_concern": True,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        assert resp.json()["risk_level"] == "urgent"

    def test_get_checkins_for_case(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        # Submit first
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        resp = client.get(
            f"/checkins/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_get_checkin_by_id(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        create_resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        checkin_id = create_resp.json()["id"]

        resp = client.get(
            f"/checkins/{checkin_id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == checkin_id

    def test_get_checkin_cross_user_forbidden(
        self, client, victim_user, victim_token, victim_case, active_consent,
        other_victim_user, other_victim_token,
    ):
        create_resp = client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))
        checkin_id = create_resp.json()["id"]

        resp = client.get(
            f"/checkins/{checkin_id}",
            headers=auth_header(other_victim_token),
        )
        assert resp.status_code == 403


# ──────────────────────────────────────────────────────────
# Alert Tests
# ──────────────────────────────────────────────────────────

class TestAlerts:

    def test_alert_created_for_high_distress(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Submitting high-distress answers should generate an alert."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        alerts = resp.json()
        assert len(alerts) >= 1

    def test_no_alert_for_low_distress(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Low distress answers should not generate an alert."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": LOW_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        alerts = resp.json()
        assert len(alerts) == 0

    def test_admin_can_action_alert(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Admin should be able to resolve an alert."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "resolve",
            "reason": "Test resolution",
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"

    def test_victim_cannot_action_alert(
        self, client, victim_user, victim_token, victim_case, active_consent,
    ):
        """Victims should not be able to perform admin actions on alerts."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "resolve",
            "reason": "Should fail",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 403

    def test_get_alert_cross_user_forbidden(
        self, client, victim_user, victim_token, victim_case, active_consent,
        other_victim_user, other_victim_token,
    ):
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.get(
            f"/alerts/{alert_id}",
            headers=auth_header(other_victim_token),
        )
        assert resp.status_code == 403

    def test_admin_assign_alert_success(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Admin can assign an alert to an authorized staff member."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "assign",
            "assigned_to": admin_user.id,
            "reason": "Assigning to staff",
        }, headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "assigned"
        assert data["assigned_to"] == admin_user.id

    def test_admin_assign_alert_missing_assignee(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Assigning an alert without assigned_to must fail."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "assign",
            "reason": "No assignee specified",
        }, headers=auth_header(admin_token))
        assert resp.status_code == 400
        assert "assignee" in resp.json()["detail"].lower()

    def test_admin_assign_alert_invalid_assignee(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Assigning an alert to nonexistent user must fail."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "assign",
            "assigned_to": 99999,
        }, headers=auth_header(admin_token))
        assert resp.status_code == 400

    def test_admin_assign_alert_to_victim_fails(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Assigning an alert to a victim account must fail."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "assign",
            "assigned_to": victim_user.id,
        }, headers=auth_header(admin_token))
        assert resp.status_code == 400
        assert "victim" in resp.json()["detail"].lower()

    def test_admin_update_resolved_alert_fails(
        self, client, victim_user, victim_token, admin_user, admin_token,
        victim_case, active_consent,
    ):
        """Updating an alert that is already resolved must fail."""
        client.post(f"/checkins/{victim_case.id}", json={
            "questionnaire_version": "v1",
            "answers": HIGH_DISTRESS_ANSWERS,
        }, headers=auth_header(victim_token))

        alerts_resp = client.get(
            f"/alerts/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        alert_id = alerts_resp.json()[0]["id"]

        # First resolve it
        res = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "resolve",
        }, headers=auth_header(admin_token))
        assert res.status_code == 200

        # Attempting further action must fail
        resp = client.patch(f"/alerts/{alert_id}/action", json={
            "action": "escalate",
        }, headers=auth_header(admin_token))
        assert resp.status_code == 400
        assert "resolved" in resp.json()["detail"].lower()


# ──────────────────────────────────────────────────────────
# Referral Tests
# ──────────────────────────────────────────────────────────

class TestReferrals:

    def test_create_referral(
        self, client, victim_user, victim_token, victim_case,
    ):
        resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "mental_health",
            "organization": "Test Mental Health Center",
            "reason": "Needs counseling support",
            "priority": "routine",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["referral_type"] == "mental_health"
        assert data["status"] == "created"

    def test_get_referrals_for_case(
        self, client, victim_user, victim_token, victim_case,
    ):
        client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "welfare",
            "organization": "Welfare Org",
            "reason": "Support needed",
        }, headers=auth_header(victim_token))

        resp = client.get(
            f"/referrals/case/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_update_referral_status(
        self, client, victim_user, victim_token, victim_case,
    ):
        create_resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "legal",
            "organization": "Legal Aid",
            "reason": "Legal assistance",
        }, headers=auth_header(victim_token))
        referral_id = create_resp.json()["id"]

        resp = client.patch(
            f"/referrals/{referral_id}/status?status_value=acknowledged",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "acknowledged"

    def test_update_referral_status_via_json_body(
        self, client, victim_user, victim_token, victim_case,
    ):
        """Updating referral status using JSON request body must succeed."""
        create_resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "mental_health",
            "organization": "Counseling Service",
            "reason": "Trauma support",
        }, headers=auth_header(victim_token))
        referral_id = create_resp.json()["id"]

        resp = client.patch(
            f"/referrals/{referral_id}/status",
            json={"status": "acknowledged"},
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "acknowledged"

    def test_update_referral_status_invalid_transition(
        self, client, victim_user, victim_token, victim_case,
    ):
        """Invalid referral status transition (e.g. from created directly to completed) must fail."""
        create_resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "legal",
            "organization": "Legal Aid",
            "reason": "Test",
        }, headers=auth_header(victim_token))
        referral_id = create_resp.json()["id"]

        resp = client.patch(
            f"/referrals/{referral_id}/status",
            json={"status": "completed"},
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()

    def test_update_referral_status_missing_payload(
        self, client, victim_user, victim_token, victim_case,
    ):
        """PATCH without body or query parameter must return 400."""
        create_resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "legal",
            "organization": "Legal Aid",
            "reason": "Test",
        }, headers=auth_header(victim_token))
        referral_id = create_resp.json()["id"]

        resp = client.patch(
            f"/referrals/{referral_id}/status",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 400

    def test_staff_can_update_referral_status(
        self, client, victim_user, victim_token, admin_user, admin_token, victim_case,
    ):
        """Admin or staff can update referral status on behalf of a victim."""
        create_resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "welfare",
            "organization": "Relief Service",
            "reason": "Assistance needed",
        }, headers=auth_header(victim_token))
        referral_id = create_resp.json()["id"]

        resp = client.patch(
            f"/referrals/{referral_id}/status",
            json={"status": "acknowledged"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "acknowledged"

    def test_referral_cross_user_forbidden(
        self, client, victim_case, other_victim_user, other_victim_token,
    ):
        resp = client.post(f"/referrals/{victim_case.id}", json={
            "referral_type": "mental_health",
            "organization": "Test Org",
            "reason": "Test",
        }, headers=auth_header(other_victim_token))
        assert resp.status_code == 403


# ──────────────────────────────────────────────────────────
# Safe Contact Tests
# ──────────────────────────────────────────────────────────

class TestSafeContacts:

    def test_create_safe_contact(
        self, client, victim_user, victim_token, victim_case,
    ):
        resp = client.post(f"/safe-contacts/{victim_case.id}", json={
            "contact_name": "Trusted Person",
            "relationship": "friend",
            "phone": "+919876543210",
            "preferred_channel": "sms",
            "neutral_notification": True,
        }, headers=auth_header(victim_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["contact_name"] == "Trusted Person"
        assert data["is_active"] is True

    def test_list_safe_contacts(
        self, client, victim_user, victim_token, victim_case,
    ):
        client.post(f"/safe-contacts/{victim_case.id}", json={
            "contact_name": "Contact A",
            "relationship": "family",
            "phone": "+911234567890",
            "preferred_channel": "call",
        }, headers=auth_header(victim_token))

        resp = client.get(
            f"/safe-contacts/{victim_case.id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_deactivate_safe_contact(
        self, client, victim_user, victim_token, victim_case,
    ):
        create_resp = client.post(f"/safe-contacts/{victim_case.id}", json={
            "contact_name": "To Deactivate",
            "relationship": "colleague",
            "phone": "+910000000000",
            "preferred_channel": "sms",
        }, headers=auth_header(victim_token))
        contact_id = create_resp.json()["id"]

        resp = client.delete(
            f"/safe-contacts/{victim_case.id}/{contact_id}",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_safe_contact_cross_user_forbidden(
        self, client, victim_case, other_victim_user, other_victim_token,
    ):
        resp = client.post(f"/safe-contacts/{victim_case.id}", json={
            "contact_name": "Hack Contact",
            "relationship": "unknown",
            "phone": "+910000000001",
            "preferred_channel": "sms",
        }, headers=auth_header(other_victim_token))
        assert resp.status_code == 403


# ──────────────────────────────────────────────────────────
# Dashboard Tests
# ──────────────────────────────────────────────────────────

class TestDashboard:

    def test_dashboard_summary(
        self, client, victim_user, victim_token, victim_case,
    ):
        resp = client.get(
            "/dashboards/summary",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total_cases" in data
        assert "open_alerts" in data
        assert "active_referrals" in data


# ──────────────────────────────────────────────────────────
# Audit Log Tests
# ──────────────────────────────────────────────────────────

class TestAuditLogs:

    def test_get_my_audit_logs(
        self, client, victim_user, victim_token,
    ):
        resp = client.get("/audit", headers=auth_header(victim_token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_resource_audit_logs_requires_admin(
        self, client, victim_user, victim_token,
    ):
        resp = client.get(
            "/audit/resource?resource_type=checkin&resource_id=1",
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 403

    def test_resource_audit_logs_admin_allowed(
        self, client, admin_user, admin_token,
    ):
        resp = client.get(
            "/audit/resource?resource_type=checkin&resource_id=1",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200


# ──────────────────────────────────────────────────────────
# Voice Analysis Tests
# ──────────────────────────────────────────────────────────

class TestVoice:

    def test_voice_analyze(self, client, victim_user, victim_token):
        resp = client.post("/voice/analyze", json={
            "text": "I feel sad and hopeless",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data["result"]["distress_score"] > 0

    def test_voice_analyze_empty_text(self, client, victim_user, victim_token):
        resp = client.post("/voice/analyze", json={
            "text": "",
        }, headers=auth_header(victim_token))
        assert resp.status_code == 400

    def test_voice_analyze_unauthenticated(self, client):
        resp = client.post("/voice/analyze", json={
            "text": "test",
        })
        assert resp.status_code == 401


# ──────────────────────────────────────────────────────────
# Health and Root Tests
# ──────────────────────────────────────────────────────────

class TestHealthAndRoot:

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "running" in resp.json()["message"].lower()

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


# ──────────────────────────────────────────────────────────
# CORS Tests
# ──────────────────────────────────────────────────────────

class TestCORS:

    def test_cors_allowed_origin(self, client):
        """Allowed origin receives Access-Control-Allow-Origin header."""
        resp = client.options("/health", headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "GET",
        })
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:8501"

    def test_cors_disallowed_origin(self, client):
        """Disallowed origin does NOT receive Access-Control-Allow-Origin header."""
        resp = client.options("/health", headers={
            "Origin": "http://evil-untrusted-domain.com",
            "Access-Control-Request-Method": "GET",
        })
        assert resp.headers.get("access-control-allow-origin") is None


# ──────────────────────────────────────────────────────────
# AI Pipeline & Baseline Integration Tests
# ──────────────────────────────────────────────────────────

class TestAIPipelineAndBaselineIntegration:

    def test_ai_crisis_signals_trigger_urgent_risk_and_alert(
        self, client, victim_user, victim_token, victim_case, active_consent, db,
    ):
        """When check-in answers contain textual crisis signals (e.g. hopeless, alone, cannot cope),
        the AI NLP crisis signal detector must flag safety concern, produce 'urgent' risk level,
        enrich assessment with AI Decision Support, and generate an urgent alert."""
        crisis_answers = [
            {"question_id": "feelings", "answer": "I feel hopeless and completely alone"},
            {"question_id": "coping", "answer": "It is too much to handle and I cannot cope"},
        ]
        resp = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": crisis_answers,
                "direct_safety_concern": False,
            },
            headers=auth_header(victim_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["risk_level"] == "urgent"

        # Verify Assessment details in database
        assessment = (
            db.query(Assessment)
            .filter(Assessment.checkin_id == data["id"])
            .first()
        )
        assert assessment is not None
        assert assessment.risk_level == "urgent"
        assert "rule-v1+ai-pipeline-v1" in assessment.model_version
        assert "AI Decision Support:" in assessment.reason
        assert "Detected signals:" in assessment.reason

        # Verify an Alert was generated
        alert = (
            db.query(Alert)
            .filter(Alert.assessment_id == assessment.id)
            .first()
        )
        assert alert is not None
        assert alert.alert_type == "urgent"
        assert alert.risk_level == "urgent"
        assert "AI Decision Support:" in alert.reason

    def test_baseline_tracking_across_multiple_checkins(
        self, client, victim_user, victim_token, victim_case, active_consent, db,
    ):
        """Test multi-check-in baseline trend tracking:
        1st check-in: Baseline score is None -> direction is 'unknown'
        2nd check-in: Distress increases (+5) -> direction is 'worsening'
        3rd check-in: Distress decreases (-6) -> direction is 'improving'
        """
        # First check-in: Low distress (score = 1)
        resp1 = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "q1", "answer": "mild"},  # 1
                    {"question_id": "q2", "answer": "none"},  # 0
                ],
            },
            headers=auth_header(victim_token),
        )
        assert resp1.status_code == 201
        checkin1_id = resp1.json()["id"]

        a1 = db.query(Assessment).filter(Assessment.checkin_id == checkin1_id).first()
        assert a1 is not None
        assert a1.score == 1
        assert a1.direction == "unknown"

        # Second check-in: High distress (score = 6)
        resp2 = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "q1", "answer": "severe"},  # 3
                    {"question_id": "q2", "answer": "severe"},  # 3
                ],
            },
            headers=auth_header(victim_token),
        )
        assert resp2.status_code == 201
        checkin2_id = resp2.json()["id"]

        a2 = db.query(Assessment).filter(Assessment.checkin_id == checkin2_id).first()
        assert a2 is not None
        assert a2.score == 6
        assert a2.direction == "worsening"
        assert "Distress increased by 5 points from baseline" in a2.reason

        # Third check-in: Distress resolves (score = 0)
        resp3 = client.post(
            f"/checkins/{victim_case.id}",
            json={
                "questionnaire_version": "v1",
                "answers": [
                    {"question_id": "q1", "answer": "none"},  # 0
                    {"question_id": "q2", "answer": "none"},  # 0
                ],
            },
            headers=auth_header(victim_token),
        )
        assert resp3.status_code == 201
        checkin3_id = resp3.json()["id"]

        a3 = db.query(Assessment).filter(Assessment.checkin_id == checkin3_id).first()
        assert a3 is not None
        assert a3.score == 0
        assert a3.direction == "improving"
        assert "Distress decreased by 6 points from baseline" in a3.reason

    def test_ai_pipeline_graceful_fallback_on_error(
        self, client, victim_user, victim_token, victim_case, active_consent, db,
    ):
        """If the AI pipeline raises an unexpected exception, the check-in must still succeed
        safely with the deterministic rule engine (no unhandled 500 error)."""
        with patch("app.services.ai__services.analyze_checkin_answers", side_effect=RuntimeError("AI pipeline crash")):
            resp = client.post(
                f"/checkins/{victim_case.id}",
                json={
                    "questionnaire_version": "v1",
                    "answers": [
                        {"question_id": "q1", "answer": "mild"},
                    ],
                },
                headers=auth_header(victim_token),
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "submitted"

            assessment = (
                db.query(Assessment)
                .filter(Assessment.checkin_id == data["id"])
                .first()
            )
            assert assessment is not None
            assert assessment.model_version == "rule-v1"
            assert "AI Decision Support" not in assessment.reason

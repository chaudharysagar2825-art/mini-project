"""Manas Setu API Client.

Provides a unified, resilient interface for the Streamlit frontend
to communicate with the FastAPI backend.
"""

from typing import Any
import requests


class APIError(Exception):
    """Custom exception containing status code and error details."""

    def __init__(self, status_code: int, message: str, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details


class ManasSetuClient:
    """Client for Manas Setu REST API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _headers(self, token: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code >= 400:
            error_detail = "An error occurred"
            if isinstance(data, dict) and "detail" in data:
                error_detail = data["detail"]
                if isinstance(error_detail, list):
                    # Pydantic validation error list
                    formatted = []
                    for item in error_detail:
                        loc = " -> ".join(str(l) for l in item.get("loc", []))
                        msg = item.get("msg", "")
                        formatted.append(f"{loc}: {msg}" if loc else msg)
                    error_detail = "; ".join(formatted)
            elif isinstance(data, str) and data:
                error_detail = data

            raise APIError(response.status_code, str(error_detail), details=data)

        return data

    def check_health(self) -> dict[str, Any]:
        """Check if backend is reachable and healthy."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=4)
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Backend connection failed at {self.base_url}: {exc}")

    # ── Auth ──────────────────────────────────────────────────────────
    def login(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate user and obtain JWT token."""
        try:
            r = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                headers=self._headers(),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Unable to reach authentication service: {exc}")

    def get_me(self, token: str) -> dict[str, Any]:
        """Get profile and role of currently authenticated user."""
        try:
            r = requests.get(
                f"{self.base_url}/auth/me",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to retrieve user profile: {exc}")

    # ── Cases ─────────────────────────────────────────────────────────
    def get_my_cases(self, token: str) -> list[dict[str, Any]]:
        """List cases belonging to the authenticated user."""
        try:
            r = requests.get(
                f"{self.base_url}/cases/my",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load cases: {exc}")

    def generate_case(self, token: str) -> dict[str, Any]:
        """Generate a new case for the user with an auto-generated code."""
        try:
            r = requests.post(
                f"{self.base_url}/cases/generate",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to generate case: {exc}")

    def create_case(self, token: str, case_code: str) -> dict[str, Any]:
        """Create a new case with an explicit case code."""
        try:
            r = requests.post(
                f"{self.base_url}/cases",
                json={"case_code": case_code},
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to create case: {exc}")

    def get_case(self, token: str, case_id: int) -> dict[str, Any]:
        """Retrieve details of a specific case."""
        try:
            r = requests.get(
                f"{self.base_url}/cases/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load case {case_id}: {exc}")

    # ── Consent ───────────────────────────────────────────────────────
    def get_consent(self, token: str, case_id: int) -> dict[str, Any] | None:
        """Get latest consent record for a case, or None if not found."""
        try:
            r = requests.get(
                f"{self.base_url}/consent/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except APIError as e:
            if e.status_code == 404:
                return None
            raise
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load consent: {exc}")

    def create_consent(
        self,
        token: str,
        case_id: int,
        status: str = "granted",
        version: str = "v1",
        scope: str = "monitoring",
        channel: str = "web",
    ) -> dict[str, Any]:
        """Record initial consent for a case."""
        try:
            r = requests.post(
                f"{self.base_url}/consent/{case_id}",
                json={
                    "status": status,
                    "version": version,
                    "scope": scope,
                    "channel": channel,
                },
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to create consent: {exc}")

    def update_consent_status(
        self,
        token: str,
        case_id: int,
        status_value: str,
    ) -> dict[str, Any]:
        """Update consent status (granted, paused, withdrawn)."""
        try:
            r = requests.patch(
                f"{self.base_url}/consent/{case_id}/status?status_value={status_value}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to update consent status: {exc}")

    # ── Check-ins ─────────────────────────────────────────────────────
    def submit_checkin(
        self,
        token: str,
        case_id: int,
        answers: list[dict[str, str]],
        questionnaire_version: str = "v1",
        direct_safety_concern: bool | None = None,
        user_skipped_questions: list[str] | None = None,
        requested_human_contact: bool = False,
    ) -> dict[str, Any]:
        """Submit a well-being check-in questionnaire."""
        payload = {
            "questionnaire_version": questionnaire_version,
            "answers": answers,
            "direct_safety_concern": direct_safety_concern,
            "user_skipped_questions": user_skipped_questions or [],
            "requested_human_contact": requested_human_contact,
        }
        try:
            r = requests.post(
                f"{self.base_url}/checkins/{case_id}",
                json=payload,
                headers=self._headers(token),
                timeout=15,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to submit check-in: {exc}")

    def get_case_checkins(self, token: str, case_id: int) -> list[dict[str, Any]]:
        """List historical check-ins for a case."""
        try:
            r = requests.get(
                f"{self.base_url}/checkins/case/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load check-ins: {exc}")

    def get_checkin(self, token: str, checkin_id: int) -> dict[str, Any]:
        """Get details for a single check-in."""
        try:
            r = requests.get(
                f"{self.base_url}/checkins/{checkin_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load check-in {checkin_id}: {exc}")

    # ── Alerts ────────────────────────────────────────────────────────
    def get_alerts_queue(self, token: str) -> list[dict[str, Any]]:
        """Retrieve recent alerts for staff triage queue."""
        try:
            r = requests.get(
                f"{self.base_url}/alerts",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load alert queue: {exc}")

    def get_case_alerts(self, token: str, case_id: int) -> list[dict[str, Any]]:
        """List alerts associated with a specific case."""
        try:
            r = requests.get(
                f"{self.base_url}/alerts/case/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load alerts for case {case_id}: {exc}")

    def get_alert(self, token: str, alert_id: int) -> dict[str, Any]:
        """Get single alert details."""
        try:
            r = requests.get(
                f"{self.base_url}/alerts/{alert_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load alert {alert_id}: {exc}")

    def action_alert(
        self,
        token: str,
        alert_id: int,
        action: str,
        assigned_to: int | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Triage, assign, resolve, or dismiss an alert (staff/admin only)."""
        payload: dict[str, Any] = {"action": action}
        if assigned_to is not None:
            payload["assigned_to"] = assigned_to
        if reason is not None:
            payload["reason"] = reason

        try:
            r = requests.patch(
                f"{self.base_url}/alerts/{alert_id}/action",
                json=payload,
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to update alert {alert_id}: {exc}")

    # ── Referrals ─────────────────────────────────────────────────────
    def get_case_referrals(self, token: str, case_id: int) -> list[dict[str, Any]]:
        """List referrals for a specific case."""
        try:
            r = requests.get(
                f"{self.base_url}/referrals/case/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load referrals: {exc}")

    def create_referral(
        self,
        token: str,
        case_id: int,
        referral_type: str,
        organization: str,
        reason: str,
        priority: str = "routine",
    ) -> dict[str, Any]:
        """Create a new referral request for support services."""
        try:
            r = requests.post(
                f"{self.base_url}/referrals/{case_id}",
                json={
                    "referral_type": referral_type,
                    "organization": organization,
                    "reason": reason,
                    "priority": priority,
                },
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to create referral: {exc}")

    def update_referral_status(
        self,
        token: str,
        referral_id: int,
        status: str,
    ) -> dict[str, Any]:
        """Update referral status (created -> acknowledged -> in_progress -> completed/cancelled)."""
        try:
            r = requests.patch(
                f"{self.base_url}/referrals/{referral_id}/status",
                json={"status": status},
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to update referral status: {exc}")

    # ── Safe Contacts ─────────────────────────────────────────────────
    def get_safe_contacts(self, token: str, case_id: int) -> list[dict[str, Any]]:
        """List active safe contacts for a case."""
        try:
            r = requests.get(
                f"{self.base_url}/safe-contacts/{case_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load safe contacts: {exc}")

    def create_safe_contact(
        self,
        token: str,
        case_id: int,
        contact_name: str,
        relationship: str,
        phone: str,
        preferred_language: str = "en",
        preferred_channel: str = "call",
        safe_time: str | None = None,
        neutral_notification: bool = True,
        fallback_contact: bool = False,
    ) -> dict[str, Any]:
        """Add a trusted safe contact."""
        try:
            r = requests.post(
                f"{self.base_url}/safe-contacts/{case_id}",
                json={
                    "contact_name": contact_name,
                    "relationship": relationship,
                    "phone": phone,
                    "preferred_language": preferred_language,
                    "preferred_channel": preferred_channel,
                    "safe_time": safe_time,
                    "neutral_notification": neutral_notification,
                    "fallback_contact": fallback_contact,
                },
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to create safe contact: {exc}")

    def deactivate_safe_contact(
        self,
        token: str,
        case_id: int,
        contact_id: int,
    ) -> dict[str, Any]:
        """Deactivate a safe contact."""
        try:
            r = requests.delete(
                f"{self.base_url}/safe-contacts/{case_id}/{contact_id}",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to deactivate safe contact: {exc}")

    # ── Dashboard & Audit ─────────────────────────────────────────────
    def get_dashboard_summary(self, token: str) -> dict[str, Any]:
        """Get aggregated counts for cases, alerts, and referrals."""
        try:
            r = requests.get(
                f"{self.base_url}/dashboards/summary",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load dashboard summary: {exc}")

    def get_audit_logs(self, token: str) -> list[dict[str, Any]]:
        """Get user audit logs."""
        try:
            r = requests.get(
                f"{self.base_url}/audit",
                headers=self._headers(token),
                timeout=10,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to load audit logs: {exc}")

    # ── Voice / Text Journal Analysis ─────────────────────────────────
    def analyze_voice_text(self, token: str, text: str) -> dict[str, Any]:
        """Analyze text for sentiment, crisis signals, and distress indicators."""
        try:
            r = requests.post(
                f"{self.base_url}/voice/analyze",
                json={"text": text},
                headers=self._headers(token),
                timeout=15,
            )
            return self._handle_response(r)
        except requests.RequestException as exc:
            raise APIError(503, f"Failed to analyze text: {exc}")

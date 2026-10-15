"""Redesigned clinical decision-support and caseworker triage portal for Manas Setu."""

from typing import Any
import streamlit as st
from api_client import APIError, ManasSetuClient
from theme import render_badge


def render_staff_portal(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_nav: str,
) -> None:
    """Main staff portal router dispatching to dedicated triage views."""

    if active_nav == "Overview":
        _render_staff_overview(client, token, user)
    elif active_nav == "Alert Queue":
        _render_staff_alerts(client, token, user)
    elif active_nav == "Case Referrals":
        _render_staff_referrals(client, token, user)
    elif active_nav == "Audit Logs":
        _render_staff_audit(client, token, user)
    else:
        _render_staff_overview(client, token, user)


# ──────────────────────────────────────────────────────────
# 1. Staff Overview
# ──────────────────────────────────────────────────────────

def _render_staff_overview(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render caseworker overview metrics and operational summary."""

    username = user.get("username", "Staff Member")
    role_name = user.get("role", "caseworker").capitalize()

    st.markdown(
        f"""
        <div class="ms-hero-banner" style="background: linear-gradient(135deg, #134e4a 0%, #1e3a8a 100%);">
            <h2 class="ms-hero-title">Caseworker Portal — {username}</h2>
            <p class="ms-hero-subtitle">
                Role: <strong>{role_name}</strong> • Human-supervised triage and clinical care coordination.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Metrics from API
    try:
        summary = client.get_dashboard_summary(token)
    except APIError as e:
        st.warning(f"Unable to load summary metrics: {e.message}")
        summary = {}

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Active Support Cases</div>
                <div class="ms-stat-value">{summary.get('total_cases', 0)}</div>
                <div class="ms-stat-desc">Cases registered under your care</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Open Distress Alerts</div>
                <div class="ms-stat-value" style="color: #991b1b;">{summary.get('open_alerts', 0)}</div>
                <div class="ms-stat-desc">Requiring review or follow-up</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Pending Referrals</div>
                <div class="ms-stat-value">{summary.get('active_referrals', 0)}</div>
                <div class="ms-stat-desc">External service coordination</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Operational Quick Actions
    c_queue_card, c_ref_card = st.columns(2)

    with c_queue_card:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>🚨 Distress Alert Triage</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "Review automated risk assessments, identify longitudinal distress trends, "
                "and assign caseworkers to high-distress cases."
            )
            if st.button("Open Alert Triage Queue →", type="primary", use_container_width=True):
                st.session_state.current_nav = "Alert Queue"
                st.rerun()

    with c_ref_card:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #0f4c5c; margin-top: 0;'>🤝 Multi-Agency Referrals</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "Coordinate external medical, legal, and shelter services for victims, "
                "and manage referral status progression."
            )
            if st.button("Manage Referrals →", type="secondary", use_container_width=True):
                st.session_state.current_nav = "Case Referrals"
                st.rerun()


# ──────────────────────────────────────────────────────────
# 2. Alert Queue
# ──────────────────────────────────────────────────────────

def _render_staff_alerts(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render triage queue with filter controls and actioning drawers."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Distress Alert Triage Queue</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Clinical decision support: alerts generated by deterministic risk rules and AI crisis detection.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    is_admin = user.get("role") == "admin"

    # Filters
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        status_filter = st.selectbox(
            "Status Filter",
            options=["All", "Open", "Assigned", "Escalated", "Resolved", "Dismissed"],
            index=0,
        )
    with c_f2:
        risk_filter = st.selectbox(
            "Risk Priority Filter",
            options=["All", "Urgent", "Follow_Up"],
            index=0,
        )

    try:
        alerts = client.get_alerts_queue(token)
    except APIError as e:
        st.error(f"Failed to load alert queue: {e.message}")
        return

    # Filter alerts
    if status_filter != "All":
        alerts = [a for a in alerts if a.get("status", "").lower() == status_filter.lower()]
    if risk_filter != "All":
        alerts = [a for a in alerts if a.get("risk_level", "").lower() == risk_filter.lower()]

    if not alerts:
        st.markdown(
            """
            <div class="ms-empty-state">
                <div class="ms-empty-icon">✅</div>
                <h4 style="color: #0f4c5c; margin-bottom: 4px;">No Alerts Matching Filter</h4>
                <p style="margin: 0; font-size: 0.9rem;">The alert triage queue is clear for the selected criteria.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.write(f"Showing **{len(alerts)}** alert(s):")

    for a in alerts:
        aid = a.get("id")
        risk = a.get("risk_level", "routine")
        status_val = a.get("status", "open")
        direction = a.get("direction", "unknown")
        case_id = a.get("case_id")
        created_at = a.get("created_at", "")[:16].replace("T", " ")

        risk_badge = render_badge(risk)
        status_badge = render_badge(status_val)

        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            with h1:
                st.markdown(f"#### Alert #{aid} • Case #{case_id}")
                st.caption(f"Created: {created_at} • Direction: `{direction.capitalize()}` • Confidence: `{a.get('confidence', 'N/A')}`")
            with h2:
                st.markdown(f"<div style='text-align: right;'>{risk_badge} {status_badge}</div>", unsafe_allow_html=True)

            # Clinical Decision Support Summary
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border-left: 3px solid #0f4c5c; padding: 10px 14px; border-radius: 4px; margin: 8px 0; font-size: 0.88rem; color: #334155;">
                    <strong>Decision Support Rationale:</strong> {a.get('reason', 'None recorded')}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Assignee & Action controls
            assignee = a.get("assigned_to")
            assigned_str = f"Staff ID #{assignee}" if assignee else "Unassigned"
            st.caption(f"Assigned To: **{assigned_str}**")

            if status_val in ("resolved", "dismissed"):
                st.caption(f"Alert is in terminal state: `{status_val}`.")
            else:
                if not is_admin:
                    st.caption("ℹ️ Caseworkers have triage view access. Assignment and resolution require `admin` authorization.")
                else:
                    with st.expander(f"⚙️ Triage Action — Alert #{aid}"):
                        with st.form(f"action_alert_form_{aid}"):
                            action_choice = st.selectbox(
                                "Select Triage Action",
                                options=["acknowledge", "assign", "escalate", "resolve", "dismiss"],
                                key=f"sel_act_{aid}",
                            )
                            assign_to_id = None
                            if action_choice == "assign":
                                assign_to_id = st.number_input(
                                    "Assign to Staff User ID",
                                    min_value=1,
                                    value=user.get("id", 1),
                                    step=1,
                                    key=f"input_assignee_{aid}",
                                )
                            action_notes = st.text_input(
                                "Clinical Justification / Action Notes",
                                placeholder="e.g. Outreach conducted, victim connected to safe housing.",
                                key=f"input_notes_{aid}",
                            )
                            sub_action = st.form_submit_button("Confirm Action", type="primary")

                        if sub_action:
                            try:
                                client.action_alert(
                                    token=token,
                                    alert_id=aid,
                                    action=action_choice,
                                    assigned_to=int(assign_to_id) if assign_to_id is not None else None,
                                    reason=action_notes.strip() if action_notes.strip() else None,
                                )
                                st.success(f"Alert #{aid} updated successfully.")
                                st.rerun()
                            except APIError as exc:
                                st.error(f"Action failed: {exc.message}")


# ──────────────────────────────────────────────────────────
# 3. Case Referrals Management
# ──────────────────────────────────────────────────────────

def _render_staff_referrals(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render case referrals review and status management."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Case Referrals Coordination</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Review and transition support referrals for partner organizations (medical, DLSA legal, shelter).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    case_search_id = st.number_input("Enter Case ID to inspect referrals:", min_value=1, step=1, value=1)

    try:
        referrals = client.get_case_referrals(token, int(case_search_id))
    except APIError as e:
        st.error(f"Failed to load referrals for Case #{case_search_id}: {e.message}")
        return

    if not referrals:
        st.markdown(
            f"""
            <div class="ms-empty-state">
                <div class="ms-empty-icon">🤝</div>
                <h4 style="color: #0f4c5c; margin-bottom: 4px;">No Referrals on Record</h4>
                <p style="margin: 0; font-size: 0.9rem;">No referrals have been requested for Case #{case_search_id} yet.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for ref in referrals:
        rid = ref.get("id")
        cur_status = ref.get("status", "created")
        prio = ref.get("priority", "routine")

        status_badge = render_badge(cur_status)
        prio_badge = render_badge(prio, text=f"{prio.upper()} PRIORITY")

        with st.container(border=True):
            r1, r2 = st.columns([3, 1])
            with r1:
                st.markdown(f"#### Referral #{rid} • {ref.get('referral_type', '').replace('_', ' ').title()}")
                st.markdown(f"**Agency / Provider:** {ref.get('organization')}")
                st.caption(f"Reason: {ref.get('reason')}")
            with r2:
                st.markdown(f"<div style='text-align: right;'>{status_badge} {prio_badge}</div>", unsafe_allow_html=True)

            valid_next = {
                "created": ["acknowledged", "cancelled"],
                "acknowledged": ["in_progress", "cancelled"],
                "in_progress": ["completed", "cancelled"],
                "completed": [],
                "cancelled": [],
            }.get(cur_status, [])

            if valid_next:
                with st.form(f"update_ref_form_{rid}"):
                    c_sel, c_btn = st.columns([2, 1])
                    with c_sel:
                        new_st = st.selectbox("Update Status", options=valid_next, key=f"sel_st_{rid}")
                    with c_btn:
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        update_sub = st.form_submit_button("Update", type="primary")

                    if update_sub:
                        try:
                            client.update_referral_status(token, rid, new_st)
                            st.success(f"Referral #{rid} transitioned to '{new_st}'.")
                            st.rerun()
                        except APIError as err:
                            st.error(err.message)
            else:
                st.caption(f"Referral has reached terminal state: `{cur_status}`.")


# ──────────────────────────────────────────────────────────
# 4. Audit Trail
# ──────────────────────────────────────────────────────────

def _render_staff_audit(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render cryptographic compliance and audit trail."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Compliance & Audit Trail</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Immutable cryptographic activity logs ensuring full accountability and privacy compliance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        logs = client.get_audit_logs(token)
    except APIError as e:
        st.error(f"Failed to load audit logs: {e.message}")
        return

    if not logs:
        st.info("No audit logs recorded for your account.")
        return

    st.write(f"Showing **{min(len(logs), 25)}** recent log entries:")

    for log in logs[:25]:
        ts = log.get("created_at", "")[:19].replace("T", " ")
        action = log.get("action", "")
        res_type = log.get("resource_type", "")
        res_id = log.get("resource_id", "")
        details = log.get("details", "")

        with st.container(border=True):
            st.markdown(f"**`{action.upper()}`** on `{res_type}` #{res_id}")
            st.caption(f"Timestamp: {ts} • Details: {details}")

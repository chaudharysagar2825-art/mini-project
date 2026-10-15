"""Redesigned clinical decision-support and caseworker triage portal for Manas Setu."""

from typing import Any
import pandas as pd
import streamlit as st
from api_client import APIError, ManasSetuClient
from theme import render_badge, render_helpline_banner


def render_staff_portal(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
    active_nav: str,
) -> None:
    """Main staff portal router dispatching to dedicated triage views."""

    if active_nav == "Overview":
        _render_staff_overview(client, token, user)
    elif active_nav == "Longitudinal Monitoring":
        _render_staff_monitoring(client, token, user)
    elif active_nav == "Alert Queue":
        _render_staff_alerts(client, token, user)
    elif active_nav == "Case Referrals":
        _render_staff_referrals(client, token, user)
    elif active_nav == "Multi-Channel Comms":
        _render_staff_comms(client, token, user)
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
                Role: <strong>{role_name}</strong> • Human-supervised triage, clinical decision support, and longitudinal monitoring.
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
                <div class="ms-stat-desc">Cases registered under monitoring</div>
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
                <div class="ms-stat-label">Active Referrals</div>
                <div class="ms-stat-value">{summary.get('active_referrals', 0)}</div>
                <div class="ms-stat-desc">Multi-agency coordination</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Operational Quick Actions
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>📈 Longitudinal Monitoring</h4>", unsafe_allow_html=True)
            st.markdown("Track case-specific distress score progression, historical risk trends, and AI explainability factors.")
            if st.button("Inspect Case Trends →", type="primary", use_container_width=True):
                st.session_state.current_nav = "Longitudinal Monitoring"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>🚨 Distress Alert Triage</h4>", unsafe_allow_html=True)
            st.markdown("Review deterministic risk assessments, crisis indicators, and assign caseworkers to urgent cases.")
            if st.button("Open Alert Queue →", type="secondary", use_container_width=True):
                st.session_state.current_nav = "Alert Queue"
                st.rerun()

    with c3:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>📡 Multi-Channel Comms</h4>", unsafe_allow_html=True)
            st.markdown("Manage SMS and IVR voice check-in channels, dispatch reminders, and monitor integration telemetry.")
            if st.button("Manage Channels →", type="secondary", use_container_width=True):
                st.session_state.current_nav = "Multi-Channel Comms"
                st.rerun()


# ──────────────────────────────────────────────────────────
# 2. Longitudinal Monitoring & Trends
# ──────────────────────────────────────────────────────────

def _render_staff_monitoring(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render case-specific longitudinal distress monitoring, trends, and history."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Longitudinal Distress Monitoring</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Clinical decision support: Inspect persisted distress scores (0-10 scale), risk categories, and trajectory over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Case Selection
    cases = []
    try:
        cases = client.list_all_cases(token)
    except APIError:
        pass

    selected_case_id = 1
    if cases:
        case_options = {c["id"]: f"Case #{c['id']} — {c['case_code']} (Status: {c.get('status', 'active')})" for c in cases}
        selected_case_id = st.selectbox(
            "Select Victim Case to Inspect:",
            options=list(case_options.keys()),
            format_func=lambda x: case_options[x],
            key="staff_case_inspect_sel",
        )
    else:
        selected_case_id = st.number_input("Enter Case ID to Inspect:", min_value=1, step=1, value=1)

    # 2. Fetch Longitudinal Trends from API
    try:
        trends = client.get_case_trends(token, int(selected_case_id))
    except APIError as e:
        st.error(f"Failed to load case trends: {e.message}")
        return

    history = trends.get("history", [])

    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Total Check-Ins</div>
                <div class="ms-stat-value">{trends.get('total_checkins', len(history))}</div>
                <div class="ms-stat-desc">Self-reports recorded</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        cat = trends.get("current_risk_category", "low")
        cat_badge = render_badge(cat, text=f"{cat.upper()} RISK")
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Current Risk Category</div>
                <div style="margin: 8px 0;">{cat_badge}</div>
                <div class="ms-stat-desc">Screening classification</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        direction = trends.get("overall_direction", "unknown").capitalize()
        dir_icon = "📈" if direction == "Worsening" else ("📉" if direction == "Improving" else "⚖️")
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Overall Trajectory</div>
                <div class="ms-stat-value" style="font-size: 1.3rem;">{dir_icon} {direction}</div>
                <div class="ms-stat-desc">Baseline vs recent check-ins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        avg = trends.get("average_score", 0.0)
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Avg Distress Score</div>
                <div class="ms-stat-value">{avg} <span style="font-size: 0.9rem; color: #64748b;">/ 10</span></div>
                <div class="ms-stat-desc">0-10 standardized scale</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if not history:
        st.info(f"Case #{selected_case_id} has no check-ins recorded yet.")
        return

    # 3. Longitudinal Distress Line Chart
    if len(history) >= 2:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>📈 Longitudinal Distress Score Progression (0-10 Scale)</h4>", unsafe_allow_html=True)
            chart_df = pd.DataFrame(
                {"Distress Score (0-10)": [h["score"] for h in history]},
                index=[h["timestamp"][:16].replace("T", " ") for h in history],
            )
            st.line_chart(chart_df, height=220)

    # 4. Detailed Chronological Assessments Table/Cards
    st.markdown("#### Chronological Check-Ins & Assessment Records")
    try:
        assessments = client.get_case_assessments(token, int(selected_case_id))
    except APIError:
        assessments = []

    asm_by_checkin = {a.get("checkin_id"): a for a in assessments}

    for item in reversed(history):
        cid = item.get("checkin_id")
        date_str = item.get("timestamp", "")[:16].replace("T", " ")
        score = item.get("score", 0)
        risk_cat = item.get("risk_category", "low")
        dir_val = item.get("direction", "unknown")
        reason = item.get("reason", "Routine indicators")
        asm = asm_by_checkin.get(cid)
        model_ver = asm.get("model_version", "rule-v1") if asm else "rule-v1"

        cat_badge = render_badge(risk_cat, text=f"{risk_cat.upper()} RISK")
        dir_badge = render_badge(dir_val, text=f"{dir_val.upper()}")

        with st.container(border=True):
            r1, r2 = st.columns([3, 1])
            with r1:
                st.markdown(f"**Check-In #{cid}** • Submitted: **{date_str}**")
                st.markdown(f"**Distress Score:** `{score} / 10` • **Direction:** `{dir_val.capitalize()}` • **Model:** `{model_ver}`")
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; border-left: 3px solid #0f4c5c; padding: 8px 12px; border-radius: 4px; margin-top: 6px; font-size: 0.88rem; color: #334155;">
                        <strong>Decision Support Rationale:</strong> {reason}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with r2:
                st.markdown(f"<div style='text-align: right;'>{cat_badge} {dir_badge}</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# 3. Alert Queue
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
# 4. Case Referrals Management
# ──────────────────────────────────────────────────────────

def _render_staff_referrals(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render case referrals review, creation, and status management."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Case Referrals Coordination</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Coordinate and track multi-agency support services (Mental Health, DLSA Legal, Protection, Shelter, Financial).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Staff Create New Referral Expander
    with st.expander("➕ Create New Referral for a Case"):
        with st.form("staff_new_referral_form"):
            c_id_in = st.number_input("Target Case ID", min_value=1, step=1, value=1)
            ref_cat = st.selectbox(
                "Referral Category",
                options=["mental_health", "protection", "legal", "financial", "rehab", "welfare"],
                format_func=lambda x: {
                    "mental_health": "Mental Health & Counselling",
                    "protection": "Protection & Safe Housing",
                    "legal": "Legal Assistance & DLSA",
                    "financial": "Financial Aid & Compensation",
                    "rehab": "Medical & Physical Rehabilitation",
                    "welfare": "Welfare & Social Support",
                }[x],
            )
            ref_org = st.text_input("Designated Provider / Agency", placeholder="e.g. District Hospital Psychiatric Dept / DLSA Legal Aid Clinic")
            ref_reason = st.text_area("Referral Justification & Needs", placeholder="Clinical justification and requested service parameters...", height=70)
            ref_prio = st.selectbox("Priority", options=["routine", "follow_up", "urgent"])
            staff_sub_ref = st.form_submit_button("Create Referral Record", type="primary")

        if staff_sub_ref:
            if not ref_org.strip() or not ref_reason.strip():
                st.error("Provider organization and justification reason are required.")
            else:
                try:
                    new_ref = client.create_referral(
                        token=token,
                        case_id=int(c_id_in),
                        referral_type=ref_cat,
                        organization=ref_org.strip(),
                        reason=ref_reason.strip(),
                        priority=ref_prio,
                    )
                    st.success(f"Referral #{new_ref['id']} created successfully for Case #{c_id_in}.")
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to create referral: {e.message}")

    st.markdown("---")
    case_search_id = st.number_input("Filter by Case ID to inspect active referrals:", min_value=1, step=1, value=1)

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
                <p style="margin: 0; font-size: 0.9rem;">No referrals have been created for Case #{case_search_id} yet.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.write(f"Showing **{len(referrals)}** referral(s) for Case #{case_search_id}:")

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
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; border-left: 3px solid #0f4c5c; padding: 6px 10px; border-radius: 4px; margin: 4px 0; font-size: 0.85rem; color: #334155;">
                        <strong>Needs / History:</strong> {ref.get('reason')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
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
                    c_sel, c_note, c_btn = st.columns([1.5, 2, 1])
                    with c_sel:
                        new_st = st.selectbox("Update Status", options=valid_next, key=f"sel_st_{rid}")
                    with c_note:
                        f_note = st.text_input("Follow-Up Notes / Outcome", placeholder="Action taken or provider update...", key=f"input_note_{rid}")
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
# 5. Multi-Channel Communication
# ──────────────────────────────────────────────────────────

def _render_staff_comms(
    client: ManasSetuClient,
    token: str,
    user: dict[str, Any],
) -> None:
    """Render multi-channel communication dashboard, reminders, and simulation tester."""

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="color: #0f4c5c; margin-bottom: 4px;">Multi-Channel Communication Hub</h2>
            <p style="color: #475569; font-size: 0.9rem; margin: 0;">
                Unified intake and notification status across SMS, Voice/IVR, and Web channels.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Integration Status
    try:
        provider_status = client.get_communication_status(token)
    except APIError:
        provider_status = {"sms": {"provider": "MockSMSProvider", "is_mock": True}, "voice_ivr": {"provider": "MockIVRProvider", "is_mock": True}}

    s1, s2 = st.columns(2)
    with s1:
        sms_info = provider_status.get("sms", {})
        is_mock_sms = sms_info.get("is_mock", True)
        sms_badge = render_badge("routine", text="MOCK DEV MODE") if is_mock_sms else render_badge("routine", text="LIVE GATEWAY")
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">SMS Gateway</div>
                <div style="margin: 6px 0;">{sms_badge}</div>
                <div class="ms-stat-desc">Provider: <code>{sms_info.get('provider')}</code> • Neutral Notifications Enforced</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        ivr_info = provider_status.get("voice_ivr", {})
        ivr_badge = render_badge("routine", text="MOCK IVR ACTIVE")
        st.markdown(
            f"""
            <div class="ms-stat-card">
                <div class="ms-stat-label">Voice / IVR Telephony</div>
                <div style="margin: 6px 0;">{ivr_badge}</div>
                <div class="ms-stat-desc">Provider: <code>{ivr_info.get('provider')}</code> • DTMF & Speech Parsing Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Dispatch Safe SMS Reminder
    c_rem, c_sim = st.columns(2, gap="medium")

    with c_rem:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>📲 Dispatch Routine Wellness SMS</h4>", unsafe_allow_html=True)
            st.caption("Dispatches a privacy-preserving check-in reminder SMS to a verified safe contact. Sensitive case keywords are strictly omitted.")
            with st.form("dispatch_sms_reminder_form"):
                rem_case_id = st.number_input("Victim Case ID", min_value=1, step=1, value=1)
                rem_phone = st.text_input("Destination Phone Number", placeholder="e.g. +91 9876543210")
                sub_rem = st.form_submit_button("Send Safe Reminder", type="primary")

            if sub_rem:
                if not rem_phone.strip():
                    st.error("Phone number is required.")
                else:
                    try:
                        res = client.trigger_sms_reminder(token, int(rem_case_id), rem_phone.strip())
                        st.success(f"Reminder dispatched! Status: `{res.get('status')}` (Provider: {res.get('provider')})")
                    except APIError as e:
                        st.error(f"Dispatch failed: {e.message}")

    with c_sim:
        with st.container(border=True):
            st.markdown("<h4 style='color: #0f4c5c; margin-top: 0;'>🧪 Interactive Inbound SMS Simulator</h4>", unsafe_allow_html=True)
            st.caption("Simulates an incoming SMS from a registered safe contact to demonstrate end-to-end NLP distress detection, assessment creation, and triage alerts.")
            with st.form("simulate_sms_inbound_form"):
                sim_phone = st.text_input("Sender Phone", value="+91 9876543210")
                sim_msg = st.text_area(
                    "Simulated SMS Text",
                    value="I feel scared and alone, please help me reach my caseworker",
                    height=70,
                )
                sub_sim = st.form_submit_button("Simulate Inbound SMS Intake", type="primary")

            if sub_sim:
                try:
                    res = client.send_inbound_sms(sim_phone.strip(), sim_msg.strip())
                    st.info(f"Ingestion result: Status `{res.get('status')}`")
                    if res.get("checkin_id"):
                        st.success(f"Generated Check-In #{res['checkin_id']} for Case #{res.get('case_id')}. Distress pipeline triggered.")
                    elif res.get("message"):
                        st.warning(f"Intake response: {res.get('message')}")
                except APIError as e:
                    st.error(f"Simulation failed: {e.message}")


# ──────────────────────────────────────────────────────────
# 6. Audit Trail
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
